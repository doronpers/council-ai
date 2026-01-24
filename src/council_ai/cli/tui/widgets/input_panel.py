"""Input panel widget for TUI with history support."""

from pathlib import Path
from typing import cast

from textual.message import Message
from textual.widgets import Input


class InputPanel(Input):
    """Input widget with command history support."""

    class Submitted(Message):
        """Message sent when input is submitted."""

        value: str

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: list[str] = []
        self._history_index = -1
        # Use workspace-relative path
        from ..utils.paths import get_workspace_config_dir

        self._history_file = get_workspace_config_dir("council-ai") / "history.txt"
        self._load_history()

    def _load_history(self) -> None:
        """Load history from file."""
        if self._history_file.exists():
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    self._history = [line.strip() for line in f.readlines() if line.strip()]
                    # Keep last 1000 entries
                    self._history = self._history[-1000:]
            except Exception:
                self._history = []

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_file, "w", encoding="utf-8") as f:
                for entry in self._history[-1000:]:  # Keep last 1000
                    f.write(f"{entry}\n")
        except Exception:
            pass  # Silently fail if can't save

    def on_key(self, event) -> None:
        """Handle keyboard input."""
        if event.key == "up":
            self._navigate_history(-1)
            event.prevent_default()
            event.stop()
        elif event.key == "down":
            self._navigate_history(1)
            event.prevent_default()
            event.stop()
        elif event.key == "enter":
            input_text: str = self.value.strip()  # type: ignore[has-type]
            if input_text:
                # Add to history if not duplicate
                if not self._history or self._history[-1] != input_text:
                    self._history.append(input_text)
                self._history_index = -1
                self._save_history()
                self.post_message(self.Submitted(input_text))
                self.value = ""
            event.prevent_default()
            event.stop()
        # For other keys, let the Input widget handle them naturally

    def _navigate_history(self, direction: int) -> None:
        """Navigate through history."""
        if not self._history:
            return

        self._history_index += direction

        # Clamp index
        if self._history_index < -len(self._history):
            self._history_index = -len(self._history)
        elif self._history_index >= 0:
            self._history_index = -1
            self.value = ""
            return

        # Set value from history
        history_value: str = self._history[self._history_index]
        self.value = history_value
