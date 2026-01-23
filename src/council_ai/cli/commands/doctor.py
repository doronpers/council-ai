"""
Diagnostic and maintenance commands.
"""

import asyncio
import os
import sys

import click
from rich.panel import Panel
from rich.table import Table

from ...providers import list_providers
from ..utils import console


@click.group("cost")
def cost_group():
    """View cost tracking information."""
    pass


@cost_group.command("summary")
@click.option("--session", "-s", "session_id", help="Session ID to get costs for")
def cost_summary(session_id):
    """Show cost summary for current session or specified session."""
    from ...core.history import ConsultationHistory

    history = ConsultationHistory()

    if session_id:
        costs = history.get_session_costs(session_id)
        if costs["total_cost_usd"] > 0:
            console.print("\n[bold]Session Cost Summary[/bold]")
            console.print(f"Session ID: {session_id}")
            console.print(f"Total Cost: ${costs['total_cost_usd']:.2f}")
            console.print(f"Consultations: {costs['consultation_count']}")
            console.print(
                f"Total Tokens: {costs['total_input_tokens'] + costs['total_output_tokens']:,}"
            )
        else:
            console.print(f"[dim]No cost data found for session {session_id}[/dim]")
    else:
        # Show cost for most recent session
        sessions = history.list_sessions(limit=1)
        if sessions:
            session_id = sessions[0]["id"]
            costs = history.get_session_costs(session_id)
            if costs["total_cost_usd"] > 0:
                console.print("\n[bold]Recent Session Cost[/bold]")
                console.print(f"Session: {sessions[0]['name']}")
                console.print(f"Total Cost: ${costs['total_cost_usd']:.2f}")
                console.print(f"Consultations: {costs['consultation_count']}")
            else:
                console.print("[dim]No cost data available for recent session[/dim]")
        else:
            console.print("[dim]No sessions found[/dim]")


@click.command("providers")
@click.option("--diagnose", "-d", is_flag=True, help="Show detailed API key diagnostics")
def show_providers(diagnose):
    """List available LLM providers."""
    providers = list_providers()

    if diagnose:
        from ...core.diagnostics import diagnose_api_keys

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
        "\n[dim]Set API key via .env file, env var, or 'council config set api.api_key'[/dim]"
    )
    if not diagnose:
        console.print("[dim]Use --diagnose for detailed API key diagnostics[/dim]")


@click.command("test-key")
@click.option("--provider", "-p", default="openai", help="Provider to test")
@click.option("--api-key", "-k", help="API key to test (uses env/config if not provided)")
def test_key(provider: str, api_key: str):
    """Test if an API key works for a provider."""
    from ...core.diagnostics import test_api_key

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


@click.command()
def doctor():
    """
    🏥 Run system diagnostics ("Council Doctor").

    Checks API keys, provider connectivity, and system health.
    """
    from ...core.diagnostics import (
        check_provider_connectivity,
        check_tts_connectivity,
        diagnose_api_keys,
    )

    console.print(
        Panel(
            "[bold]🏥 Council Doctor[/bold]\nChecking vital signs...",
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
            if provider == "lmstudio":
                table.add_row(provider, "✅ Active", "Running locally at http://localhost:1234")
                configured_providers.append(provider)
            else:
                table.add_row(
                    provider, "✅ Configured", f"Prefix: {status.get('key_prefix', '***')}"
                )
                if provider in ["openai", "anthropic", "gemini"]:
                    configured_providers.append(provider)
        else:
            if provider == "lmstudio":
                table.add_row(provider, "❌ Offline", "LM Studio not detected")
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
            try:
                results = asyncio.run(run_checks())
            except Exception as e:
                console.print(f"[red]Error running provider checks: {e}[/red]")
                return

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
