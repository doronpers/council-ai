"""
Code review command.
"""

from pathlib import Path
import click
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from ..utils import console, require_api_key, DEFAULT_PROVIDER


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option(
    "--focus",
    "-f",
    type=click.Choice(["all", "code", "design", "security"]),
    default="all",
    help="Focus of the review",
)
@click.option("--provider", "-p", help="LLM provider")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key")
@click.option("--output", "-o", type=click.Path(), help="Save report to file")
@click.pass_context
@require_api_key
def review(ctx, path, focus, provider, api_key, output):
    """
    Review a repository or directory.

    Performs a comprehensive AI-driven audit of the code at PATH.
    """
    config_manager = ctx.obj["config_manager"]
    provider = provider or config_manager.get("api.provider", DEFAULT_PROVIDER)
    model = config_manager.get("api.model")

    from ...core.council import Council
    from ...tools.reviewer import RepositoryReviewer

    # Setup Council based on focus
    if focus == "design":
        council = Council.for_domain("creative", api_key=api_key, provider=provider, model=model)
    elif focus == "security":
        council = Council.for_domain("devops", api_key=api_key, provider=provider, model=model)
    else:
        # Custom mix for general review
        council = Council(api_key=api_key, provider=provider)
        try:
            council.add_member("rams")  # Design
            council.add_member("holman")  # Security
            council.add_member("kahneman")  # Cognitive
            council.add_member("taleb")  # Risk
        except ValueError:
            pass  # Fallback if specific personas missing

    reviewer = RepositoryReviewer(council)

    with console.status(f"[bold green]Scanning {path}...[/bold green]"):
        context = reviewer.gather_context(Path(path))
        context_str = reviewer.format_context(context)

    console.print(f"[green]✓[/green] Scanned {len(context['key_files'])} key files.")

    results = []

    # Execute Reviews
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Reviewing...", total=None)

        if focus in ["all", "code"]:
            progress.update(task, description="Reviewing Code Quality...")
            results.append(("Code Quality", reviewer.review_code_quality(context_str)))

        if focus in ["all", "design"]:
            progress.update(task, description="Reviewing Design & UX...")
            results.append(("Design & UX", reviewer.review_design_ux(context_str)))

        if focus in ["all", "security"]:
            progress.update(task, description="Auditing Security...")
            results.append(("Security Audit", reviewer.review_security(context_str)))

    # Output
    final_output = [f"# Repository Review: {context['project_name']}\n"]

    for title, result in results:
        section = f"\n## {title}\n\n{result.to_markdown()}"
        final_output.append(section)

        console.print(
            Panel(
                Markdown(result.synthesis or result.responses[0].content),
                title=title,
                border_style="green",
            )
        )

    if output:
        Path(output).write_text("\n".join(final_output))
        console.print(f"\n[green]✓[/green] Report saved to {output}")
