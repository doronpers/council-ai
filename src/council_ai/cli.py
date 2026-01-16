"""
Council AI - Command Line Interface

A comprehensive CLI for interacting with the Council AI system.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from . import Council, get_domain, get_persona, list_domains, list_personas
from .core.config import ConfigManager, get_api_key
from .core.history import ConsultationHistory
from .core.persona import Persona, PersonaCategory, PersonaManager
from .core.session import ConsultationResult
from .providers import list_providers

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# Main CLI Group
# ═══════════════════════════════════════════════════════════════════════════════


@click.group()
@click.version_option(version="1.0.0", prog_name="council-ai")
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.pass_context
def main(ctx, config):
    """
    🏛️ Council AI - Intelligent Advisory Council System

    Get advice from a council of AI-powered personas with diverse
    perspectives and expertise.

    \b
    First Time Setup:
      council init              # Guided setup wizard
      council quickstart        # Explore features (no API key needed)

    \b
    Quick Start:
      council consult "Should I take this job offer?"
      council consult --domain business "Review our Q1 strategy"
      council interactive

    \b
    Manage Personas:
      council persona list
      council persona show rams
      council persona create

    \b
    Configuration & Presets:
      council config set api.provider anthropic
      council config preset-save my-team --domain coding
      council consult --preset my-team "Review this code"
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["config_manager"] = ConfigManager(config)


# ═══════════════════════════════════════════════════════════════════════════════
# Init Command (Setup Wizard)
# ═══════════════════════════════════════════════════════════════════════════════


@main.command()
@click.pass_context
def init(ctx):
    """
    Initialize Council AI with a setup wizard.

    Guides you through first-time setup including API keys and preferences.
    Automatically detects all available API keys and suggests the best provider.
    """
    from .core.config import get_available_providers, get_best_available_provider
    from .core.diagnostics import diagnose_api_keys

    config_manager = ctx.obj["config_manager"]

    console.print(
        Panel(
            "[bold]🏛️ Welcome to Council AI![/bold]\n\n"
            "This wizard will help you set up Council AI.\n"
            "You can change these settings later with 'council config'.",
            title="Setup Wizard",
            border_style="blue",
        )
    )

    # Step 0: Detect all available API keys
    console.print("\n[bold]Step 0: Detecting available API keys...[/bold]")
    diagnose_api_keys()  # Run diagnostics (results used by get_available_providers)
    available_providers = get_available_providers()

    # Show what we found
    found_keys = []
    for provider_name, api_key in available_providers:
        if api_key:
            found_keys.append(provider_name)
            console.print(f"[green]✓[/green] Found {provider_name.upper()} API key")

    if not found_keys:
        console.print("[yellow]⚠[/yellow] No API keys detected in environment variables")
        console.print("[dim]We'll help you configure one in the next step[/dim]")
    else:
        console.print(
            f"\n[bold]Found {len(found_keys)} available provider(s):[/bold] {', '.join(found_keys)}"
        )
        best = get_best_available_provider()
        if best:
            console.print(f"[cyan]💡 Recommended:[/cyan] {best[0]} (best supported provider)")

    # Step 1: Choose provider
    console.print("\n[bold]Step 1: Choose your LLM provider[/bold]")
    all_providers = list_providers()
    console.print(f"Supported providers: {', '.join(all_providers)}")

    # Build choices with availability indicators
    default_provider = config_manager.get("api.provider", "anthropic")
    provider_availability = {}

    for provider_name in all_providers:
        has_key = any(p == provider_name and k for p, k in available_providers)
        provider_availability[provider_name] = has_key
        if has_key:
            # Use first available as default if no config
            if not config_manager.get("api.provider") and default_provider == "anthropic":
                default_provider = provider_name

    # If we have a best provider, use it as default
    best = get_best_available_provider()
    if best and best[0] in all_providers:
        default_provider = best[0]

    console.print("\nAvailable options:")
    for provider_name in all_providers:
        has_key = provider_availability[provider_name]
        if has_key:
            console.print(f"  • {provider_name} [green](API key available)[/green]")
        else:
            console.print(f"  • {provider_name} [dim](no API key)[/dim]")

    provider = Prompt.ask(
        "\nWhich provider would you like to use?",
        choices=all_providers,
        default=default_provider,
    )
    config_manager.set("api.provider", provider)

    # Step 2: API Key
    console.print("\n[bold]Step 2: Configure API key[/bold]")
    existing_key = get_api_key(provider)

    # Also check for vercel/generic if using openai
    if provider == "openai":
        vercel_key = get_api_key("vercel")
        if vercel_key:
            existing_key = vercel_key
            console.print("[cyan]ℹ[/cyan] Using AI_GATEWAY_API_KEY (Vercel AI Gateway)")

    if existing_key and "your-" not in existing_key.lower() and "here" not in existing_key.lower():
        console.print(f"[green]✓[/green] Found existing {provider.upper()} API key")
        if not Confirm.ask("Do you want to update it?", default=False):
            existing_key = None  # Skip update
    else:
        existing_key = None

    if not existing_key:
        console.print("\n[dim]You can get an API key from:[/dim]")
        if provider == "anthropic":
            console.print("  https://console.anthropic.com/")
        elif provider == "openai":
            console.print("  https://platform.openai.com/api-keys")
        elif provider == "gemini":
            console.print("  https://ai.google.dev/")

        console.print(
            f"\n[yellow]Note:[/yellow] You can also set {provider.upper()}_API_KEY in your environment"
        )
        if provider == "openai":
            console.print(
                "[dim]Or use AI_GATEWAY_API_KEY for Vercel AI Gateway (OpenAI-compatible)[/dim]"
            )

        if Confirm.ask("Do you have an API key to configure now?", default=True):
            api_key = Prompt.ask(f"{provider.capitalize()} API key", password=True)
            if api_key:
                config_manager.set("api.api_key", api_key)
                console.print("[green]✓[/green] API key saved to config")
        else:
            # Show fallback information
            if found_keys:
                console.print(
                    f"\n[cyan]ℹ[/cyan] You have {len(found_keys)} other provider(s) available: {', '.join(found_keys)}"
                )
                console.print(
                    "[dim]Council AI will automatically use these as fallbacks if needed[/dim]"
                )

    # Step 3: Default domain
    console.print("\n[bold]Step 3: Choose default domain[/bold]")
    domains = list_domains()
    console.print("\nAvailable domains:")
    for d in domains[:5]:  # Show first 5
        console.print(f"  • {d.id}: {d.name}")
    console.print(f"  ... and {len(domains) - 5} more")

    default_domain = Prompt.ask(
        "Default domain",
        default=config_manager.get("default_domain", "general"),
    )
    config_manager.set("default_domain", default_domain)

    # Step 4: Save
    config_manager.save()

    # Build summary with fallback info
    summary_lines = [
        "[green]✓ Setup complete![/green]\n",
        f"Provider: {provider}",
        f"Default domain: {default_domain}",
        f"Config saved to: {config_manager.path}",
    ]

    # Add fallback information
    if len(found_keys) > 1 or (len(found_keys) == 1 and provider not in found_keys):
        fallback_providers = [p for p in found_keys if p != provider]
        if fallback_providers:
            summary_lines.append(
                f"\n[cyan]Fallback providers:[/cyan] {', '.join(fallback_providers)}"
            )
            summary_lines.append(
                "[dim]Council AI will automatically use these if the primary provider fails[/dim]"
            )

    summary_lines.extend(
        [
            "\n[bold]Next steps:[/bold]",
            "  • Run 'council consult \"your question\"' to get started",
            "  • Run 'council interactive' for a session",
            "  • Run 'council --help' to see all commands",
            "  • Run 'council providers --diagnose' to check API key status",
        ]
    )

    console.print(
        Panel(
            "\n".join(summary_lines),
            title="Setup Complete",
            border_style="green",
        )
    )


