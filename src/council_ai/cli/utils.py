"""Shared utilities for the Council AI CLI."""

import socket
import sys
import threading
import time
import webbrowser
from functools import wraps

from rich.console import Console
from rich.table import Table

from ..core.config import get_api_key, is_placeholder_key
from ..core.council import Council

# Reconfigure stdout/stderr for Windows to support UTF-8 (emojis etc)
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()
DEFAULT_PROVIDER = "anthropic"


def require_api_key(func):
    @wraps(func)
    def wrapper(ctx, *args, **kwargs):
        config_manager = ctx.obj["config_manager"]
        provider = kwargs.get("provider")
        api_key = kwargs.get("api_key")

        requested_provider = provider or config_manager.get("api.provider", DEFAULT_PROVIDER)

        # LM Studio doesn't require an API key - it uses a dummy key
        if requested_provider == "lmstudio":
            if not api_key:
                api_key = "lm-studio"  # pragma: allowlist secret  # Dummy key for LM Studio
            kwargs["api_key"] = api_key
            return func(ctx, *args, **kwargs)

        if is_placeholder_key(api_key):
            api_key = None

        api_key = api_key or get_api_key(requested_provider)
        if not api_key:
            console.print("[red]Error:[/red] No API key provided.")
            console.print(
                "Set via --api-key, COUNCIL_API_KEY env var, or 'council config set api.api_key'"
            )
            sys.exit(1)
        if is_placeholder_key(api_key):
            console.print("[red]Error:[/red] API key appears to be a placeholder value.")
            console.print(
                "Please update your .env file with your actual API key (not the example value)."
            )
            console.print("Run 'council providers --diagnose' for help.")
            sys.exit(1)

        kwargs["api_key"] = api_key
        return func(ctx, *args, **kwargs)

    return wrapper


def assemble_council(domain, members, api_key, provider, model, base_url):
    """Assemble a council from domain or specific members.

    Args:
        domain: Domain preset to use
        members: List of specific member IDs, or None to use domain
        api_key: API key for the LLM provider
        provider: LLM provider name
        model: Model name/ID
        base_url: Base URL for custom endpoints

    Returns:
        Council: Assembled council instance
    """
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
    return council


def show_members(council):
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


def run_web(host: str, port: int, reload: bool, no_open: bool):
    """Internal helper to run the web server with port discovery."""
    try:
        import aiohttp  # noqa: F401
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError as e:
        console.print(
            f"[red]Error:[/red] Missing dependency: [bold]{e.name}[/bold]. "
            'Install with: [cyan]pip install -e ".[web]"[/cyan]'
        )
        sys.exit(1)

    # Find available port if default is busy
    def is_port_in_use(p):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, p)) == 0

    original_port = port
    while is_port_in_use(port):
        if port >= original_port + 10:
            break
        port += 1

    if port != original_port:
        console.print(
            f"[yellow]⚠️[/yellow] Port {original_port} is busy, using [bold]{port}[/bold]"
        )

    # Resolve display host for helpful feedback
    display_host = host
    if host == "0.0.0.0":
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            display_host = s.getsockname()[0]
            s.close()
        except Exception:
            display_host = "localhost"

    url = f"http://{display_host}:{port}"

    # Auto-open browser after a short delay
    if not no_open:

        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(url if host != "0.0.0.0" else f"http://localhost:{port}")

        threading.Thread(target=open_browser, daemon=True).start()
        console.print(f"[green]✓[/green] Server starting at [cyan]{url}[/cyan]")
        if host == "0.0.0.0":
            console.print(f"[dim]Local access: http://localhost:{port}[/dim]")
        if not no_open:
            console.print("[dim]Opening browser automatically...[/dim]")

    uvicorn.run("council_ai.webapp:app", host=host, port=port, reload=reload)
