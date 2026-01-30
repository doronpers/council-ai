"""
TUI Response Scrolling and Navigation utilities

Provides keyboard navigation and scrolling control for response containers
in the Textual-based TUI.
"""

from typing import List, Optional

from textual.containers import ScrollableContainer
from textual.message import Message


class ScrollableResponse(ScrollableContainer):
    """Enhanced scrollable container for responses with keyboard support"""

    class Scrolled(Message):
        """Posted when scrolled"""

        def __init__(self, offset: int) -> None:
            super().__init__()
            self.offset = offset

    def on_mount(self) -> None:
        """Configure scrolling on mount"""
        self.can_focus = True

    def action_scroll_up(self) -> None:
        """Scroll up by 5 lines"""
        self.scroll_up(5)
        self.post_message(self.Scrolled(self.scroll_y))

    def action_scroll_down(self) -> None:
        """Scroll down by 5 lines"""
        self.scroll_down(5)
        self.post_message(self.Scrolled(self.scroll_y))

    def action_scroll_to_top(self) -> None:
        """Jump to top"""
        self.scroll_to(0, 0)
        self.post_message(self.Scrolled(0))

    def action_scroll_to_bottom(self) -> None:
        """Jump to bottom"""
        self.scroll_to(0, self.virtual_size.height)
        self.post_message(self.Scrolled(self.scroll_y))

    def action_page_up(self) -> None:
        """Page up"""
        self.scroll_up(self.size.height)
        self.post_message(self.Scrolled(self.scroll_y))

    def action_page_down(self) -> None:
        """Page down"""
        self.scroll_down(self.size.height)
        self.post_message(self.Scrolled(self.scroll_y))


class ResponseNavigator:
    """Manages keyboard navigation between response sections"""

    def __init__(self):
        """Initialize response navigator"""
        self.sections: List[ScrollableResponse] = []
        self.current_section_index = 0

    def register_section(self, section: ScrollableResponse) -> None:
        """Register a scrollable response section"""
        self.sections.append(section)

    def focus_next_section(self) -> Optional[ScrollableResponse]:
        """Move focus to next section"""
        if not self.sections:
            return None

        self.current_section_index = (self.current_section_index + 1) % len(self.sections)
        return self.sections[self.current_section_index]

    def focus_previous_section(self) -> Optional[ScrollableResponse]:
        """Move focus to previous section"""
        if not self.sections:
            return None

        self.current_section_index = (self.current_section_index - 1) % len(self.sections)
        return self.sections[self.current_section_index]

    def focus_section(self, index: int) -> Optional[ScrollableResponse]:
        """Focus specific section by index"""
        if 0 <= index < len(self.sections):
            self.current_section_index = index
            return self.sections[index]
        return None

    def get_current_section(self) -> Optional[ScrollableResponse]:
        """Get currently focused section"""
        if self.sections:
            return self.sections[self.current_section_index]
        return None


class ScrollPositionManager:
    """Manages scroll position persistence and restoration"""

    def __init__(self):
        """Initialize scroll position manager"""
        self.positions: dict[str, int] = {}

    def save_position(self, widget_id: str, scroll_offset: int) -> None:
        """Save scroll position for widget"""
        self.positions[widget_id] = scroll_offset

    def get_position(self, widget_id: str) -> int:
        """Get saved scroll position for widget"""
        return self.positions.get(widget_id, 0)

    def restore_position(self, widget: ScrollableResponse, widget_id: str) -> None:
        """Restore scroll position for widget"""
        offset = self.get_position(widget_id)
        if offset > 0:
            widget.scroll_to(0, offset)

    def clear_positions(self) -> None:
        """Clear all saved positions"""
        self.positions.clear()


class ContentPersistenceManager:
    """Manages persistence of response content during session"""

    def __init__(self, max_history: int = 100):
        """Initialize content persistence manager"""
        self.max_history = max_history
        self.content_history: List[dict] = []

    def save_response(
        self,
        persona_id: str,
        persona_name: str,
        content: str,
        thinking: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        """Save response content"""
        import time

        entry = {
            "persona_id": persona_id,
            "persona_name": persona_name,
            "content": content,
            "thinking": thinking,
            "timestamp": timestamp or time.time(),
        }

        self.content_history.append(entry)

        # Keep only recent history
        if len(self.content_history) > self.max_history:
            self.content_history = self.content_history[-self.max_history :]

    def get_response(self, index: int) -> Optional[dict]:
        """Get response from history by index"""
        if 0 <= index < len(self.content_history):
            return self.content_history[index]
        return None

    def get_persona_responses(self, persona_id: str) -> List[dict]:
        """Get all responses from specific persona"""
        return [entry for entry in self.content_history if entry["persona_id"] == persona_id]

    def get_all_content(self) -> List[dict]:
        """Get all content history"""
        return self.content_history.copy()

    def clear_history(self) -> None:
        """Clear all content history"""
        self.content_history.clear()

    def export_content(self, format: str = "markdown") -> str:
        """Export content in specified format"""
        if format == "markdown":
            return self._export_markdown()
        elif format == "json":
            return self._export_json()
        elif format == "text":
            return self._export_text()
        else:
            raise ValueError(f"Unknown format: {format}")

    def _export_markdown(self) -> str:
        """Export as markdown"""
        lines = ["# Council AI Session\n"]

        for entry in self.content_history:
            lines.append(f"## {entry['persona_name']}\n")

            if entry["thinking"]:
                lines.append("### Thinking Process\n")
                lines.append(f"{entry['thinking']}\n")

            lines.append("### Response\n")
            lines.append(f"{entry['content']}\n")

        return "\n".join(lines)

    def _export_json(self) -> str:
        """Export as JSON"""
        import json

        return json.dumps(self.content_history, indent=2, default=str)

    def _export_text(self) -> str:
        """Export as plain text"""
        lines = []

        for entry in self.content_history:
            lines.append(f"{'=' * 60}")
            lines.append(f"{entry['persona_name']}")
            lines.append(f"{'=' * 60}\n")

            if entry["thinking"]:
                lines.append("THINKING PROCESS:")
                lines.append(entry["thinking"])
                lines.append("")

            lines.append("RESPONSE:")
            lines.append(entry["content"])
            lines.append("")

        return "\n".join(lines)
