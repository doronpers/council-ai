import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import get_domain, list_domains

console = Console()


@click.group()
def domain():
    """Manage council domains."""
    pass


@domain.command("list")
def domain_list():
    """List available domains."""
    domains = list_domains()

    table = Table(title="Available Domains")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Default Personas")

    for d in domains:
        table.add_row(
            d.id,
            d.name,
            d.category.value,
            ", ".join(d.default_personas[:4]) + ("..." if len(d.default_personas) > 4 else ""),
        )

    console.print(table)


@domain.command("show")
@click.argument("domain_id")
def domain_show(domain_id):
    """Show details of a domain."""
    try:
        d = get_domain(domain_id)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold]{d.name}[/bold]\n"
            f"[dim]{d.description}[/dim]\n\n"
            f"[bold]Category:[/bold] {d.category.value}\n\n"
            f"[bold]Default Personas:[/bold]\n{', '.join(d.default_personas)}\n\n"
            f"[bold]Optional Personas:[/bold]\n{', '.join(d.optional_personas) or 'None'}\n\n"
            f"[bold]Recommended Mode:[/bold] {d.recommended_mode}\n\n"
            f"[bold]Example Queries:[/bold]\n" + "\n".join(f"• {q}" for q in d.example_queries),
            title=f"Domain: {d.id}",
            border_style="blue",
        )
    )
