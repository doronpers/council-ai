"""History and session management commands."""

import sys
from pathlib import Path

import click
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ...core.history import ConsultationHistory
from ...core.session import ConsultationResult
from ..utils import console


@click.group("history")
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
    from .interactive import interactive

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
