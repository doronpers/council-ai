"""Consultation commands."""

import re
import sys
from pathlib import Path

import click
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils import (
    DEFAULT_PROVIDER,
    assemble_council,
    console,
    parse_bracket_notation,
    require_api_key,
)


@click.command()
@click.argument("query")
@click.option("--preset", help="Use a saved preset configuration")
@click.option("--domain", "-d", help="Domain preset to use")
@click.option("--members", "-m", multiple=True, help="Specific personas to consult")
@click.option("--provider", "-p", help="LLM provider (anthropic, openai)")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key for provider")
@click.option("--context", "-ctx", help="Additional context for the query")
@click.option(
    "--mode",
    type=click.Choice(["individual", "sequential", "synthesis", "debate", "vote"]),
    help="Consultation mode",
)
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--session", "-s", "session_id", help="Resume an existing session ID")
@click.option("--no-recall", is_flag=True, help="Disable automatic context recall")
@click.option("--quick", is_flag=True, help="Quick mode: 2-3 personas, 500 tokens, no synthesis")
@click.option("--domains", help="Comma-separated list of domains for cross-domain consultation")
@click.pass_context
@require_api_key
def consult(
    ctx,
    query,
    preset,
    domain,
    members,
    provider,
    api_key,
    context,
    mode,
    output,
    output_json,
    session_id,
    no_recall,
    quick,
    domains,
):
    r"""
    Consult the council on a query.

    \b
    Examples:
      council consult "Should we refactor this module?"
      council consult --domain startup "Is this the right time to raise?"
      council consult --members DR --members DK "Review this design"
      council consult "[MD, JT] What do you think about this?"
      council consult --preset my-team "What do you think?"
    """
    config_manager = ctx.obj["config_manager"]

    # Check for bracket notation in query
    bracket_members = parse_bracket_notation(query)
    if bracket_members:
        # If bracket notation found in query, use those members
        if members:
            console.print(
                "[yellow]Warning:[/yellow] Both bracket notation in query and --members specified. "
                "Using bracket notation from query."
            )
        members = tuple(bracket_members)
        # Remove bracket notation from query
        query = re.sub(r"\[[^\]]+\]\s*", "", query).strip()

    # Load preset if specified
    if preset:
        if preset not in config_manager.config.presets:
            console.print(f"[red]Error:[/red] Preset '{preset}' not found")
            console.print("[dim]Use 'council config preset-list' to see available presets[/dim]")
            sys.exit(1)

        preset_config = config_manager.config.presets[preset]
        # Apply preset values if not overridden by CLI options
        if not domain:
            domain = preset_config.get("domain", "general")
        if not members and "members" in preset_config:
            members = preset_config["members"]
        if not mode:
            mode = preset_config.get("mode", "synthesis")

    # Handle cross-domain consultation
    if domains:
        # Parse comma-separated domains
        domain_list = [d.strip() for d in domains.split(",")]
        from ...domains import get_domain

        # Collect personas from all domains (deduplicate)
        all_personas = []
        seen_personas = set()
        for dom_id in domain_list:
            try:
                dom = get_domain(dom_id)
                for persona_id in dom.default_personas:
                    if persona_id not in seen_personas:
                        all_personas.append(persona_id)
                        seen_personas.add(persona_id)
            except ValueError:
                console.print(f"[yellow]Warning:[/yellow] Domain '{dom_id}' not found, skipping")

        # Use collected personas as members
        if not members:
            members = tuple(all_personas)
        domain = None  # Clear domain since we're using explicit members

    # Apply defaults if still not set
    if not domain:
        domain = config_manager.get("default_domain", "general")
    if not mode:
        mode = config_manager.get("default_mode", "synthesis")

    # Handle quick mode
    if quick:
        # Quick mode: limit personas, reduce tokens, skip synthesis
        if not members and domain:
            # Limit to first 2-3 personas from domain
            from ...domains import get_domain

            try:
                dom = get_domain(domain)
                members = tuple(dom.default_personas[:3])  # First 3 personas
            except ValueError:
                pass
        elif members:
            # Limit to first 2-3 specified members
            members = tuple(list(members)[:3])

        # Skip synthesis in quick mode
        if mode == "synthesis":
            mode = "individual"

        # Set max tokens to 500 (will be applied via config override)

    # Create council
    provider = provider or config_manager.get("api.provider", DEFAULT_PROVIDER)
    model = config_manager.get("api.model")
    base_url = config_manager.get("api.base_url")
    from ...core.council import ConsultationMode

    mode_enum = ConsultationMode(mode)

    # Apply quick mode config overrides
    if quick:
        from ...core.council import CouncilConfig

        # Create a config override for quick mode
        quick_config = CouncilConfig(max_tokens_per_response=500)
    else:
        quick_config = None

    # Only show progress spinner if not JSON output (for clean JSON output)
    if output_json:
        # Assemble council
        council = assemble_council(domain, members, api_key, provider, model, base_url)
        if quick_config:
            council.config = quick_config

        try:
            from ...core.history import ConsultationHistory

            council._history = ConsultationHistory()
            result = council.consult(
                query,
                context=context,
                mode=mode_enum,
                session_id=session_id,
                auto_recall=not no_recall,
            )
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    else:
        # Show progress with spinner for interactive mode
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Assembling council...", total=None)

            council = assemble_council(domain, members, api_key, provider, model, base_url)
            if quick_config:
                council.config = quick_config
            progress.update(progress.task_ids[0], description="Consulting council...")

            try:
                # Use streaming to show thinking process
                import asyncio

                # Track thinking and responses per persona
                persona_thinking = {}
                persona_responses = {}
                persona_names = {}
                result = None

                async def stream_and_display():
                    nonlocal result
                    console.print()  # Add spacing after progress
                    async for event in council.consult_stream(
                        query, context=context, mode=mode_enum
                    ):
                        event_type = event.get("type")
                        persona_id = event.get("persona_id")
                        persona_name = event.get("persona_name", persona_id)
                        persona_emoji = event.get("persona_emoji", "")

                        if persona_id:
                            if persona_id not in persona_names:
                                persona_names[persona_id] = f"{persona_emoji} {persona_name}"

                        if event_type == "thinking_chunk":
                            content = event.get("content", "")
                            accumulated = event.get("accumulated_thinking", "")
                            if persona_id:
                                persona_thinking[persona_id] = accumulated
                                # Display thinking in real-time
                                name = persona_names.get(persona_id, persona_id)
                                # Only show if this is a new chunk (not just updating)
                                if content:
                                    console.print(f"[dim cyan]💭 {name} (thinking...)[/dim cyan]")
                                    console.print(f"[dim]{content}[/dim]")
                        elif event_type == "response_chunk":
                            content = event.get("content", "")
                            accumulated = event.get("accumulated_response", "")
                            if persona_id:
                                # Clear thinking display when response starts
                                if persona_id in persona_thinking:
                                    persona_thinking[persona_id] = ""
                                persona_responses[persona_id] = accumulated
                                # Display response chunks
                                name = persona_names.get(persona_id, persona_id)
                                if content:
                                    console.print(f"[bold]{name}:[/bold] {content}", end="")
                        elif event_type == "response_complete":
                            if persona_id:
                                # Clear thinking when response is complete
                                if persona_id in persona_thinking:
                                    del persona_thinking[persona_id]
                                # Add newline after response
                                console.print()  # Newline after response
                        elif event_type == "complete":
                            result = event.get("result")
                            break

                # Run the async stream and display
                asyncio.run(stream_and_display())

                # Fallback to non-streaming if result is None
                if not result:
                    result = council.consult(query, context=context, mode=mode_enum)
            except Exception as e:
                # Fallback to non-streaming on error
                console.print(f"[yellow]Streaming error: {e}[/yellow]")
                console.print("[dim]Falling back to non-streaming mode...[/dim]")
                try:
                    result = council.consult(query, context=context, mode=mode_enum)
                except Exception as e2:
                    console.print(f"[red]Error:[/red] {e2}")
                    sys.exit(1)

    # Record consultation in user memory for personalization
    try:
        from ...core.user_memory import get_user_memory

        user_memory = get_user_memory()
        user_memory.record_consultation(result)
        if result.session_id:
            user_memory.record_session(result.session_id, domain)
    except Exception as e:
        # User memory is optional - don't fail if it doesn't work
        import logging

        logging.getLogger(__name__).debug(f"Failed to record in user memory: {e}")

    # Show personalized greeting and insights
    if not output_json:
        try:
            from ...core.user_memory import get_user_memory

            user_memory = get_user_memory()
            greeting = user_memory.get_personalized_greeting()
            console.print(f"[dim]{greeting}[/dim]\n")

            insights = user_memory.get_personalized_insights()
            if insights:
                console.print("[bold cyan]Insights from your history:[/bold cyan]")
                for insight in insights[:2]:
                    console.print(f"  • {insight}")
                console.print()
        except Exception:
            pass  # Personalization is optional

    # Output
    if output_json:
        import json

        output_text = json.dumps(result.to_dict(), indent=2)
    else:
        output_text = result.to_markdown()

    if output:
        Path(output).write_text(output_text, encoding="utf-8")
        console.print(f"[green]✓[/green] Output saved to {output}")
    else:
        console.print()
        console.print(Markdown(output_text))

        # Offer to save if not already saved
        if not output_json:
            try:
                from rich.prompt import Confirm

                if Confirm.ask(
                    "\n[cyan]Save consultation results to a file?[/cyan]", default=False
                ):
                    from rich.prompt import Prompt

                    default_path = f"consultation_{result.id[:8]}.md"
                    save_path = Prompt.ask("Output file path", default=default_path)
                    try:
                        Path(save_path).write_text(output_text, encoding="utf-8")
                        console.print(f"[green]✓ Results saved to {save_path}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error saving results: {e}[/red]")
            except ImportError:
                pass  # rich.prompt not available

    # Display cost if enabled
    if result and result.id:
        from ...core.cost_tracker import get_cost_tracker

        cost_tracker = get_cost_tracker()
        total_cost = cost_tracker.get_total_cost()

        if total_cost > 0:
            show_cost = config_manager.get("display.show_cost", False)
            if show_cost:
                persona_count = len(result.responses)
                mode_str = result.mode
                console.print(
                    f"\n[dim]Cost: ${total_cost:.2f} ({persona_count} personas, {mode_str})[/dim]"
                )


