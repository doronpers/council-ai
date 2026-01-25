"""Quickstart command."""

import subprocess
import sys
from pathlib import Path

import click

from ..utils import console


@click.command()
def quickstart():
    """
    Run an interactive quickstart demo (no API key required).

    Explore Council AI features and see examples without needing an API key.
    """
    # Assuming the current file structure is src/council_ai/cli/commands/misc.py
    # We need to find examples/quickstart.py in the root

    # Go up 4 levels: commands -> cli -> council_ai -> src -> root
    root_path = Path(__file__).parent.parent.parent.parent.parent
    quickstart_path = root_path / "examples" / "quickstart.py"

    if not quickstart_path.exists():
        # Maybe installed package
        # Try finding via site-packages structure or relative to package root
        # If in site-packages/council_ai/cli/commands/misc.py
        # examples might be in sys.prefix/share/council-ai/examples/quickstart.py or similar
        # For dev environment relative path is usually reliable
        pass

    if quickstart_path.exists():
        try:
            subprocess.run([sys.executable, str(quickstart_path)], check=True)
        except subprocess.CalledProcessError:
            console.print("[red]Error:[/red] Failed to run quickstart demo")
            sys.exit(1)
    else:
        # Fallback to searching relative to council_ai package
        import council_ai

        pkg_path = Path(council_ai.__file__).parent.parent.parent
        quickstart_path = pkg_path / "examples" / "quickstart.py"

        if quickstart_path.exists():
            try:
                subprocess.run([sys.executable, str(quickstart_path)], check=True)
                return
            except subprocess.CalledProcessError:
                console.print("[red]Error:[/red] Failed to run quickstart demo")
                sys.exit(1)

        console.print(
            "[yellow]Quickstart demo not found.[/yellow]\n\n"
            "You can view personas and domains with:\n"
            "  council persona list\n"
            "  council domain list\n"
        )
