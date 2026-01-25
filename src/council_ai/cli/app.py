"""Main CLI entry point."""

import click

from ..core.config import ConfigManager


@click.group()
@click.version_option(version="2.0.0", prog_name="council-ai")
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.pass_context
def main(ctx, config):
    r"""
    🏛️ Council AI - Intelligent Advisory Council System

    Get advice from a council of AI-powered personas with diverse
    perspectives and expertise.

    \b
    First Time Setup:
      council init              # Guided setup wizard
      council quickstart        # Explore features (no API key needed)

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
    Configuration & Presets:
      council config set api.provider anthropic
      council config preset-save my-team --domain coding
      council consult --preset my-team "Review this code"
    """
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["config_manager"] = ConfigManager(config)


def register_commands():
    # Import commands inside function to avoid circular imports and enable lazy loading effects
    # Existing modular commands - we assume these are still in their original locations
    # or moved to the new structure. For now, we import them from original locations
    # if they haven't been moved, OR we will refactor them too.
    # The plan said "Extract config.py commands", so we should treat them as external subcommands.
    from .commands import (
        consult_command,
        cost_group,
        doctor_command,
        history_group,
        init_command,
        interactive_command,
        q_command,
        qa_command,
        quickstart_command,
        review_command,
        show_providers_command,
        test_key_command,
        tui_command,
        ui_command,
        web_command,
    )
    from .commands.session_report import session as session_group
    from .config import config as config_cmd
    from .domain import domain as domain_cmd
    from .persona import persona as persona_cmd

    # Core commands
    main.add_command(init_command)
    main.add_command(quickstart_command)
    main.add_command(consult_command)
    main.add_command(qa_command)
    main.add_command(q_command)
    main.add_command(interactive_command)
    main.add_command(tui_command)

    # Subgroups / specialized commands
    main.add_command(history_group)
    main.add_command(review_command)
    main.add_command(web_command)
    main.add_command(ui_command)
    main.add_command(cost_group)
    main.add_command(doctor_command)
    main.add_command(show_providers_command)
    main.add_command(test_key_command)
    main.add_command(session_group)

    # External modules
    main.add_command(config_cmd)
    main.add_command(domain_cmd)
    main.add_command(persona_cmd)

    # Personal integration
    try:
        from .personal import personal

        main.add_command(personal)
    except ImportError:
        pass


register_commands()