@main.command()
def quickstart():
    """
    Run an interactive quickstart demo (no API key required).

    Explore Council AI features and see examples without needing an API key.
    """
    import subprocess
    import sys

    quickstart_path = Path(__file__).parent.parent.parent / "examples" / "quickstart.py"

    if not quickstart_path.exists():
        # Try alternative path for installed package
        quickstart_path = Path(__file__).parent / ".." / ".." / "examples" / "quickstart.py"

    if quickstart_path.exists():
        try:
            subprocess.run([sys.executable, str(quickstart_path)], check=True)
        except subprocess.CalledProcessError:
            console.print("[red]Error:[/red] Failed to run quickstart demo")
            sys.exit(1)
    else:
        console.print(
            "[yellow]Quickstart demo not found.[/yellow]\n\n"
            "You can view personas and domains with:\n"
            "  council persona list\n"
            "  council domain list\n"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Consult Command
# ═══════════════════════════════════════════════════════════════════════════════


@main.command()
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
@click.pass_context
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
):
    """
    Consult the council on a query.

    \b
    Examples:
      council consult "Should we refactor this module?"
      council consult --domain startup "Is this the right time to raise?"
      council consult --members rams --members kahneman "Review this design"
      council consult --preset my-team "What do you think?"
    """
    config_manager = ctx.obj["config_manager"]

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

    # Apply defaults if still not set
    if not domain:
        domain = config_manager.get("default_domain", "general")
    if not mode:
        mode = config_manager.get("default_mode", "synthesis")

    # Get API key
    requested_provider = provider or config_manager.get("api.provider", "anthropic")

    # Check if api_key from CLI/env is a placeholder - if so, ignore it and try get_api_key()
    is_placeholder = api_key and ("your-" in api_key.lower() or "here" in api_key.lower())
    if is_placeholder:
        api_key = None  # Ignore placeholder, force get_api_key() to run

    api_key = api_key or get_api_key(requested_provider)
    if not api_key:
        console.print("[red]Error:[/red] No API key provided.")
        console.print(
            "Set via --api-key, COUNCIL_API_KEY env var, or 'council config set api.api_key'"
        )
        sys.exit(1)
    if "your-" in api_key.lower() or "here" in api_key.lower():
        console.print("[red]Error:[/red] API key appears to be a placeholder value.")
        console.print(
            "Please update your .env file with your actual API key (not the example value)."
        )
        console.print("Run 'council providers --diagnose' for help.")
        sys.exit(1)

    # Create council
    provider = provider or config_manager.get("api.provider", "anthropic")
    model = config_manager.get("api.model")
    base_url = config_manager.get("api.base_url")
    from .core.council import ConsultationMode

    mode_enum = ConsultationMode(mode)

    # Only show progress spinner if not JSON output (for clean JSON output)
    if output_json:
        # Assemble council
        if members:
            council = Council(api_key=api_key, provider=provider, model=model, base_url=base_url)
            for member_id in members:
                try:
                    council.add_member(member_id)
                except ValueError as e:
                    console.print(f"[yellow]Warning:[/yellow] {e}")
        else:
            council = Council.for_domain(
                domain,
                api_key=api_key,
                provider=provider,
                model=model,
                base_url=base_url,
            )

        try:
            from .core.history import ConsultationHistory

            council._history = ConsultationHistory()
            result = council.consult(
                query,
                context=context,
                mode=mode_enum,
                session_id=session_id,
                auto_recall=not no_recall,
            )
        except Exception as e:
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

            if members:
                council = Council(
                    api_key=api_key, provider=provider, model=model, base_url=base_url
                )
                for member_id in members:
                    try:
                        council.add_member(member_id)
                    except ValueError as e:
                        console.print(f"[yellow]Warning:[/yellow] {e}")
            else:
                council = Council.for_domain(
                    domain,
                    api_key=api_key,
                    provider=provider,
                    model=model,
                    base_url=base_url,
                )

            progress.update(progress.task_ids[0], description="Consulting council...")

            try:
                result = council.consult(query, context=context, mode=mode_enum)
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                sys.exit(1)

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