@click.command("q")
@click.argument("query")
@click.option("--preset", help="Use a saved preset configuration")
@click.option("--domain", "-d", help="Domain preset to use")
@click.option("--members", "-m", multiple=True, help="Specific personas to consult")
@click.option("--provider", "-p", help="LLM provider (anthropic, openai)")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key for provider")
@click.option("--context", "-ctx", help="Additional context for the query")
@click.option(
    "--mode",
    type=click.Choice(["individual", "sequential", "synthesis", "debate", "vote"]),
    help="Consultation mode",
)
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--session", "-s", "session_id", help="Resume an existing session ID")
@click.option("--no-recall", is_flag=True, help="Disable automatic context recall")
@click.option("--quick", is_flag=True, help="Quick mode: 2-3 personas, 500 tokens, no synthesis")
@click.pass_context
@require_api_key
def q(
    ctx,
    query,
    preset,
    domain,
    members,
    provider,
    api_key,
    context,
    mode,
    output,
    output_json,
    session_id,
    no_recall,
    quick,
):
    """
    Quick consultation shorthand (alias for 'council consult').

    Examples:
      council q "Should we refactor this module?"
      council q --quick "What's the risk here?"
      council q -d sonotheia "Review this SAR narrative"
    """
    # Delegate to consult function
    ctx.invoke(
        consult,
        query=query,
        preset=preset,
        domain=domain,
        members=members,
        provider=provider,
        api_key=api_key,
        context=context,
        mode=mode,
        output=output,
        output_json=output_json,
        session_id=session_id,
        no_recall=no_recall,
        quick=quick,
    )
