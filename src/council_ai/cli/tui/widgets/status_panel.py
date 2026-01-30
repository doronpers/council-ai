"""Status panel widget for TUI."""

from textual.widgets import Static


class StatusPanel(Static):
    """Status panel showing domain, members, session, and mode."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._domain = "general"
        self._members: list = []
        self._session_id: str | None = None
        self._mode = "synthesis"
        self._member_statuses: dict = {}
        self.update_display()

    def update_display(self) -> None:
        """Update the status display."""
        parts = []
        parts.append(f"Domain: {self._domain}")
        if self._members:
            member_str = ", ".join(self._members[:3])
            if len(self._members) > 3:
                member_str += f" (+{len(self._members) - 3})"
            parts.append(f"Members: {member_str}")
        parts.append(f"Mode: {self._mode}")
        if self._session_id:
            parts.append(f"Session: {self._session_id[:8]}")
        if self._member_statuses:
            status_parts = []
            for pid, status in self._member_statuses.items():
                if status == "thinking":
                    status_parts.append(f"{pid}:💭")
                elif status == "responding":
                    status_parts.append(f"{pid}:⏳")
                elif status == "completed":
                    status_parts.append(f"{pid}:✓")
            if status_parts:
                parts.append(" | ".join(status_parts))

        self.update(" | ".join(parts))

    @property
    def domain(self) -> str:
        """Get domain."""
        return self._domain

    @domain.setter
    def domain(self, value: str) -> None:
        """Set domain."""
        self._domain = value
        self.update_display()

    @property
    def members(self) -> list:
        """Get members."""
        return self._members

    @members.setter
    def members(self, value: list) -> None:
        """Set members."""
        self._members = value
        self.update_display()

    @property
    def session_id(self) -> str | None:
        """Get session ID."""
        return self._session_id

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        """Set session ID."""
        self._session_id = value
        self.update_display()

    @property
    def mode(self) -> str:
        """Get mode."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Set mode."""
        self._mode = value
        self.update_display()

    @property
    def member_statuses(self) -> dict:
        """Get member statuses."""
        return self._member_statuses

    @member_statuses.setter
    def member_statuses(self, value: dict) -> None:
        """Set member statuses."""
        self._member_statuses = value
        self.update_display()
