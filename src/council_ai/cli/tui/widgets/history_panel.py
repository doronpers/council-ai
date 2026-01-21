"""History panel widget for TUI."""

from textual.widgets import Static


class HistoryPanel(Static):
    """Panel displaying conversation history."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: list = []
        self.update_display()

    def update_display(self) -> None:
        """Update the history display."""
        if not self._history:
            self.update("[dim]No questions yet...[/dim]")
            return

        lines = []
        for entry in self._history[-10:]:  # Show last 10 entries
            question = entry.get("question", "")
            synthesis = entry.get("synthesis", "")
            if question:
                display_q = question[:60] + "..." if len(question) > 60 else question
                lines.append(f"[bold cyan]Q:[/bold cyan] {display_q}")
            if synthesis:
                display_a = synthesis[:80] + "..." if len(synthesis) > 80 else synthesis
                lines.append(f"[dim]A:[/dim] {display_a}")
            lines.append("")

        self.update("\n".join(lines))

    def add_entry(self, question: str, synthesis: str = "") -> None:
        """Add a new history entry."""
        self._history.append({"question": question, "synthesis": synthesis})
        # Keep last 50 entries
        self._history = self._history[-50:]
        self.update_display()

    @property
    def history(self) -> list:
        """Get history."""
        return self._history

    @history.setter
    def history(self, value: list) -> None:
        """Set history."""
        self._history = value
        self.update_display()
