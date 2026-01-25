import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..core.persona import Persona, PersonaCategory, PersonaManager, get_persona, list_personas

console = Console()


@click.group()
def persona():
    """Manage council personas."""
    pass


@persona.command("list")
@click.option(
    "--category",
    "-c",
    type=click.Choice(["advisory", "adversarial", "custom"]),
    help="Filter by category",
)
def persona_list(category):
    """List available personas."""
    cat = PersonaCategory(category) if category else None
    personas = list_personas(cat)

    table = Table(title="Available Personas")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Focus Areas")

    for p in personas:
        table.add_row(
            p.id,
            f"{p.emoji} {p.name}",
            p.title,
            p.category.value,
            ", ".join(p.focus_areas[:3]) + ("..." if len(p.focus_areas) > 3 else ""),
        )

    console.print(table)


@persona.command("show")
@click.argument("persona_id")
def persona_show(persona_id):
    """Show details of a persona."""
    try:
        p = get_persona(persona_id)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold]{p.emoji} {p.name}[/bold]\n"
            f"[dim]{p.title}[/dim]\n\n"
            f'[bold]Core Question:[/bold]\n"{p.core_question}"\n\n'
            f'[bold]Razor:[/bold]\n"{p.razor}"\n\n'
            f"[bold]Focus Areas:[/bold]\n{', '.join(p.focus_areas)}\n\n"
            f"[bold]Traits:[/bold]\n" + "\n".join(f"• {t.name}: {t.description}" for t in p.traits),
            title=f"Persona: {p.id}",
            border_style="blue",
        )
    )


@persona.command("create")
@click.option("--interactive", "-i", is_flag=True, help="Interactive creation wizard")
@click.option("--from-file", type=click.Path(exists=True), help="Create from YAML file")
def persona_create(interactive, from_file):
    """Create a new persona."""
    if from_file:
        p = Persona.from_yaml_file(from_file)
        manager = PersonaManager()
        manager.add(p)
        manager.save_persona(p.id)
        console.print(f"[green]✓[/green] Created persona '{p.id}' from {from_file}")
        return

    if not interactive:
        console.print("Use --interactive or --from-file to create a persona")
        return

    # Interactive creation
    console.print(Panel("[bold]Create New Persona[/bold]", border_style="green"))

    id = Prompt.ask("ID (lowercase, no spaces)")
    name = Prompt.ask("Name")
    title = Prompt.ask("Title")
    emoji = Prompt.ask("Emoji", default="👤")
    core_question = Prompt.ask("Core Question (the fundamental question this persona asks)")
    razor = Prompt.ask("Razor (their decision-making principle)")

    category = Prompt.ask(
        "Category", choices=["advisory", "adversarial", "custom"], default="custom"
    )

    focus_areas = Prompt.ask("Focus Areas (comma-separated)").split(",")
    focus_areas = [f.strip() for f in focus_areas if f.strip()]

    p = Persona(
        id=id,
        name=name,
        title=title,
        emoji=emoji,
        core_question=core_question,
        razor=razor,
        category=PersonaCategory(category),
        focus_areas=focus_areas,
    )

    # Add traits
    if Confirm.ask("Add traits?"):
        while True:
            trait_name = Prompt.ask("Trait name (empty to finish)")
            if not trait_name:
                break
            trait_desc = Prompt.ask("Trait description")
            p.add_trait(trait_name, trait_desc)

    # Save
    manager = PersonaManager()
    manager.add(p)
    path = manager.save_persona(p.id)

    console.print(f"[green]✓[/green] Created persona '{p.id}'")
    console.print(f"[dim]Saved to: {path}[/dim]")


@persona.command("edit")
@click.argument("persona_id")
@click.option("--weight", type=float, help="Set weight (0.0-2.0)")
@click.option("--add-trait", nargs=2, multiple=True, help="Add trait: name description")
@click.option("--remove-trait", multiple=True, help="Remove trait by name")
def persona_edit(persona_id, weight, add_trait, remove_trait):
    """Edit an existing persona."""
    manager = PersonaManager()
    p = manager.get_or_raise(persona_id)

    if weight is not None:
        p.weight = weight
        console.print(f"[green]✓[/green] Set weight to {weight}")

    for name, desc in add_trait:
        p.add_trait(name, desc)
        console.print(f"[green]✓[/green] Added trait '{name}'")

    for name in remove_trait:
        p.remove_trait(name)
        console.print(f"[green]✓[/green] Removed trait '{name}'")

    manager.save_persona(persona_id)
    console.print("[dim]Saved changes[/dim]")
