import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def config():
    """Manage configuration."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    config_manager = ctx.obj["config_manager"]
    cfg = config_manager.config

    console.print(
        Panel(
            f"[bold]API Settings[/bold]\n"
            f"  Provider: {cfg.api.provider}\n"
            f"  API Key: {'[set]' if cfg.api.api_key else '[not set]'}\n"
            f"  Model: {cfg.api.model or '[default]'}\n"
            f"  Base URL: {cfg.api.base_url or '[default]'}\n\n"
            f"[bold]Defaults[/bold]\n"
            f"  Mode: {cfg.default_mode}\n"
            f"  Domain: {cfg.default_domain}\n"
            f"  Temperature: {cfg.temperature}\n"
            f"  Max Tokens: {cfg.max_tokens_per_response}\n"
            f"  Synthesis Provider: {cfg.synthesis_provider or '[default]'}\n"
            f"  Synthesis Model: {cfg.synthesis_model or '[default]'}\n"
            f"  Synthesis Max Tokens: {cfg.synthesis_max_tokens or '[default]'}\n\n"
            f"[bold]Paths[/bold]\n"
            f"  Config: {config_manager.path}\n"
            f"  Custom Personas: {cfg.custom_personas_path or '[default]'}\n"
            f"  Custom Domains: {cfg.custom_domains_path or '[default]'}",
            title="Configuration",
            border_style="blue",
        )
    )


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
    except KeyError:
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


@config.command("preset-save")
@click.argument("preset_name")
@click.option("--domain", "-d", help="Domain to save in preset")
@click.option("--members", "-m", help="Comma-separated member IDs")
@click.option("--mode", help="Consultation mode")
@click.pass_context
def config_preset_save(ctx, preset_name, domain, members, mode):
    """Save current or specified settings as a preset."""
    config_manager = ctx.obj["config_manager"]

    preset = {}

    if domain:
        preset["domain"] = domain
    else:
        preset["domain"] = config_manager.get("default_domain")

    if members:
        preset["members"] = [m.strip() for m in members.split(",")]

    if mode:
        preset["mode"] = mode
    else:
        preset["mode"] = config_manager.get("default_mode")

    # Save to presets
    if not isinstance(config_manager.config.presets, dict):
        config_manager.config.presets = {}

    config_manager.config.presets[preset_name] = preset
    config_manager.save()

    console.print(f"[green]✓[/green] Preset '{preset_name}' saved")
    console.print(f"[dim]Use with: council consult --preset {preset_name}[/dim]")


@config.command("preset-list")
@click.pass_context
def config_preset_list(ctx):
    """List saved presets."""
    config_manager = ctx.obj["config_manager"]
    presets = config_manager.config.presets

    if not presets:
        console.print("[dim]No presets saved.[/dim]")
        console.print("[dim]Create one with: council config preset-save <name>[/dim]")
        return

    table = Table(title="Saved Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Domain")
    table.add_column("Mode")
    table.add_column("Members")

    for name, preset in presets.items():
        members = (
            ", ".join(preset.get("members", [])) if preset.get("members") else "[domain default]"
        )
        table.add_row(
            name,
            preset.get("domain", "general"),
            preset.get("mode", "synthesis"),
            members,
        )

    console.print(table)


@config.command("preset-delete")
@click.argument("preset_name")
@click.pass_context
def config_preset_delete(ctx, preset_name):
    """Delete a saved preset."""
    config_manager = ctx.obj["config_manager"]

    if preset_name in config_manager.config.presets:
        del config_manager.config.presets[preset_name]
        config_manager.save()
        console.print(f"[green]✓[/green] Preset '{preset_name}' deleted")
    else:
        console.print(f"[red]Error:[/red] Preset '{preset_name}' not found")
