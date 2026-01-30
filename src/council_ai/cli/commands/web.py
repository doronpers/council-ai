"""Web application commands."""

import click

from ..utils import run_web


@click.command("web")
@click.option("--host", default="127.0.0.1", help="Host to bind the web server")
@click.option("--port", default=8000, type=int, help="Port to bind the web server")
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev only)")
@click.option("--no-open", is_flag=True, help="Don't auto-open browser")
def web(host: str, port: int, reload: bool, no_open: bool):
    """Run the Council AI web server."""
    run_web(host, port, reload, no_open)


@click.command("ui")
@click.option("--host", default="127.0.0.1", help="Host to bind the web server")
@click.option("--port", default=8000, type=int, help="Port to bind the web server")
@click.option("--no-open", is_flag=True, help="Don't auto-open browser")
def ui(host: str, port: int, no_open: bool):
    """Launch the Council AI web interface."""
    run_web(host, port, False, no_open)
