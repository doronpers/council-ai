"""CLI commands for personal integration management."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .core.personal_integration import (
    PersonalIntegration,
    get_personal_status,
    verify_personal_integration,
)

console = Console()


@click.group("personal")
def personal():
    """Manage council-ai-personal integration."""
    pass


@personal.command("status")
def status():
    """Show personal integration status."""
    status_info = get_personal_status()

    console.print("\n[bold]Personal Integration Status[/bold]")
    console.print("=" * 60)

    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    # Detection status
    detected = status_info.get("detected", False)
    table.add_row("Repository Detected", "✅ Yes" if detected else "❌ No")
    if detected:
        table.add_row("Repository Path", status_info.get("repo_path", "N/A"))

    # Configuration status
    configured = status_info.get("configured", False)
    table.add_row("Configured", "✅ Yes" if configured else "❌ No")
    table.add_row("Config Directory", status_info.get("config_dir", "N/A"))

    # Available resources
    available = status_info.get("available", {})
    if available:
        if available.get("configs"):
            table.add_row("Configs Available", "✅ Yes")
        if "personas" in available:
            table.add_row("Personal Personas", str(available["personas"]))
        if "scripts" in available:
            table.add_row("Personal Scripts", str(available["scripts"]))

    console.print(table)
    console.print()

    if not detected:
        console.print(
            "[yellow]ℹ[/yellow] council-ai-personal repository not detected.\n"
            "Place it in one of these locations:\n"
            "  • Sibling directory: ../council-ai-personal\n"
            "  • Home directory: ~/council-ai-personal\n"
            "  • Set COUNCIL_AI_PERSONAL_PATH environment variable"
        )
    elif not configured:
        console.print(
            "[yellow]ℹ[/yellow] Repository detected but not integrated.\n"
            "Run [cyan]council personal integrate[/cyan] to activate."
        )
    else:
        console.print("[green]✓[/green] Personal integration is active!")


@personal.command("integrate")
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to council-ai-personal repository",
)
@click.option(
    "--auto",
    is_flag=True,
    help="Skip confirmation prompts",
)
def integrate(path: Path | None, auto: bool):
    """Integrate council-ai-personal repository."""
    integration = PersonalIntegration()

    # Detect or use provided path
    repo_path = path or integration.detect_repo()
    if not repo_path:
        console.print("[red]Error:[/red] Could not detect council-ai-personal repository.")
        console.print(
            "Please specify the path with [cyan]--path[/cyan] or place it in a standard location."
        )
        sys.exit(1)

    console.print(f"[cyan]Found repository at:[/cyan] {repo_path}")

    # Check if already configured
    if integration.is_configured():
        if not auto:
            from rich.prompt import Confirm

            if not Confirm.ask("Personal integration already exists. Re-integrate?", default=False):
                console.print("[dim]Cancelled.[/dim]")
                return
        console.print("[yellow]Re-integrating...[/yellow]")
    else:
        if not auto:
            from rich.prompt import Confirm

            if not Confirm.ask("Integrate council-ai-personal now?", default=True):
                console.print("[dim]Cancelled.[/dim]")
                return

    # Perform integration
    console.print("\n[bold]Integrating...[/bold]")
    success = integration.integrate(repo_path)

    if success:
        console.print("[green]✓[/green] Integration completed successfully!")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  • Personal configs are now available")
        console.print("  • Personal personas can be used in consultations")
        console.print("  • Run [cyan]council personal verify[/cyan] to check everything")
    else:
        console.print("[red]✗[/red] Integration failed.")
        console.print("Check the error messages above for details.")
        sys.exit(1)


@personal.command("verify")
def verify():
    """Verify that personal integration is working correctly."""
    console.print("\n[bold]Verifying Personal Integration[/bold]")
    console.print("=" * 60)

    verification = verify_personal_integration()

    table = Table(title="Verification Results", box=None)
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    # Detection
    detected = verification.get("detected", False)
    table.add_row(
        "Repository Detected",
        "[green]✓[/green]" if detected else "[red]✗[/red]",
        verification.get("repo_path", "Not found"),
    )

    # Configuration
    configured = verification.get("configured", False)
    table.add_row(
        "Configuration",
        "[green]✓[/green]" if configured else "[red]✗[/red]",
        "Integrated" if configured else "Not integrated",
    )

    # Configs loaded
    configs_loaded = verification.get("configs_loaded", False)
    table.add_row(
        "Configs Loaded",
        "[green]✓[/green]" if configs_loaded else "[red]✗[/red]",
        "Available" if configs_loaded else "Not found",
    )

    # Personas available
    personas_available = verification.get("personas_available", False)
    persona_count = verification.get("persona_count", 0)
    table.add_row(
        "Personas Available",
        "[green]✓[/green]" if personas_available else "[red]✗[/red]",
        f"{persona_count} personas" if personas_available else "None found",
    )

    console.print(table)
    console.print()

    # Show issues if any
    issues = verification.get("issues", [])
    if issues:
        console.print("[yellow]Issues Found:[/yellow]")
        for issue in issues:
            console.print(f"  • {issue}")
        console.print()
        sys.exit(1)
    else:
        console.print(
            "[green]✓[/green] All checks passed! Personal integration is working correctly."
        )


@personal.command("detect")
def detect():
    """Detect council-ai-personal repository location."""
    integration = PersonalIntegration()
    repo_path = integration.detect_repo()

    if repo_path:
        console.print(f"[green]✓[/green] Found at: {repo_path}")
    else:
        console.print("[red]✗[/red] Not detected in standard locations.")
        console.print("\n[bold]Checked locations:[/bold]")
        console.print("  1. COUNCIL_AI_PERSONAL_PATH environment variable")
        console.print("  2. Sibling directory: ../council-ai-personal")
        console.print("  3. Home directory: ~/council-ai-personal")
        console.print("  4. Current directory parent")
        sys.exit(1)
