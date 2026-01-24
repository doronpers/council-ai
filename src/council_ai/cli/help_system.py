"""CLI command documentation and help utilities"""

from typing import Dict, List, Optional, TypedDict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class CommandDoc(TypedDict):
    """TypedDict for individual command documentation entries."""

    description: str
    usage: str
    examples: List[str]
    common_options: List[str]
    quick_tips: List[str]


COMMAND_DOCS: Dict[str, CommandDoc] = {
    "consult": {
        "description": "Get advice from the AI council on any topic",
        "usage": "council consult 'Your question or topic'",
        "examples": [
            "council consult 'Should I take this job offer?'",
            "council consult --domain business 'Review our Q1 strategy'",
            "council consult --members ram,grove 'What is your opinion on this design?'",
            "council consult --mode reasoning 'Explain quantum computing'",
        ],
        "common_options": [
            "--domain (-d): Set consultation domain (general, business, technical, creative)",
            "--members (-m): Comma-separated member IDs to consult",
            "--mode: Consultation mode (individual, synthesis, reasoning)",
            "--output (-o): Save results to file",
            "--json: Output as JSON",
            "--context (-c): Provide additional context",
        ],
        "quick_tips": [
            "Use --quick flag for faster consultations with fewer members",
            "Run 'council persona list' to see available members",
            "Use brackets notation: [ram,grove] 'query' to specify members inline",
        ],
    },
    "interactive": {
        "description": "Start an interactive multi-turn consultation session",
        "usage": "council interactive",
        "examples": [
            "council interactive",
            "council interactive --domain coding",
            "council interactive --preset my-team",
        ],
        "common_options": [
            "--domain (-d): Set domain for session",
            "--preset (-p): Load preset settings",
            "/save: Save session to file",
            "/clear: Clear conversation history",
            "/quit: End session",
        ],
        "quick_tips": [
            "Use /help to see available commands",
            "Session is saved automatically",
            "Previous sessions can be reviewed: council history list",
        ],
    },
    "tui": {
        "description": "Launch interactive Terminal User Interface",
        "usage": "council tui",
        "examples": [
            "council tui",
        ],
        "common_options": [],
        "quick_tips": [
            "Full keyboard navigation",
            "Press 'h' for help",
            "Press 'q' to quit",
        ],
    },
    "history": {
        "description": "View and manage consultation history",
        "usage": "council history <subcommand>",
        "examples": [
            "council history list",
            "council history show <id>",
            "council history search 'keyword'",
            "council history delete <id>",
        ],
        "common_options": [
            "list: Show recent consultations",
            "show <id>: Display specific consultation",
            "search <query>: Search consultation history",
            "delete <id>: Remove consultation record",
            "export: Export all history",
        ],
        "quick_tips": [
            "Use history to learn from previous consultations",
            "Sessions are personalized for future consultations",
        ],
    },
    "doctor": {
        "description": "Diagnose configuration and API connectivity issues",
        "usage": "council doctor",
        "examples": [
            "council doctor",
            "council doctor --diagnose",
        ],
        "common_options": [
            "--diagnose (-d): Show detailed API key diagnostics",
        ],
        "quick_tips": [
            "Run after setup to verify everything is configured",
            "Checks all providers for API key availability",
            "Shows network connectivity to API endpoints",
        ],
    },
    "config": {
        "description": "Manage Council AI configuration settings",
        "usage": "council config <subcommand>",
        "examples": [
            "council config show",
            "council config set api.provider anthropic",
            "council config get api.provider",
            "council config preset-save my-team --domain coding",
        ],
        "common_options": [
            "show: Display all settings",
            "set <key> <value>: Set a configuration value",
            "get <key>: Get a configuration value",
            "preset-save <name>: Save current settings as preset",
        ],
        "quick_tips": [
            "Use 'council config set api.api_key YOUR_KEY' to configure API key",
            "Presets help you quickly switch between different setups",
        ],
    },
    "persona": {
        "description": "Manage personas (council members)",
        "usage": "council persona <subcommand>",
        "examples": [
            "council persona list",
            "council persona show dempsey",
            "council persona create",
        ],
        "common_options": [
            "list: Show all available personas",
            "show <id>: Display persona details",
            "create: Create custom persona",
        ],
        "quick_tips": [
            "Customize personas for your needs",
            "Each persona has unique expertise",
        ],
    },
}


def display_command_help(command: str) -> None:
    """Display comprehensive help for a specific command"""
    if command not in COMMAND_DOCS:
        console.print(f"[yellow]No help found for command: {command}[/yellow]")
        console.print("Run 'council --help' to see available commands")
        return

    doc = COMMAND_DOCS[command]

    console.print()
    console.print(
        Panel(
            f"[bold cyan]{command.upper()}[/bold cyan]\n\n" f"{doc['description']}",
            border_style="cyan",
            expand=False,
        )
    )

    # Usage
    console.print("\n[bold]Usage:[/bold]")
    console.print(f"  {doc['usage']}")

    # Examples
    if doc["examples"]:
        console.print("\n[bold]Examples:[/bold]")
        for example in doc["examples"]:
            console.print(f"  $ {example}")

    # Options
    if doc["common_options"]:
        console.print("\n[bold]Common Options:[/bold]")
        for option in doc["common_options"]:
            console.print(f"  • {option}")

    # Tips
    if doc["quick_tips"]:
        console.print("\n[bold]💡 Quick Tips:[/bold]")
        for tip in doc["quick_tips"]:
            console.print(f"  • {tip}")

    console.print()


def display_getting_started() -> None:
    """Display getting started guide"""
    console.print(
        Panel(
            "[bold cyan]🏛️ Council AI - Getting Started[/bold cyan]\n\n"
            "[bold]1. Initial Setup[/bold]\n"
            "   council init              # Guided setup\n\n"
            "[bold]2. Your First Consultation[/bold]\n"
            "   council consult 'Your question here'\n\n"
            "[bold]3. Explore Interactive Mode[/bold]\n"
            "   council interactive       # Multi-turn conversation\n\n"
            "[bold]4. Manage Your Workspace[/bold]\n"
            "   council config show       # View settings\n"
            "   council history list      # View past consultations\n"
            "   council doctor            # Diagnose issues\n\n"
            "[bold]Pro Tips:[/bold]\n"
            "   • Use --domain to focus on specific domains\n"
            "   • Use --preset to save common configurations\n"
            "   • Run 'council help <command>' for detailed help",
            border_style="cyan",
            expand=False,
        )
    )


def display_available_commands() -> None:
    """Display table of available commands"""
    table = Table(title="Council AI Commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="green")
    table.add_column("Description")
    table.add_column("Usage", style="dim")

    for command, doc in COMMAND_DOCS.items():
        table.add_row(
            command,
            doc["description"],
            doc["usage"].split()[0],  # First part of usage
        )

    console.print("\n")
    console.print(table)
    console.print("\nRun [bold]council help <command>[/bold] for detailed information")


def suggest_command(query: str) -> Optional[str]:
    """Suggest a command based on user query"""
    query_lower = query.lower()

    # Simple fuzzy matching
    suggestions = {
        "ask": "consult",
        "advice": "consult",
        "question": "consult",
        "talk": "interactive",
        "chat": "interactive",
        "conversation": "interactive",
        "history": "history",
        "past": "history",
        "previous": "history",
        "error": "doctor",
        "problem": "doctor",
        "diagnose": "doctor",
        "setup": "init",
        "configure": "config",
        "settings": "config",
        "member": "persona",
        "character": "persona",
    }

    for keyword, command in suggestions.items():
        if keyword in query_lower:
            return command

    return None