# ═══════════════════════════════════════════════════════════════════════════════
# Interactive Mode
# ═══════════════════════════════════════════════════════════════════════════════


@main.command()
@click.option("--domain", "-d", default="general", help="Domain preset to use")
@click.option("--provider", "-p", help="LLM provider")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key")
@click.option("--session", "-s", "session_id", help="Resume an existing session ID")
@click.pass_context
def interactive(ctx, domain, provider, api_key, session_id):
    """
    Start an interactive council session.

    Have a multi-turn conversation with your council.
    """
    config_manager = ctx.obj["config_manager"]

    # Check if api_key from CLI/env is a placeholder - if so, ignore it and try get_api_key()
    is_placeholder = api_key and ("your-" in api_key.lower() or "here" in api_key.lower())
    if is_placeholder:
        api_key = None  # Ignore placeholder, force get_api_key() to run

    api_key = api_key or get_api_key(provider or config_manager.get("api.provider", "anthropic"))
    if not api_key:
        console.print("[red]Error:[/red] No API key provided.")
        sys.exit(1)
    if "your-" in api_key.lower() or "here" in api_key.lower():
        console.print("[red]Error:[/red] API key appears to be a placeholder value.")
        console.print(
            "Please update your .env file with your actual API key (not the example value)."
        )
        console.print("Run 'council providers --diagnose' for help.")
        sys.exit(1)

    provider = provider or config_manager.get("api.provider", "anthropic")
    model = config_manager.get("api.model")
    base_url = config_manager.get("api.base_url")
    council = Council.for_domain(
        domain,
        api_key=api_key,
        provider=provider,
        model=model,
        base_url=base_url,
    )

    # Enable history
    from .core.history import ConsultationHistory

    council._history = ConsultationHistory()

    # If resuming, load session metadata (not strictly needed as consult() handles it,
    # but good for display)
    if session_id:
        existing = council._history.load_session(session_id)
        if existing:
            domain = existing.council_name.lower()

    console.print(
        Panel(
            f"[bold]🏛️ Council AI Interactive Session[/bold]\n\n"
            f"Domain: {domain}\n"
            f"Members: {', '.join(m.name for m in council.list_members())}\n\n"
            f"Commands:\n"
            f"  /help - Show this help message\n"
            f"  /members - List current members\n"
            f"  /add <id> - Add a member\n"
            f"  /remove <id> - Remove a member\n"
            f"  /domain <name> - Switch domain\n"
            f"  /mode <mode> - Change consultation mode\n"
            f"  /quit or /exit - Exit session\n\n"
            f"[dim]Tip: Press Ctrl+C or Ctrl+D to exit anytime[/dim]",
            title="Welcome",
            border_style="blue",
        )
    )

    while True:
        try:
            query = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            if not query.strip():
                continue

            # Handle commands
            if query.startswith("/"):
                parts = query[1:].split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None

                if cmd == "quit" or cmd == "exit":
                    console.print("[green]✓[/green] Session ended. Goodbye!")
                    break
                elif cmd == "help":
                    console.print(
                        Panel(
                            "[bold]Available Commands:[/bold]\n\n"
                            "  /help - Show this help message\n"
                            "  /members - List current members\n"
                            "  /add <id> - Add a member\n"
                            "  /remove <id> - Remove a member\n"
                            "  /domain <name> - Switch domain\n"
                            "  /mode <mode> - Change consultation mode\n"
                            "  /quit or /exit - Exit session",
                            title="Help",
                            border_style="blue",
                        )
                    )
                elif cmd == "members":
                    _show_members(council)
                elif cmd == "add" and arg:
                    try:
                        council.add_member(arg)
                        console.print(f"[green]✓[/green] Added {arg}")
                    except ValueError as e:
                        console.print(f"[red]Error:[/red] {e}")
                elif cmd == "remove" and arg:
                    council.remove_member(arg)
                    console.print(f"[green]✓[/green] Removed {arg}")
                elif cmd == "domain" and arg:
                    council = Council.for_domain(
                        arg,
                        api_key=api_key,
                        provider=provider,
                        model=model,
                        base_url=base_url,
                    )
                    console.print(f"[green]✓[/green] Switched to {arg} domain")
                elif cmd == "mode" and arg:
                    from .core.council import ConsultationMode

                    council.config.mode = ConsultationMode(arg)
                    console.print(f"[green]✓[/green] Mode set to {arg}")
                else:
                    console.print("[yellow]Unknown command[/yellow]")
                continue

            # Consult
            with console.status("Consulting council..."):
                result = council.consult(query, session_id=session_id)
                # Keep tracking session_id for next turns if we just started one
                session_id = result.session_id

            console.print()
            console.print(Markdown(result.to_markdown()))

        except (KeyboardInterrupt, EOFError):
            console.print("\n[green]✓[/green] Session ended. Goodbye!")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def _show_members(council):
    """Display current council members."""
    table = Table(title="Council Members")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Weight")
    table.add_column("Enabled")

    for m in council.list_members():
        table.add_row(
            m.id, f"{m.emoji} {m.name}", m.title, f"{m.weight:.1f}", "✓" if m.enabled else "✗"
        )

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# Persona Commands
# ═══════════════════════════════════════════════════════════════════════════════


@main.group()
def persona():
    """Manage council personas."""
    pass


@persona.command("list")
@click.option(
    "--category",
    "-c",
    type=click.Choice(["advisory", "adversarial", "custom"]),
    help="Filter by category",
)
def persona_list(category):
    """List available personas."""
    cat = PersonaCategory(category) if category else None
    personas = list_personas(cat)

    table = Table(title="Available Personas")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Focus Areas")

    for p in personas:
        table.add_row(
            p.id,
            f"{p.emoji} {p.name}",
            p.title,
            p.category.value,
            ", ".join(p.focus_areas[:3]) + ("..." if len(p.focus_areas) > 3 else ""),
        )

    console.print(table)


