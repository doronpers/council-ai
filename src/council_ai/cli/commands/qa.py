"""
QA / Evaluate Command
Uses sono-eval to assess content for quality, risks, and best practices.
"""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from ...tools.sono_eval_client import SonoEvalClient

console = Console()


@click.command(name="qa")
@click.argument("content", required=False)
@click.option("--candidate-id", "-id", default="council_qa", help="Session/Candidate ID")
@click.option(
    "--path", "-p", "paths", multiple=True, help="Assessment paths (technical, design, etc.)"
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
@click.option("--json", "-j", "json_output", is_flag=True, help="Output raw JSON")
def qa_command(
    content: Optional[str],
    candidate_id: str,
    paths: list[str],
    verbose: bool,
    json_output: bool,
):
    """
    Run quality assurance on text/code using sono-eval.

    CONTENT can be passed as an argument or piped via stdin.

    Examples:
      council qa "def foo(): pass"
      council consult "Design a system..." | council qa
    """
    # Handle input (arg or stdin)
    if not content:
        if not sys.stdin.isatty():
            content = sys.stdin.read()

    if not content:
        console.print("[red]Error: No content provided (provide argument or pipe stdin)[/red]")
        sys.exit(1)

    client = SonoEvalClient()

    if not client.is_available():
        console.print("[yellow]Warning: 'sono-eval' not found in PATH or peer directory.[/yellow]")
        console.print("Please ensure sono-eval is installed or available.")
        sys.exit(1)

    with console.status("[bold green]Running quality assessment..."):
        try:
            result = client.assess_text(
                content=content, candidate_id=candidate_id, paths=list(paths) if paths else None
            )
        except Exception as e:
            console.print(f"[red]Assessment failed: {e}[/red]")
            sys.exit(1)

    if json_output:
        console.print_json(data=result)
        return

    # Display friendly output
    score = result.get("overall_score", 0)
    score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"

    console.print(
        Panel(
            f"[bold {score_color}]Overall Score: {score:.1f}/100[/bold {score_color}]",
            title="Assessment Result",
            expand=False,
        )
    )

    # Show Summary
    if "summary" in result:
        console.print(f"\n[bold]Summary:[/bold] {result['summary']}")

    # Key Findings
    findings = result.get("key_findings", [])
    if findings:
        console.print("\n[bold]Key Findings:[/bold]")
        for finding in findings:
            console.print(f"• {finding}")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in recommendations:
            console.print(f"• {rec}")

    if verbose:
        # Show path scores
        path_scores = result.get("path_scores", [])
        if path_scores:
            console.print("\n[bold]Detailed Scores:[/bold]")
            for ps in path_scores:
                p_score = ps.get("overall_score", 0)
                p_name = ps.get("path", "Unknown")
                console.print(f"- {p_name}: {p_score:.1f}")
