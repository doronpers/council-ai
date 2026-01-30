"""Session report commands for Council AI."""

from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ...core.history import ConsultationHistory
from ...core.session_reports import SessionReport

console = Console()


@click.group()
def session():
    """Session management and reporting commands."""
    pass


@session.command()
@click.option("--session-id", "-s", help="Session ID to generate report for")
@click.option("--output", "-o", type=click.Path(), help="Output file path (JSON or Markdown)")
@click.option(
    "--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown"
)
@click.option("--auto-save", is_flag=True, help="Automatically save report without prompting")
def report(session_id: str, output: str, output_format: str, auto_save: bool):
    """
    Generate a comprehensive session report.

    Examples:
        # Generate report for most recent session
        council session report

        # Generate report for specific session
        council session report --session-id abc123

        # Save report to file
        council session report --output session_report.md

        # Save as JSON
        council session report --format json --output report.json
    """
    history = ConsultationHistory()
    report_generator = SessionReport(history)

    # Get session ID if not provided
    if not session_id:
        sessions = history.list_sessions(limit=1)
        if not sessions:
            console.print("[red]Error:[/red] No sessions found")
            console.print("[dim]Run a consultation first to create a session[/dim]")
            raise click.Abort()
        session_id = sessions[0]["id"]
        console.print(f"[dim]Using most recent session: {session_id[:8]}...[/dim]")

    try:
        # Generate report
        output_path = Path(output) if output else None
        report_data = report_generator.generate_session_report(session_id, output_path)

        # Display report
        if not output:
            report_generator.display_report(report_data)

            # Offer to save
            if not auto_save:
                if Confirm.ask("\n[cyan]Save this report to a file?[/cyan]", default=True):
                    default_path = f"session_report_{session_id[:8]}.md"
                    save_path = Prompt.ask("Output file path", default=default_path)
                    try:
                        output_path = Path(save_path)
                        report_generator.generate_session_report(session_id, output_path)
                        console.print(f"[green]✓ Report saved to {save_path}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error saving report: {e}[/red]")
        else:
            console.print(f"[green]✓ Report saved to {output}[/green]")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        raise click.Abort()


@session.command()
@click.option("--session-id", "-s", help="Session ID to end")
def end(session_id: str):
    """
    End a session and generate a report.

    Examples:
        # End current session
        council session end

        # End specific session
        council session end --session-id abc123
    """
    history = ConsultationHistory()
    report_generator = SessionReport(history)

    # Get session ID if not provided
    if not session_id:
        sessions = history.list_sessions(limit=1)
        if not sessions:
            console.print("[yellow]No active sessions found[/yellow]")
            return
        session_id = sessions[0]["id"]

    try:
        # Generate and display report
        report_data = report_generator.generate_session_report(session_id)
        report_generator.display_report(report_data)

        # Offer to save
        if Confirm.ask("\n[cyan]Save session report?[/cyan]", default=True):
            default_path = f"session_report_{session_id[:8]}.md"
            save_path = Prompt.ask("Output file path", default=default_path)
            try:
                output_path = Path(save_path)
                report_generator.generate_session_report(session_id, output_path)
                console.print(f"[green]✓ Report saved to {save_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving report: {e}[/red]")

        console.print("\n[green]✓ Session ended[/green]")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@session.command()
def list():
    """List all sessions."""
    history = ConsultationHistory()
    sessions = history.list_sessions(limit=50)

    if not sessions:
        console.print("[yellow]No sessions found[/yellow]")
        return

    from rich.table import Table

    console.print(f"\n[bold cyan]Sessions ({len(sessions)})[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Session ID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Members", style="dim")
    table.add_column("Started", style="dim")

    for s in sessions:
        members_str = ", ".join(s.get("members", [])[:3])
        if len(s.get("members", [])) > 3:
            members_str += "..."

        started = s.get("started_at", "")
        if started:
            try:
                from datetime import datetime

                if isinstance(started, str):
                    dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    started = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass

        table.add_row(
            s.get("id", "")[:8] if s.get("id") else "N/A",
            s.get("name", "Unknown"),
            members_str,
            str(started)[:16] if started else "N/A",
        )

    console.print(table)
