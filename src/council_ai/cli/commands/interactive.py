"""
Interactive session command.
"""

import click
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from ..utils import console, require_api_key, show_members, DEFAULT_PROVIDER


@click.command()
@click.option("--domain", "-d", default="general", help="Domain preset to use")
@click.option("--provider", "-p", help="LLM provider")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key")
@click.option("--session", "-s", "session_id", help="Resume an existing session ID")
@click.pass_context
@require_api_key
def interactive(ctx, domain, provider, api_key, session_id):
    """
    Start an interactive council session.

    Have a multi-turn conversation with your council.
    """
    config_manager = ctx.obj["config_manager"]

    provider = provider or config_manager.get("api.provider", DEFAULT_PROVIDER)
    model = config_manager.get("api.model")
    base_url = config_manager.get("api.base_url")

    from ...core.council import Council

    council = Council.for_domain(
        domain,
        api_key=api_key,
        provider=provider,
        model=model,
        base_url=base_url,
    )

    # Enable history
    from ...core.history import ConsultationHistory

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
                    show_members(council)
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
                    from ...core.council import ConsultationMode

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
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
