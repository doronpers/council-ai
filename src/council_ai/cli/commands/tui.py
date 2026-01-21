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
    # #region agent log
    import json

    with open("/Volumes/Treehorn/Gits/sono-platform/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "id": "log_tui_entry",
                    "timestamp": __import__("time").time() * 1000,
                    "location": "tui.py:18",
                    "message": "TUI command entry",
                    "data": {
                        "domain": domain,
                        "members": list(members) if members else None,
                        "provider": provider,
                        "has_api_key": bool(api_key),
                    },
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A",
                }
            )
            + "\n"
        )
    # #endregion
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
    # #region agent log
    import json

    with open("/Volumes/Treehorn/Gits/sono-platform/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "id": "log_tui_before_create",
                    "timestamp": __import__("time").time() * 1000,
                    "location": "tui.py:49",
                    "message": "Before CouncilTUI creation",
                    "data": {"domain": domain, "model": model, "base_url": base_url},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B",
                }
            )
            + "\n"
        )
    # #endregion
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
        # #region agent log
        import json

        with open("/Volumes/Treehorn/Gits/sono-platform/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "id": "log_tui_created",
                        "timestamp": __import__("time").time() * 1000,
                        "location": "tui.py:59",
                        "message": "CouncilTUI created successfully",
                        "data": {"has_council": hasattr(app, "council")},
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "B",
                    }
                )
                + "\n"
            )
        # #endregion
    except Exception as e:
        # #region agent log
        import json
        import traceback

        with open("/Volumes/Treehorn/Gits/sono-platform/.cursor/debug.log", "a") as f:
            f.write(
                json.dumps(
                    {
                        "id": "log_tui_create_error",
                        "timestamp": __import__("time").time() * 1000,
                        "location": "tui.py:62",
                        "message": "CouncilTUI creation failed",
                        "data": {
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "traceback": traceback.format_exc(),
                        },
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "B",
                    }
                )
                + "\n"
            )
        # #endregion
        raise
    # #region agent log
    import json

    with open("/Volumes/Treehorn/Gits/sono-platform/.cursor/debug.log", "a") as f:
        f.write(
            json.dumps(
                {
                    "id": "log_tui_before_run",
                    "timestamp": __import__("time").time() * 1000,
                    "location": "tui.py:64",
                    "message": "Before app.run()",
                    "data": {},
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "C",
                }
            )
            + "\n"
        )
    # #endregion
    app.run()
