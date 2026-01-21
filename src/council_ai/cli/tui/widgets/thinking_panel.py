"""Thinking panel widget for TUI."""

from textual.widgets import Static


class ThinkingPanel(Static):
    """Panel displaying thinking/reasoning process."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thinking_content: dict = {}
        self.update_display()

    def update_display(self) -> None:
        """Update the thinking display."""
        if not self._thinking_content:
            self.update("")
            return

        lines = []
        for persona_id, thinking in self._thinking_content.items():
            if thinking:
                # Show first 200 chars of thinking
                preview = thinking[:200] + "..." if len(thinking) > 200 else thinking
                lines.append(f"[dim cyan]💭 {persona_id} (thinking...)[/dim cyan]")
                lines.append(f"[dim]{preview}[/dim]")

        self.update("\n".join(lines) if lines else "")

    def clear_persona(self, persona_id: str) -> None:
        """Clear thinking for a specific persona."""
        if persona_id in self._thinking_content:
            del self._thinking_content[persona_id]
            self.update_display()

    def set_thinking(self, persona_id: str, content: str) -> None:
        """Set thinking content for a persona."""
        self._thinking_content[persona_id] = content
        self.update_display()

    @property
    def thinking_content(self) -> dict:
        """Get thinking content."""
        return self._thinking_content

    @thinking_content.setter
    def thinking_content(self, value: dict) -> None:
        """Set thinking content."""
        self._thinking_content = value
        self.update_display()
