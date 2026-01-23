"""
TUI Keyboard Shortcuts and Keybindings

Centralizes keyboard navigation and command bindings for the TUI.
"""

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from rich.console import Console

console = Console()


@dataclass
class KeyBinding:
    """Represents a keyboard binding"""

    key: str
    description: str
    action: str
    category: str  # navigation, editing, session, etc.


class KeyboardShortcutManager:
    """Manages keyboard shortcuts and keybindings"""

    # Default keybindings
    DEFAULT_BINDINGS: Dict[str, KeyBinding] = {
        # Navigation
        "tab": KeyBinding("Tab", "Move to next section", "focus_next", "navigation"),
        "shift+tab": KeyBinding(
            "Shift+Tab", "Move to previous section", "focus_previous", "navigation"
        ),
        "up": KeyBinding("↑", "Scroll up in focused section", "scroll_up", "navigation"),
        "down": KeyBinding("↓", "Scroll down in focused section", "scroll_down", "navigation"),
        "pageup": KeyBinding("Page Up", "Page up in focused section", "page_up", "navigation"),
        "pagedown": KeyBinding(
            "Page Down", "Page down in focused section", "page_down", "navigation"
        ),
        "home": KeyBinding("Home", "Jump to top of section", "scroll_to_top", "navigation"),
        "end": KeyBinding("End", "Jump to bottom of section", "scroll_to_bottom", "navigation"),
        "ctrl+home": KeyBinding(
            "Ctrl+Home", "Jump to first section", "jump_to_first", "navigation"
        ),
        "ctrl+end": KeyBinding("Ctrl+End", "Jump to last section", "jump_to_last", "navigation"),
        # Editing
        "ctrl+a": KeyBinding("Ctrl+A", "Select all in input", "select_all", "editing"),
        "ctrl+x": KeyBinding("Ctrl+X", "Cut from input", "cut", "editing"),
        "ctrl+c": KeyBinding("Ctrl+C", "Copy selected", "copy", "editing"),
        "ctrl+v": KeyBinding("Ctrl+V", "Paste to input", "paste", "editing"),
        "ctrl+z": KeyBinding("Ctrl+Z", "Undo last action", "undo", "editing"),
        # Session Control
        "enter": KeyBinding("Enter", "Submit query to council", "submit_query", "session"),
        "ctrl+l": KeyBinding("Ctrl+L", "Clear consultation view", "clear_view", "session"),
        "ctrl+s": KeyBinding("Ctrl+S", "Save session", "save_session", "session"),
        "ctrl+e": KeyBinding("Ctrl+E", "Export session", "export_session", "session"),
        "ctrl+p": KeyBinding("Ctrl+P", "Show member list", "show_members", "session"),
        # Help and Info
        "f1": KeyBinding("F1", "Show help", "show_help", "help"),
        "?": KeyBinding("?", "Show shortcuts", "show_shortcuts", "help"),
        "f2": KeyBinding("F2", "Show status", "show_status", "help"),
        # Exit
        "q": KeyBinding("q", "Quit application", "quit", "exit"),
        "ctrl+q": KeyBinding("Ctrl+Q", "Force quit", "force_quit", "exit"),
        "escape": KeyBinding("Esc", "Cancel current operation", "cancel", "exit"),
    }

    def __init__(self):
        """Initialize keyboard shortcut manager"""
        self.bindings: Dict[str, KeyBinding] = self.DEFAULT_BINDINGS.copy()
        self.handlers: Dict[str, Callable] = {}

    def register_handler(self, action: str, handler: Callable) -> None:
        """Register handler for action"""
        self.handlers[action] = handler

    def trigger_action(self, key: str) -> bool:
        """Trigger action for key if handler registered"""
        if key not in self.bindings:
            return False

        binding = self.bindings[key]
        if binding.action in self.handlers:
            try:
                self.handlers[binding.action]()
                return True
            except Exception as e:
                console.print(f"[red]Error executing action: {e}[/red]")
                return False

        return False

    def get_binding(self, key: str) -> Optional[KeyBinding]:
        """Get binding for key"""
        return self.bindings.get(key)

    def get_bindings_by_category(self, category: str) -> Dict[str, KeyBinding]:
        """Get all bindings in category"""
        return {k: v for k, v in self.bindings.items() if v.category == category}

    def display_shortcuts(self) -> None:
        """Display all keyboard shortcuts"""
        from rich.table import Table

        table = Table(title="⌨️ Keyboard Shortcuts", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="green")
        table.add_column("Description")
        table.add_column("Category", style="yellow")

        # Group by category
        categories = {}
        for key, binding in self.bindings.items():
            cat = binding.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, binding))

        # Sort and display
        for category in sorted(categories.keys()):
            for key, binding in sorted(categories[category], key=lambda x: x[0]):
                table.add_row(
                    f"[bold]{binding.key}[/bold]",
                    binding.description,
                    category.capitalize(),
                )

        console.print()
        console.print(table)
        console.print()


