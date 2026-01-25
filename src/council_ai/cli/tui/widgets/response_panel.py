"""Response panel widget for TUI."""

from textual.widgets import Static


class ResponsePanel(Static):
    """Panel displaying streaming responses."""

    _responses: dict = {}
    _synthesis: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_display()

    def update_display(self) -> None:
        """Update the response display."""
        lines = []
        for persona_name, response in self._responses.items():
            if response:
                # Truncate long responses for display
                display_response = response[:500] + "..." if len(response) > 500 else response
                lines.append(f"[bold]{persona_name}:[/bold] {display_response}")

        if self._synthesis:
            lines.append("")
            lines.append("[bold cyan]Synthesis:[/bold cyan]")
            display_synthesis = (
                self._synthesis[:500] + "..." if len(self._synthesis) > 500 else self._synthesis
            )
            lines.append(display_synthesis)

        content = "\n".join(lines) if lines else "[dim]Waiting for responses...[/dim]"
        self.update(content)

    def add_response_chunk(self, persona_name: str, chunk: str) -> None:
        """Add a response chunk for a persona."""
        if persona_name not in self._responses:
            self._responses[persona_name] = ""
        self._responses[persona_name] += chunk
        self.update_display()

    def set_response(self, persona_id: str, content: str) -> None:
        """Set full response for a persona."""
        self._responses[persona_id] = content
        self.update_display()

    def set_synthesis(self, synthesis: str) -> None:
        """Set synthesis content."""
        self._synthesis = synthesis
        self.update_display()

    def add_synthesis_chunk(self, chunk: str) -> None:
        """Add a synthesis chunk."""
        self._synthesis += chunk
        self.update_display()

    def clear(self) -> None:
        """Clear all responses."""
        self._responses = {}
        self._synthesis = ""
        self.update_display()
