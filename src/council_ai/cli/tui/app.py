"""Main TUI application for Council AI."""

import sys
from typing import Optional

try:
    from textual.app import App
    from textual.binding import Binding
except ImportError:
    print(
        "[red]Error:[/red] Textual is not installed. Install with: [cyan]pip install -e '.[tui]'[/cyan]"
    )
    sys.exit(1)

from ...core.config import ConfigManager, get_api_key
from ...core.history import ConsultationHistory
from ..utils import DEFAULT_PROVIDER, assemble_council
from .screens import MainScreen


class CouncilTUI(App):
    """Main TUI application for Council AI."""

    TITLE = "🏛️ Council AI"
    CSS_PATH = None  # We'll use default styling for now

    BINDINGS = [
        Binding("ctrl+c", "exit", "Exit", priority=True),
        Binding("f1", "help", "Help"),
        Binding("f2", "members", "Members"),
        Binding("f3", "config", "Config"),
    ]

    def __init__(
        self,
        domain: str = "general",
        members: Optional[list] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        session_id: Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.config_manager = ConfigManager()
        self.domain = domain
        self.members = members
        self.provider = provider or self.config_manager.get("api.provider", DEFAULT_PROVIDER)
        self.api_key = api_key or get_api_key(self.provider)
        self.model = model or self.config_manager.get("api.model")
        self.base_url = base_url or self.config_manager.get("api.base_url")
        self.session_id = session_id

        # Assemble council
        self.council = assemble_council(
            self.domain, self.members, self.api_key, self.provider, self.model, self.base_url
        )

        # Enable history
        self.council._history = ConsultationHistory()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.push_screen(
            MainScreen(
                self.council,
                domain=self.domain,
                members=self.members,
                session_id=self.session_id,
            )
        )

    def action_exit(self) -> None:
        """Handle exit action."""
        self.exit()

    def action_help(self) -> None:
        """Show help."""
        # TODO: Implement help screen
        pass

    def action_members(self) -> None:
        """Show members."""
        # TODO: Implement member selection
        pass

    def action_config(self) -> None:
        """Show config."""
        # TODO: Implement config screen
        pass
