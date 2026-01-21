"""Main consultation screen for TUI."""

import re
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header

from ..widgets import (
    HistoryPanel,
    InputPanel,
    ResponsePanel,
    StatusPanel,
    ThinkingPanel,
)


class MainScreen(Screen):
    """Main consultation screen with all panels."""

    BINDINGS = [
        ("ctrl+c", "exit", "Exit"),
        ("f1", "help", "Help"),
        ("f2", "members", "Members"),
        ("f3", "config", "Config"),
    ]

    def __init__(
        self,
        council,
        domain: str = "general",
        members: Optional[list] = None,
        session_id: Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.council = council
        self.domain = domain
        self.members = members or []
        self.session_id = session_id
        self._consulting = False

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Vertical(id="content-area"):
                yield StatusPanel(id="status-panel")
                yield ThinkingPanel(id="thinking-panel")
                yield ResponsePanel(id="response-panel")
                yield HistoryPanel(id="history-panel")
            yield InputPanel(placeholder="Ask your council a question...", id="input-panel")
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self._update_status()
        self.input_panel.focus()

    @property
    def status_panel(self) -> StatusPanel:
        """Get status panel widget."""
        return self.query_one("#status-panel", StatusPanel)

    @property
    def thinking_panel(self) -> ThinkingPanel:
        """Get thinking panel widget."""
        return self.query_one("#thinking-panel", ThinkingPanel)

    @property
    def response_panel(self) -> ResponsePanel:
        """Get response panel widget."""
        return self.query_one("#response-panel", ResponsePanel)

    @property
    def history_panel(self) -> HistoryPanel:
        """Get history panel widget."""
        return self.query_one("#history-panel", HistoryPanel)

    @property
    def input_panel(self) -> InputPanel:
        """Get input panel widget."""
        return self.query_one("#input-panel", InputPanel)

    def _update_status(self) -> None:
        """Update status panel with current state."""
        member_ids = [m.id for m in self.council.list_members()]
        self.status_panel.domain = self.domain
        self.status_panel.members = member_ids
        self.status_panel.session_id = self.session_id
        self.status_panel.mode = self.council.config.mode.value

    def on_input_panel_submitted(self, event: InputPanel.Submitted) -> None:
        """Handle input submission."""
        if self._consulting:
            return  # Ignore if already consulting

        query = event.value.strip()
        if not query:
            return

        # Parse bracket notation for members
        bracket_members = self._parse_bracket_notation(query)
        if bracket_members:
            # Remove bracket notation from query
            query = re.sub(r"\[[^\]]+\]\s*", "", query).strip()
            # Update council members
            self.council._members.clear()
            for member_id in bracket_members:
                try:
                    self.council.add_member(member_id)
                except ValueError:
                    pass
            self._update_status()

        # Start consultation - Textual apps run in async context
        import asyncio
        asyncio.create_task(self._consult(query))

    def _parse_bracket_notation(self, text: str) -> Optional[list]:
        """Parse bracket notation for persona IDs."""
        match = re.search(r"\[([^\]]+)\]", text)
        if match:
            content = match.group(1)
            ids = []
            for id_str in content.split(","):
                id_str = id_str.strip()
                if id_str:
                    if len(id_str) <= 3:
                        ids.append(id_str.upper())
                    else:
                        ids.append(id_str.lower())
            return ids if ids else None
        return None

    async def _consult(self, query: str) -> None:
        """Run a consultation."""
        if self._consulting:
            return

        self._consulting = True
        self.response_panel.clear()
        self.thinking_panel._thinking_content = {}

        # Add to history
        self.history_panel.add_entry(query)

        # Update member statuses
        member_statuses = {}
        for member in self.council.list_members():
            member_statuses[member.id] = "waiting"
        self.status_panel.member_statuses = member_statuses

        # Run async consultation
        import asyncio

        async def run_consultation():
            try:
                from ...core.council import ConsultationMode

                mode = ConsultationMode(self.council.config.mode.value)
                result = None

                async for event in self.council.consult_stream(
                    query, mode=mode, session_id=self.session_id
                ):
                    event_type = event.get("type")
                    persona_id = event.get("persona_id")
                    persona_name = event.get("persona_name", persona_id)
                    persona_emoji = event.get("persona_emoji", "")

                    if event_type == "response_start":
                        if persona_id:
                            member_statuses[persona_id] = "responding"
                            self.status_panel.member_statuses = member_statuses

                    elif event_type == "thinking_chunk":
                        content = event.get("content", "")
                        accumulated = event.get("accumulated_thinking", "")
                        if persona_id and accumulated:
                            self.thinking_panel.set_thinking(persona_id, accumulated)

                    elif event_type == "response_chunk":
                        content = event.get("content", "")
                        if persona_id and content:
                            # Use persona name with emoji if available
                            display_name = (
                                f"{persona_emoji} {persona_name}" if persona_emoji else persona_id
                            )
                            self.response_panel.add_response_chunk(display_name, content)
                            # Clear thinking when response starts
                            if persona_id in self.thinking_panel._thinking_content:
                                self.thinking_panel.clear_persona(persona_id)

                    elif event_type == "response_complete":
                        if persona_id:
                            member_statuses[persona_id] = "completed"
                            self.status_panel.member_statuses = member_statuses
                            self.thinking_panel.clear_persona(persona_id)

                    elif event_type == "synthesis_chunk":
                        chunk = event.get("chunk", "")
                        if chunk:
                            self.response_panel.add_synthesis_chunk(chunk)

                    elif event_type == "complete":
                        result = event.get("result")
                        if result:
                            self.session_id = result.session_id
                            self.status_panel.session_id = self.session_id
                            # Update history with synthesis
                            if result.synthesis:
                                # Update last entry with synthesis
                                if self.history_panel._history:
                                    last_entry = self.history_panel._history[-1]
                                    last_entry["synthesis"] = result.synthesis
                                    self.history_panel.update_display()

            except Exception as e:
                self.response_panel.update(f"[red]Error: {e}[/red]")
            finally:
                self._consulting = False
                # Clear member statuses
                self.status_panel.member_statuses = {}
                self.input_panel.focus()

        # Schedule async consultation - use Textual's background task support
        # Textual apps run in an async context, so we can use call_from_thread
        # For now, use a simple approach: run in a thread
        import threading

        def run_in_thread():
            asyncio.run(run_consultation())

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def action_exit(self) -> None:
        """Handle exit action."""
        self.app.exit()

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