@persona.command("show")
@click.argument("persona_id")
def persona_show(persona_id):
    """Show details of a persona."""
    try:
        p = get_persona(persona_id)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold]{p.emoji} {p.name}[/bold]\n"
            f"[dim]{p.title}[/dim]\n\n"
            f'[bold]Core Question:[/bold]\n"{p.core_question}"\n\n'
            f'[bold]Razor:[/bold]\n"{p.razor}"\n\n'
            f"[bold]Focus Areas:[/bold]\n{', '.join(p.focus_areas)}\n\n"
            f"[bold]Traits:[/bold]\n" + "\n".join(f"• {t.name}: {t.description}" for t in p.traits),
            title=f"Persona: {p.id}",
            border_style="blue",
        )
    )


@persona.command("create")
@click.option("--interactive", "-i", is_flag=True, help="Interactive creation wizard")
@click.option("--from-file", type=click.Path(exists=True), help="Create from YAML file")
def persona_create(interactive, from_file):
    """Create a new persona."""
    if from_file:
        p = Persona.from_yaml_file(from_file)
        manager = PersonaManager()
        manager.add(p)
        manager.save_persona(p.id)
        console.print(f"[green]✓[/green] Created persona '{p.id}' from {from_file}")
        return

    if not interactive:
        console.print("Use --interactive or --from-file to create a persona")
        return

    # Interactive creation
    console.print(Panel("[bold]Create New Persona[/bold]", border_style="green"))

    id = Prompt.ask("ID (lowercase, no spaces)")
    name = Prompt.ask("Name")
    title = Prompt.ask("Title")
    emoji = Prompt.ask("Emoji", default="👤")
    core_question = Prompt.ask("Core Question (the fundamental question this persona asks)")
    razor = Prompt.ask("Razor (their decision-making principle)")

    category = Prompt.ask(
        "Category", choices=["advisory", "adversarial", "custom"], default="custom"
    )

    focus_areas = Prompt.ask("Focus Areas (comma-separated)").split(",")
    focus_areas = [f.strip() for f in focus_areas if f.strip()]

    p = Persona(
        id=id,
        name=name,
        title=title,
        emoji=emoji,
        core_question=core_question,
        razor=razor,
        category=PersonaCategory(category),
        focus_areas=focus_areas,
    )

    # Add traits
    if Confirm.ask("Add traits?"):
        while True:
            trait_name = Prompt.ask("Trait name (empty to finish)")
            if not trait_name:
                break
            trait_desc = Prompt.ask("Trait description")
            p.add_trait(trait_name, trait_desc)

    # Save
    manager = PersonaManager()
    manager.add(p)
    path = manager.save_persona(p.id)

    console.print(f"[green]✓[/green] Created persona '{p.id}'")
    console.print(f"[dim]Saved to: {path}[/dim]")


@persona.command("edit")
@click.argument("persona_id")
@click.option("--weight", type=float, help="Set weight (0.0-2.0)")
@click.option("--add-trait", nargs=2, multiple=True, help="Add trait: name description")
@click.option("--remove-trait", multiple=True, help="Remove trait by name")
def persona_edit(persona_id, weight, add_trait, remove_trait):
    """Edit an existing persona."""
    manager = PersonaManager()
    p = manager.get_or_raise(persona_id)

    if weight is not None:
        p.weight = weight
        console.print(f"[green]✓[/green] Set weight to {weight}")

    for name, desc in add_trait:
        p.add_trait(name, desc)
        console.print(f"[green]✓[/green] Added trait '{name}'")

    for name in remove_trait:
        p.remove_trait(name)
        console.print(f"[green]✓[/green] Removed trait '{name}'")

    manager.save_persona(persona_id)
    console.print("[dim]Saved changes[/dim]")


# ═══════════════════════════════════════════════════════════════════════════════
# Domain Commands
# ═══════════════════════════════════════════════════════════════════════════════


@main.group()
def domain():
    """Manage council domains."""
    pass


@domain.command("list")
def domain_list():
    """List available domains."""
    domains = list_domains()

    table = Table(title="Available Domains")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Default Personas")

    for d in domains:
        table.add_row(
            d.id,
            d.name,
            d.category.value,
            ", ".join(d.default_personas[:4]) + ("..." if len(d.default_personas) > 4 else ""),
        )

    console.print(table)


@domain.command("show")
@click.argument("domain_id")
def domain_show(domain_id):
    """Show details of a domain."""
    try:
        d = get_domain(domain_id)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold]{d.name}[/bold]\n"
            f"[dim]{d.description}[/dim]\n\n"
            f"[bold]Category:[/bold] {d.category.value}\n\n"
            f"[bold]Default Personas:[/bold]\n{', '.join(d.default_personas)}\n\n"
            f"[bold]Optional Personas:[/bold]\n{', '.join(d.optional_personas) or 'None'}\n\n"
            f"[bold]Recommended Mode:[/bold] {d.recommended_mode}\n\n"
            f"[bold]Example Queries:[/bold]\n" + "\n".join(f"• {q}" for q in d.example_queries),
            title=f"Domain: {d.id}",
            border_style="blue",
        )
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Config Commands
# ═══════════════════════════════════════════════════════════════════════════════


