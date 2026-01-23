"""TUI command for Council AI."""

import sys

import click

from ..utils import DEFAULT_PROVIDER, console, require_api_key


@click.command("tui")
@click.option("--domain", "-d", help="Domain preset to use")
@click.option("--members", "-m", multiple=True, help="Specific personas to consult")
@click.option("--provider", "-p", help="LLM provider")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key for provider")
@click.option("--session", "-s", "session_id", help="Resume an existing session ID")
@click.pass_context
@require_api_key
def tui(ctx, domain, members, provider, api_key, session_id):
    """
    Launch Text User Interface for Council AI.

    Provides a modern, interactive interface with minimal typing,
    command history, and automatic context preservation.

    Examples:
      council tui
      council tui --domain business
      council tui --members MD --members DK
      council tui --session abc123
    """
    try:
        from ..tui.app import CouncilTUI
    except ImportError:
        console.print(
            "[red]Error:[/red] Textual is not installed. Install with: [cyan]pip install -e '.[tui]'[/cyan]"
        )
        sys.exit(1)

    config_manager = ctx.obj["config_manager"]

    # Apply defaults
    if not domain:
        domain = config_manager.get("default_domain", "general")
    if not provider:
        provider = config_manager.get("api.provider", DEFAULT_PROVIDER)
    model = config_manager.get("api.model")
    base_url = config_manager.get("api.base_url")

    # Create and run TUI
    try:
        app = CouncilTUI(
            domain=domain,
            members=list(members) if members else None,
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            session_id=session_id,
        )
    except Exception:
        raise
    app.run()
