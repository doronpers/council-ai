"""
Council AI - Command Line Interface

A comprehensive CLI for interacting with the Council AI system.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import Council, get_persona, list_personas, get_domain, list_domains
from .core.persona import PersonaCategory, PersonaManager, Persona
from .core.config import load_config, save_config, ConfigManager, get_api_key
from .providers import list_providers

console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# Main CLI Group
# ═══════════════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(version="1.0.0", prog_name="council-ai")
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.pass_context
def main(ctx, config):
    """
    🏛️ Council AI - Intelligent Advisory Council System
    
    Get advice from a council of AI-powered personas with diverse
    perspectives and expertise.
    
    \b
    Quick Start:
      council consult "Should I take this job offer?"
      council consult --domain business "Review our Q1 strategy"
      council interactive
    
    \b
    Manage Personas:
      council persona list
      council persona show rams
      council persona create
    
    \b
    Configuration:
      council config set api.provider anthropic
      council config set api.api_key YOUR_KEY
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["config_manager"] = ConfigManager(config)


# ═══════════════════════════════════════════════════════════════════════════════
# Consult Command
# ═══════════════════════════════════════════════════════════════════════════════

@main.command()
@click.argument("query")
@click.option("--domain", "-d", default="general", help="Domain preset to use")
@click.option("--members", "-m", multiple=True, help="Specific personas to consult")
@click.option("--provider", "-p", help="LLM provider (anthropic, openai)")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key for provider")
@click.option("--context", "-ctx", help="Additional context for the query")
@click.option("--mode", type=click.Choice(["individual", "synthesis", "debate", "vote"]), 
              default="synthesis", help="Consultation mode")
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def consult(ctx, query, domain, members, provider, api_key, context, mode, output, output_json):
    """
    Consult the council on a query.
    
    \b
    Examples:
      council consult "Should we refactor this module?"
      council consult --domain startup "Is this the right time to raise?"
      council consult --members rams --members kahneman "Review this design"
    """
    config_manager = ctx.obj["config_manager"]
    
    # Get API key
    api_key = api_key or get_api_key(provider or config_manager.get("api.provider", "anthropic"))
    if not api_key:
        console.print("[red]Error:[/red] No API key provided.")
        console.print("Set via --api-key, COUNCIL_API_KEY env var, or 'council config set api.api_key'")
        sys.exit(1)
    
    # Create council
    provider = provider or config_manager.get("api.provider", "anthropic")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Assembling council...", total=None)
        
        if members:
            council = Council(api_key=api_key, provider=provider)
            for member_id in members:
                try:
                    council.add_member(member_id)
                except ValueError as e:
                    console.print(f"[yellow]Warning:[/yellow] {e}")
        else:
            council = Council.for_domain(domain, api_key=api_key, provider=provider)
        
        progress.update(progress.task_ids[0], description="Consulting council...")
        
        try:
            result = council.consult(query, context=context)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)
    
    # Output
    if output_json:
        import json
        output_text = json.dumps(result.to_dict(), indent=2)
    else:
        output_text = result.to_markdown()
    
    if output:
        Path(output).write_text(output_text)
        console.print(f"[green]✓[/green] Output saved to {output}")
    else:
        console.print()
        console.print(Markdown(output_text))


# ═══════════════════════════════════════════════════════════════════════════════
# Interactive Mode
# ═══════════════════════════════════════════════════════════════════════════════

@main.command()
@click.option("--domain", "-d", default="general", help="Domain preset to use")
@click.option("--provider", "-p", help="LLM provider")
@click.option("--api-key", "-k", envvar="COUNCIL_API_KEY", help="API key")
@click.pass_context
def interactive(ctx, domain, provider, api_key):
    """
    Start an interactive council session.
    
    Have a multi-turn conversation with your council.
    """
    config_manager = ctx.obj["config_manager"]
    
    api_key = api_key or get_api_key(provider or config_manager.get("api.provider", "anthropic"))
    if not api_key:
        console.print("[red]Error:[/red] No API key provided.")
        sys.exit(1)
    
    provider = provider or config_manager.get("api.provider", "anthropic")
    council = Council.for_domain(domain, api_key=api_key, provider=provider)
    
    console.print(Panel(
        f"[bold]🏛️ Council AI Interactive Session[/bold]\n\n"
        f"Domain: {domain}\n"
        f"Members: {', '.join(m.name for m in council.list_members())}\n\n"
        f"Commands:\n"
        f"  /members - List current members\n"
        f"  /add <id> - Add a member\n"
        f"  /remove <id> - Remove a member\n"
        f"  /domain <name> - Switch domain\n"
        f"  /mode <mode> - Change consultation mode\n"
        f"  /quit - Exit session",
        title="Welcome",
        border_style="blue"
    ))
    
    while True:
        try:
            query = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if not query.strip():
                continue
            
            # Handle commands
            if query.startswith("/"):
                parts = query[1:].split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None
                
                if cmd == "quit" or cmd == "exit":
                    console.print("[dim]Goodbye![/dim]")
                    break
                elif cmd == "members":
                    _show_members(council)
                elif cmd == "add" and arg:
                    try:
                        council.add_member(arg)
                        console.print(f"[green]✓[/green] Added {arg}")
                    except ValueError as e:
                        console.print(f"[red]Error:[/red] {e}")
                elif cmd == "remove" and arg:
                    council.remove_member(arg)
                    console.print(f"[green]✓[/green] Removed {arg}")
                elif cmd == "domain" and arg:
                    council = Council.for_domain(arg, api_key=api_key, provider=provider)
                    console.print(f"[green]✓[/green] Switched to {arg} domain")
                elif cmd == "mode" and arg:
                    from .core.council import ConsultationMode
                    council.config.mode = ConsultationMode(arg)
                    console.print(f"[green]✓[/green] Mode set to {arg}")
                else:
                    console.print("[yellow]Unknown command[/yellow]")
                continue
            
            # Consult
            with console.status("Consulting council..."):
                result = council.consult(query)
            
            console.print()
            console.print(Markdown(result.to_markdown()))
            
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def _show_members(council):
    """Display current council members."""
    table = Table(title="Council Members")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Title")
    table.add_column("Weight")
    table.add_column("Enabled")
    
    for m in council.list_members():
        table.add_row(
            m.id,
            f"{m.emoji} {m.name}",
            m.title,
            f"{m.weight:.1f}",
            "✓" if m.enabled else "✗"
        )
    
    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# Persona Commands