@main.group()
def config():
    """Manage configuration."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    config_manager = ctx.obj["config_manager"]
    cfg = config_manager.config

    console.print(
        Panel(
            f"[bold]API Settings[/bold]\n"
            f"  Provider: {cfg.api.provider}\n"
            f"  API Key: {'[set]' if cfg.api.api_key else '[not set]'}\n"
            f"  Model: {cfg.api.model or '[default]'}\n"
            f"  Base URL: {cfg.api.base_url or '[default]'}\n\n"
            f"[bold]Defaults[/bold]\n"
            f"  Mode: {cfg.default_mode}\n"
            f"  Domain: {cfg.default_domain}\n"
            f"  Temperature: {cfg.temperature}\n"
            f"  Max Tokens: {cfg.max_tokens_per_response}\n"
            f"  Synthesis Provider: {cfg.synthesis_provider or '[default]'}\n"
            f"  Synthesis Model: {cfg.synthesis_model or '[default]'}\n"
            f"  Synthesis Max Tokens: {cfg.synthesis_max_tokens or '[default]'}\n\n"
            f"[bold]Paths[/bold]\n"
            f"  Config: {config_manager.path}\n"
            f"  Custom Personas: {cfg.custom_personas_path or '[default]'}\n"
            f"  Custom Domains: {cfg.custom_domains_path or '[default]'}",
            title="Configuration",
            border_style="blue",
        )
    )


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx, key, value):
    """Set a configuration value."""
    config_manager = ctx.obj["config_manager"]

    # Type conversion
    if value.lower() in ("true", "false"):
        value = value.lower() == "true"
    elif value.isdigit():
        value = int(value)
    elif value.replace(".", "").isdigit():
        value = float(value)

    try:
        config_manager.set(key, value)
        config_manager.save()
        console.print(f"[green]✓[/green] Set {key} = {value}")
    except KeyError:
        console.print(f"[red]Error:[/red] Invalid key: {key}")


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx, key):
    """Get a configuration value."""
    config_manager = ctx.obj["config_manager"]
    value = config_manager.get(key)

    if value is None:
        console.print(f"[yellow]{key} is not set[/yellow]")
    else:
        console.print(f"{key} = {value}")


@config.command("preset-save")
@click.argument("preset_name")
@click.option("--domain", "-d", help="Domain to save in preset")
@click.option("--members", "-m", help="Comma-separated member IDs")
@click.option("--mode", help="Consultation mode")
@click.pass_context
def config_preset_save(ctx, preset_name, domain, members, mode):
    """Save current or specified settings as a preset."""
    config_manager = ctx.obj["config_manager"]

    preset = {}

    if domain:
        preset["domain"] = domain
    else:
        preset["domain"] = config_manager.get("default_domain")

    if members:
        preset["members"] = [m.strip() for m in members.split(",")]

    if mode:
        preset["mode"] = mode
    else:
        preset["mode"] = config_manager.get("default_mode")

    # Save to presets
    if not isinstance(config_manager.config.presets, dict):
        config_manager.config.presets = {}

    config_manager.config.presets[preset_name] = preset
    config_manager.save()

    console.print(f"[green]✓[/green] Preset '{preset_name}' saved")
    console.print(f"[dim]Use with: council consult --preset {preset_name}[/dim]")


@config.command("preset-list")
@click.pass_context
def config_preset_list(ctx):
    """List saved presets."""
    config_manager = ctx.obj["config_manager"]
    presets = config_manager.config.presets

    if not presets:
        console.print("[dim]No presets saved.[/dim]")
        console.print("[dim]Create one with: council config preset-save <name>[/dim]")
        return

    table = Table(title="Saved Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Domain")
    table.add_column("Mode")
    table.add_column("Members")

    for name, preset in presets.items():
        members = (
            ", ".join(preset.get("members", [])) if preset.get("members") else "[domain default]"
        )
        table.add_row(
            name,
            preset.get("domain", "general"),
            preset.get("mode", "synthesis"),
            members,
        )

    console.print(table)


@config.command("preset-delete")
@click.argument("preset_name")
@click.pass_context
def config_preset_delete(ctx, preset_name):
    """Delete a saved preset."""
    config_manager = ctx.obj["config_manager"]

    if preset_name in config_manager.config.presets:
        del config_manager.config.presets[preset_name]
        config_manager.save()
        console.print(f"[green]✓[/green] Preset '{preset_name}' deleted")
    else:
        console.print(f"[red]Error:[/red] Preset '{preset_name}' not found")


# ═══════════════════════════════════════════════════════════════════════════════
# Provider Commands
# ═══════════════════════════════════════════════════════════════════════════════


@main.command("providers")
@click.option("--diagnose", "-d", is_flag=True, help="Show detailed API key diagnostics")
def show_providers(diagnose):
    """List available LLM providers."""
    providers = list_providers()

    if diagnose:
        from .core.diagnostics import diagnose_api_keys

        diagnostics = diagnose_api_keys()

        console.print("\n[bold]API Key Diagnostics[/bold]")
        console.print("=" * 60)

        # Show provider status
        table = Table(title="Provider Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Has Key", style="green")
        table.add_column("Details")

        for provider, status in diagnostics["provider_status"].items():
            has_key = status.get("has_key", False)
            details = []
            if has_key:
                details.append(f"Length: {status.get('key_length', '?')}")
                if "key_prefix" in status:
                    details.append(f"Prefix: {status['key_prefix']}")
            else:
                details.append(f"Set: {status.get('env_var', 'N/A')}")
            if "note" in status:
                details.append(status["note"])

            table.add_row(
                provider.upper(),
                "[green]✓[/green]" if has_key else "[red]✗[/red]",
                ", ".join(details) if details else "N/A",
            )

        console.print(table)

        # Show recommendations
        if diagnostics["recommendations"]:
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in diagnostics["recommendations"]:
                console.print(f"  • {rec}")

        console.print()

    table = Table(title="Available LLM Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Env Variable")
    table.add_column("Status")

    for name in providers:
        env_var = f"{name.upper()}_API_KEY"
        # Check for Vercel AI Gateway for OpenAI
        if name == "openai":
            has_key = bool(
                os.environ.get(env_var)
                or os.environ.get("AI_GATEWAY_API_KEY")
                or os.environ.get("COUNCIL_API_KEY")
            )
        else:
            has_key = bool(os.environ.get(env_var) or os.environ.get("COUNCIL_API_KEY"))
        status = "[green]✓ Configured[/green]" if has_key else "[dim]Not configured[/dim]"
        table.add_row(name, env_var, status)

    # Add Vercel AI Gateway info
    if os.environ.get("AI_GATEWAY_API_KEY"):
        table.add_row("vercel", "AI_GATEWAY_API_KEY", "[green]✓ Configured[/green]")

    console.print(table)
    console.print(
        "\n[dim]Set API key via .env file, environment variable, or 'council config set api.api_key'[/dim]"
    )
    if not diagnose:
        console.print("[dim]Use --diagnose for detailed API key diagnostics[/dim]")


@main.command("test-key")
@click.option("--provider", "-p", default="openai", help="Provider to test")
@click.option("--api-key", "-k", help="API key to test (uses env/config if not provided)")
def test_key(provider: str, api_key: Optional[str]):
    """Test if an API key works for a provider."""
    from .core.diagnostics import test_api_key

    success, message = test_api_key(provider, api_key)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        console.print(f"[red]✗[/red] {message}")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("  1. Verify the API key is correct and not expired")
        console.print("  2. Check the key has proper permissions")
        console.print("  3. For OpenAI, ensure the key starts with 'sk-'")
        console.print("  4. Run 'council providers --diagnose' for detailed diagnostics")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# Web App Command
# ═══════════════════════════════════════════════════════════════════════════════


@main.command("web")
@click.option("--host", default="127.0.0.1", help="Host to bind the web server")
@click.option("--port", default=8000, type=int, help="Port to bind the web server")
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev only)")
@click.option("--no-open", is_flag=True, help="Don't auto-open browser")
def web(host: str, port: int, reload: bool, no_open: bool):
    """Run the Council AI web app."""
    try:
        import threading
        import time
        import webbrowser

        import uvicorn
    except ImportError:
        console.print(
            '[red]Error:[/red] uvicorn is not installed. Install with: pip install -e ".[web]"'
        )
        sys.exit(1)

    url = f"http://{host}:{port}"

    # Auto-open browser after a short delay
    if not no_open:

        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()
        console.print(f"[green]✓[/green] Server starting at [cyan]{url}[/cyan]")
        console.print("[dim]Opening browser automatically...[/dim]")

    uvicorn.run("council_ai.webapp:app", host=host, port=port, reload=reload)


# ═══════════════════════════════════════════════════════════════════════════════
# Review Command
# ═══════════════════════════════════════════════════════════════════════════════


@main.command("review")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--focus",
    "-f",
    type=click.Choice(["all", "code", "design", "security"]),
    default="all",
    help="Focus of the review",
)
@click.option("--provider", "-p", help="LLM provider")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key")
@click.option("--output", "-o", type=click.Path(), help="Save report to file")
@click.pass_context
def review(ctx, path, focus, provider, api_key, output):
    """
    Review a repository or directory.

    Performs a comprehensive AI-driven audit of the code at PATH.
    """
    config_manager = ctx.obj["config_manager"]
    # Check if api_key from CLI/env is a placeholder - if so, ignore it and try get_api_key()
    is_placeholder = api_key and ("your-" in api_key.lower() or "here" in api_key.lower())
    if is_placeholder:
        api_key = None  # Ignore placeholder, force get_api_key() to run

    api_key = api_key or get_api_key(provider or config_manager.get("api.provider", "anthropic"))

    if not api_key:
        console.print("[red]Error:[/red] No API key provided.")
        sys.exit(1)
    if "your-" in api_key.lower() or "here" in api_key.lower():
        console.print("[red]Error:[/red] API key appears to be a placeholder value.")
        console.print(
            "Please update your .env file with your actual API key (not the example value)."
        )
        console.print("Run 'council providers --diagnose' for help.")
        sys.exit(1)

    provider = provider or config_manager.get("api.provider", "anthropic")
    model = config_manager.get("api.model")

    from .tools.reviewer import RepositoryReviewer

    # Setup Council based on focus
    if focus == "design":
        council = Council.for_domain("creative", api_key=api_key, provider=provider, model=model)
    elif focus == "security":
        council = Council.for_domain("devops", api_key=api_key, provider=provider, model=model)
    else:
        # Custom mix for general review
        council = Council(api_key=api_key, provider=provider)
        try:
            council.add_member("rams")  # Design
            council.add_member("holman")  # Security
            council.add_member("kahneman")  # Cognitive
            council.add_member("taleb")  # Risk
        except ValueError:
            pass  # Fallback if specific personas missing

    reviewer = RepositoryReviewer(council)

    with console.status(f"[bold green]Scanning {path}...[/bold green]"):
        context = reviewer.gather_context(Path(path))
        context_str = reviewer.format_context(context)

    console.print(f"[green]✓[/green] Scanned {len(context['key_files'])} key files.")

    results = []

    # Execute Reviews
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Reviewing...", total=None)

        if focus in ["all", "code"]:
            progress.update(task, description="Reviewing Code Quality...")
            results.append(("Code Quality", reviewer.review_code_quality(context_str)))

        if focus in ["all", "design"]:
            progress.update(task, description="Reviewing Design & UX...")
            results.append(("Design & UX", reviewer.review_design_ux(context_str)))

        if focus in ["all", "security"]:
            progress.update(task, description="Auditing Security...")
            results.append(("Security Audit", reviewer.review_security(context_str)))

    # Output
    final_output = [f"# Repository Review: {context['project_name']}\n"]

    for title, result in results:
        section = f"\n## {title}\n\n{result.to_markdown()}"
        final_output.append(section)

        console.print(
            Panel(
                Markdown(result.synthesis or result.responses[0].content),
                title=title,
                border_style="green",
            )
        )

    if output:
        Path(output).write_text("\n".join(final_output))
        console.print(f"\n[green]✓[/green] Report saved to {output}")


# ═══════════════════════════════════════════════════════════════════════════════
# History Commands
# ═══════════════════════════════════════════════════════════════════════════════


@main.group("history")
def history_group():
    """Manage consultation and session history."""
    pass


@history_group.command("sessions")
@click.option("--limit", "-n", type=int, default=10, help="Maximum number of sessions")
def history_sessions(limit):
    """List saved sessions."""
    history = ConsultationHistory()
    sessions = history.list_sessions(limit=limit)

    if not sessions:
        console.print("[dim]No sessions found.[/dim]")
        return

    table = Table(title="Session History")
    table.add_column("Session ID", style="cyan")
    table.add_column("Council", style="white")
    table.add_column("Members", style="dim")
    table.add_column("Started At", style="yellow")

    for s in sessions:
        table.add_row(
            s["id"],
            s["name"],
            ", ".join(s["member_ids"]),
            s["started_at"][:16].replace("T", " "),
        )

    console.print(table)


@history_group.command("resume")
@click.argument("session_id", required=False)
@click.pass_context
def history_resume(ctx, session_id):
    """Resume a previous session (interactive)."""
    history = ConsultationHistory()

    if not session_id:
        sessions = history.list_sessions(limit=10)
        if not sessions:
            console.print("[yellow]No recent sessions found.[/yellow]")
            return

        console.print(Panel("[bold cyan]Resume Past Session[/bold cyan]", expand=False))

        # rich menu
        from rich.table import Table

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Session ID", style="cyan")
        table.add_column("Council", style="white")
        table.add_column("Started At", style="yellow")

        for i, s in enumerate(sessions, 1):
            table.add_row(
                str(i), s["id"][:13] + "...", s["name"], s["started_at"][:16].replace("T", " ")
            )

        console.print(table)

        choice = Prompt.ask(
            "Select session to resume",
            choices=[str(i) for i in range(1, len(sessions) + 1)] + ["q"],
            default="1",
        )

        if choice == "q":
            return

        selected = sessions[int(choice) - 1]
        session_id = selected["id"]

    # Load session to get metadata
    session = history.load_session(session_id)
    if not session:
        console.print(f"[red]Error:[/red] Session '{session_id}' not found.")
        return

    console.print(f"[green]✓[/green] Resuming session [cyan]{session_id}[/cyan]...")

    # Delegate to interactive command
    ctx.invoke(interactive, session_id=session_id)


@history_group.command("list")
@click.option("--limit", "-n", type=int, help="Maximum number of results")
@click.option("--offset", "-o", type=int, default=0, help="Skip N results")
def history_list(limit, offset):
    """List saved consultations."""
    history = ConsultationHistory()
    consultations = history.list(limit=limit, offset=offset)

    if not consultations:
        console.print("[dim]No consultations found.[/dim]")
        return

    table = Table(title="Consultation History")
    table.add_column("ID", style="cyan", width=36)
    table.add_column("Query", style="white", max_width=50)
    table.add_column("Mode", style="yellow")
    table.add_column("Date", style="dim")

    for cons in consultations:
        query_preview = cons["query"][:47] + "..." if len(cons["query"]) > 50 else cons["query"]
        date_str = cons["timestamp"][:10] if cons["timestamp"] else "N/A"
        table.add_row(
            cons["id"][:8] + "...",
            query_preview,
            cons["mode"],
            date_str,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(consultations)}[/dim]")


@history_group.command("show")
@click.argument("consultation_id")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="Output format",
)
def history_show(consultation_id, format):
    """Show a specific consultation."""
    history = ConsultationHistory()
    data = history.load(consultation_id)

    if not data:
        console.print(f"[red]Consultation '{consultation_id}' not found.[/red]")
        sys.exit(1)

    # Reconstruct ConsultationResult
    result = ConsultationResult.from_dict(data)

    if format == "json":
        import json

        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        console.print()
        console.print(Markdown(result.to_markdown()))


@history_group.command("search")
@click.argument("query")
@click.option("--limit", "-n", type=int, help="Maximum number of results")
def history_search(query, limit):
    """Search consultations."""
    history = ConsultationHistory()
    results = history.search(query, limit=limit)

    if not results:
        console.print(f"[dim]No consultations found matching '{query}'.[/dim]")
        return

    table = Table(title=f"Search Results: '{query}'")
    table.add_column("ID", style="cyan", width=36)
    table.add_column("Query", style="white", max_width=50)
    table.add_column("Mode", style="yellow")
    table.add_column("Date", style="dim")

    for cons in results:
        query_preview = cons["query"][:47] + "..." if len(cons["query"]) > 50 else cons["query"]
        date_str = cons["timestamp"][:10] if cons["timestamp"] else "N/A"
        table.add_row(
            cons["id"][:8] + "...",
            query_preview,
            cons["mode"],
            date_str,
        )

    console.print(table)
    console.print(f"\n[dim]Found: {len(results)}[/dim]")


@history_group.command("export")
@click.argument("consultation_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="Export format",
)
def history_export(consultation_id, output, format):
    """Export a consultation to a file."""
    history = ConsultationHistory()
    data = history.load(consultation_id)

    if not data:
        console.print(f"[red]Consultation '{consultation_id}' not found.[/red]")
        sys.exit(1)

    result = ConsultationResult.from_dict(data)

    if format == "json":
        import json

        content = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        ext = "json"
    else:
        content = result.to_markdown()
        ext = "md"

    if output:
        output_path = Path(output)
    else:
        # Generate filename from query
        safe_query = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "" for c in result.query[:30]
        )
        safe_query = safe_query.replace(" ", "_").lower()
        output_path = Path(f"consultation_{consultation_id[:8]}_{safe_query}.{ext}")

    output_path.write_text(content, encoding="utf-8")
    console.print(f"[green]✓[/green] Exported to {output_path}")


@history_group.command("export-session")
@click.argument("session_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def history_export_session(session_id, output):
    """Export an entire session as a findings report (planning-with-files format)."""
    history = ConsultationHistory()
    session = history.load_session(session_id)

    if not session:
        console.print(f"[red]Error:[/red] Session '{session_id}' not found.")
        sys.exit(1)

    # Format using planning-with-files principles
    lines = [
        f"# Findings Report: {session.council_name}",
        f"**Session ID:** {session.session_id}",
        f"**Date:** {session.started_at}",
        f"**Members:** {', '.join(session.members)}",
        "",
        "## Executive Summary",
        "This report summarizes a multi-turn consultation session with the AI Advisory Council.",
        "",
        "## Timeline of Discussion",
        "",
    ]

    for i, res in enumerate(session.consultations, 1):
        lines.append(f"### Turn {i}: {res.query}")
        lines.append("")
        if res.synthesis:
            lines.append("#### Synthesized Conclusion")
            lines.append(res.synthesis)
            lines.append("")

        # Add key points from individual responses if no synthesis
        if not res.synthesis:
            for resp in res.responses:
                lines.append(f"- **{resp.persona.name}:** {resp.content[:200]}...")
            lines.append("")

    lines.append("## Recommendations & Next Steps")
    lines.append("Based on the collective wisdom of the council, the following themes emerged:")
    # Simple heuristic to extract themes
    lines.append("- Review the synthesized conclusions above for actionable insights.")
    lines.append("- Consider the different perspectives offered by the diverse members.")

    content = "\n".join(lines)

    if output:
        output_path = Path(output)
    else:
        output_path = Path(f"findings_{session_id[:8]}.md")

    output_path.write_text(content, encoding="utf-8")
    console.print(f"[green]✓[/green] Session report exported to {output_path}")


@history_group.command("delete")
@click.argument("consultation_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def history_delete(consultation_id, yes):
    """Delete a consultation."""
    history = ConsultationHistory()
    data = history.load(consultation_id)

    if not data:
        console.print(f"[red]Consultation '{consultation_id}' not found.[/red]")
        sys.exit(1)

    if not yes:
        query_preview = data["query"][:50] + "..." if len(data["query"]) > 50 else data["query"]
        if not Confirm.ask(f"Delete consultation: {query_preview}?"):
            console.print("[dim]Cancelled.[/dim]")
            return

    if history.delete(consultation_id):
        console.print(f"[green]✓[/green] Deleted consultation '{consultation_id}'")
    else:
        console.print(f"[red]Failed to delete consultation '{consultation_id}'[/red]")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# Doctor Command
# ═══════════════════════════════════════════════════════════════════════════════


@main.command()
def doctor():
    """
    🏥 Run system diagnostics ("Council Doctor").

    Checks API keys, provider connectivity, and system health.
    """
    import asyncio

    from .core.diagnostics import (
        check_provider_connectivity,
        check_tts_connectivity,
        diagnose_api_keys,
    )

    console.print(
        Panel(
            "[bold]🏥 Council Doctor[/bold]\n" "Checking vital signs...",
            border_style="green",
        )
    )

    # 1. API Key Check
    with console.status("[bold green]Checking API keys..."):
        # Artificial delay for UX
        # time.sleep(0.5)
        key_diag = diagnose_api_keys()

    table = Table(title="API Key Configuration", box=None)
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    configured_providers = []

    for provider, status in key_diag["provider_status"].items():
        if status["has_key"]:
            table.add_row(provider, "✅ Configured", f"Prefix: {status.get('key_prefix', '***')}")
            if provider in ["openai", "anthropic", "gemini"]:
                configured_providers.append(provider)
        else:
            table.add_row(provider, "❌ Missing", f"Set {status.get('env_var', 'Env Var')}")

    console.print(table)
    console.print()

    # 2. Connectivity Check
    if configured_providers:
        console.print("[bold]Testing Connectivity...[/bold]")
        conn_table = Table(title="Provider Connection Test", box=None)
        conn_table.add_column("Provider", style="cyan")
        conn_table.add_column("Result", style="bold")
        conn_table.add_column("Latency", justify="right")
        conn_table.add_column("Message", style="dim")

        async def run_checks():
            tasks = [check_provider_connectivity(p) for p in configured_providers]
            return await asyncio.gather(*tasks)

        with console.status("[bold green]Pinging providers..."):
            results = asyncio.run(run_checks())

        for provider, result in zip(configured_providers, results):
            success, msg, latency = result
            status_icon = "✅ Online" if success else "❌ Failed"
            status_style = "green" if success else "red"
            conn_table.add_row(
                provider, f"[{status_style}]{status_icon}[/{status_style}]", f"{latency:.0f}ms", msg
            )

        console.print(conn_table)
        console.print()
    else:
        console.print("[yellow]⚠️ No LLM providers configured to test connectivity.[/yellow]\n")

    # 3. TTS Check
    with console.status("[bold green]Checking Voice capability..."):
        tts_results = check_tts_connectivity()

    if tts_results:
        tts_table = Table(title="Text-to-Speech Status", box=None)
        tts_table.add_column("Provider", style="cyan")
        tts_table.add_column("Status", style="bold")
        tts_table.add_column("Message", style="dim")

        for provider, res in tts_results.items():
            icon = "✅ Ready" if res["ok"] else "❌ Error"
            style = "green" if res["ok"] else "red"
            tts_table.add_row(provider, f"[{style}]{icon}[/{style}]", res["msg"])

        console.print(tts_table)
    else:
        console.print("[dim]No TTS providers configured.[/dim]")

    console.print("\n[bold]Diagnosis:[/bold]")
    if key_diag["recommendations"]:
        for rec in key_diag["recommendations"]:
            console.print(f"• {rec}")
    else:
        console.print("• System appears healthy.")