class NavigationHints:
    """Displays contextual navigation hints"""

    @staticmethod
    def display_basic_hints() -> str:
        """Display basic navigation hints"""
        return (
            "[dim]Navigation: "
            "[green]Tab[/green]=Next section | "
            "[green]↑↓[/green]=Scroll | "
            "[green]Enter[/green]=Submit | "
            "[green]?[/green]=Help | "
            "[green]q[/green]=Quit[/dim]"
        )

    @staticmethod
    def display_section_hints() -> str:
        """Display hints for scrollable section"""
        return (
            "[dim]Section: "
            "[green]↑↓[/green]=Scroll | "
            "[green]Home/End[/green]=Jump | "
            "[green]PgUp/PgDn[/green]=Page | "
            "[green]Tab[/green]=Next[/dim]"
        )

    @staticmethod
    def display_input_hints() -> str:
        """Display hints for input field"""
        return (
            "[dim]Input: "
            "[green]Ctrl+A[/green]=Select | "
            "[green]Ctrl+X/C/V[/green]=Cut/Copy/Paste | "
            "[green]Enter[/green]=Submit[/dim]"
        )


class HelpPanel:
    """Generates help content for display"""

    @staticmethod
    def get_quick_start_help() -> str:
        """Get quick start help text"""
        return """
[bold cyan]🏛️ Council AI - TUI Quick Start[/bold cyan]

[bold]Input Section[/bold]
  • Type your question or topic
  • Press [green]Enter[/green] to consult the council
  • Use [green]Ctrl+A[/green] to select all text

[bold]Consultation Sections[/bold]
  • [yellow]💭 Thinking[/yellow]: Shows reasoning process (when reasoning mode enabled)
  • [accent]📝 Responses[/accent]: Individual member responses
  • [info]📚 History[/info]: Previous consultations in this session

[bold]Navigation[/bold]
  • Press [green]Tab[/green] to move between sections
  • Use [green]Arrow Keys[/green] to scroll within sections
  • [green]Home/End[/green] jump to top/bottom
  • [green]PgUp/PgDn[/green] for full-page scrolling

[bold]Commands[/bold]
  • [green]Ctrl+L[/green]: Clear view
  • [green]Ctrl+S[/green]: Save session
  • [green]Ctrl+E[/green]: Export session
  • [green]Ctrl+P[/green]: Show members
  • [green]?[/green]: Show all shortcuts
  • [green]q[/green]: Quit

[bold]Shortcuts[/bold]
  • [green]F1[/green]: Help
  • [green]F2[/green]: Status
  • [green]Ctrl+Home[/green]: First section
  • [green]Ctrl+End[/green]: Last section
"""

    @staticmethod
    def get_advanced_help() -> str:
        """Get advanced tips"""
        return """
[bold cyan]💡 Advanced Tips[/bold cyan]

[bold]Performance[/bold]
  • Longer consultations may require scrolling
  • Use Ctrl+L to clear and start fresh
  • Export sessions to free up memory

[bold]Content Management[/bold]
  • Sessions are auto-saved
  • Use Ctrl+E to export for sharing
  • History persists across the session

[bold]Keyboard Masters[/bold]
  • Tab through sections efficiently
  • Combine Ctrl+Home/End for quick navigation
  • Shift+Tab for reverse navigation

[bold]Tips[/bold]
  • Simpler queries respond faster
  • Use Ctrl+P to see available members
  • Clear view (Ctrl+L) between different topics
"""