# ═══════════════════════════════════════════════════════════════════════════════

@main.group()
def persona():
    """Manage council personas."""
    pass


@persona.command("list")
@click.option("--category", "-c", type=click.Choice(["advisory", "adversarial", "custom"]),
              help="Filter by category")
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
            ", ".join(p.focus_areas[:3]) + ("..." if len(p.focus_areas) > 3 else "")
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
    
    console.print(Panel(
        f"[bold]{p.emoji} {p.name}[/bold]\n"
        f"[dim]{p.title}[/dim]\n\n"
        f"[bold]Core Question:[/bold]\n\"{p.core_question}\"\n\n"
        f"[bold]Razor:[/bold]\n\"{p.razor}\"\n\n"
        f"[bold]Focus Areas:[/bold]\n{', '.join(p.focus_areas)}\n\n"
        f"[bold]Traits:[/bold]\n" + "\n".join(f"• {t.name}: {t.description}" for t in p.traits),
        title=f"Persona: {p.id}",
        border_style="blue"
    ))


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
        "Category",
        choices=["advisory", "adversarial", "custom"],
        default="custom"
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
    console.print(f"[dim]Saved changes[/dim]")


# ═══════════════════════════════════════════════════════════════════════════════
# Domain Commands
# ═══════════════════════════════════════════════════════════════════════════════

@main.group()
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
            ", ".join(d.default_personas[:4]) + ("..." if len(d.default_personas) > 4 else "")
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
    
    console.print(Panel(
        f"[bold]{d.name}[/bold]\n"
        f"[dim]{d.description}[/dim]\n\n"
        f"[bold]Category:[/bold] {d.category.value}\n\n"
        f"[bold]Default Personas:[/bold]\n{', '.join(d.default_personas)}\n\n"
        f"[bold]Optional Personas:[/bold]\n{', '.join(d.optional_personas) or 'None'}\n\n"
        f"[bold]Recommended Mode:[/bold] {d.recommended_mode}\n\n"
        f"[bold]Example Queries:[/bold]\n" + "\n".join(f"• {q}" for q in d.example_queries),
        title=f"Domain: {d.id}",
        border_style="blue"
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# Config Commands
# ═══════════════════════════════════════════════════════════════════════════════

@main.group()
def config():
    """Manage configuration."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    config_manager = ctx.obj["config_manager"]
    cfg = config_manager.config
    
    console.print(Panel(
        f"[bold]API Settings[/bold]\n"
        f"  Provider: {cfg.api.provider}\n"
        f"  API Key: {'[set]' if cfg.api.api_key else '[not set]'}\n"
        f"  Model: {cfg.api.model or '[default]'}\n\n"
        f"[bold]Defaults[/bold]\n"
        f"  Mode: {cfg.default_mode}\n"
        f"  Domain: {cfg.default_domain}\n"
        f"  Temperature: {cfg.temperature}\n"
        f"  Max Tokens: {cfg.max_tokens_per_response}\n\n"
        f"[bold]Paths[/bold]\n"
        f"  Config: {config_manager.path}\n"
        f"  Custom Personas: {cfg.custom_personas_path or '[default]'}",
        title="Configuration",
        border_style="blue"
    ))


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx, key, value):
    """Set a configuration value."""
    config_manager = ctx.obj["config_manager"]
    
    # Type conversion
    if value.lower() in ("true", "false"):
        value = value.lower() == "true"
    elif value.isdigit():
        value = int(value)
    elif value.replace(".", "").isdigit():
        value = float(value)
    
    try:
        config_manager.set(key, value)
        config_manager.save()
        console.print(f"[green]✓[/green] Set {key} = {value}")
    except KeyError as e:
        console.print(f"[red]Error:[/red] Invalid key: {key}")


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx, key):
    """Get a configuration value."""
    config_manager = ctx.obj["config_manager"]
    value = config_manager.get(key)
    
    if value is None:
        console.print(f"[yellow]{key} is not set[/yellow]")
    else:
        console.print(f"{key} = {value}")


# ═══════════════════════════════════════════════════════════════════════════════
# Provider Commands
# ═══════════════════════════════════════════════════════════════════════════════

@main.command("providers")
def show_providers():
    """List available LLM providers."""
    providers = list_providers()
    
    table = Table(title="Available LLM Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Env Variable")
    table.add_column("Status")
    
    for name in providers:
        env_var = f"{name.upper()}_API_KEY"
        has_key = bool(os.environ.get(env_var) or os.environ.get("COUNCIL_API_KEY"))
        status = "[green]✓ Configured[/green]" if has_key else "[dim]Not configured[/dim]"
        table.add_row(name, env_var, status)
    
    console.print(table)
    console.print("\n[dim]Set API key via environment variable or 'council config set api.api_key'[/dim]")


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
