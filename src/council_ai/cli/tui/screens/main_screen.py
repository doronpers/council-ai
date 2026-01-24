"""Main consultation screen for TUI."""

import asyncio
import re
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header

from ..keyboard import HelpPanel, KeyboardShortcutManager, NavigationHints
from ..scrolling import ContentPersistenceManager, ResponseNavigator, ScrollPositionManager
from ..widgets import HistoryPanel, InputPanel, ResponsePanel, StatusPanel, ThinkingPanel


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
        self._consultation_tasks: list = []  # Track async tasks to prevent garbage collection

        # Initialize Phase 4 utilities
        self.keyboard_manager = KeyboardShortcutManager()
        self.content_manager = ContentPersistenceManager()
        self.scroll_manager = ScrollPositionManager()
        self.navigation_hints = NavigationHints()
        self.help_panel = HelpPanel()
        self.response_navigator = ResponseNavigator()

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        try:
            yield Header(show_clock=True)
            with Container(id="main-container"):
                with Vertical(id="content-area"):
                    yield StatusPanel(id="status-panel")
                    yield ThinkingPanel(id="thinking-panel")
                    yield ResponsePanel(id="response-panel")
                    yield HistoryPanel(id="history-panel")
                yield InputPanel(placeholder="Ask your council a question...", id="input-panel")
            yield Footer()
        except Exception:
            raise

    def on_mount(self) -> None:
        """Called when screen is mounted - setup keyboard handlers."""
        # Update status display
        self._update_status()
        self.input_panel.focus()

        # Register keyboard handlers for common actions
        self.keyboard_manager.register_handler("ctrl+s", self._handle_save_session)
        self.keyboard_manager.register_handler("?", self._handle_show_help)
        self.keyboard_manager.register_handler("f1", self._handle_show_help)
        self.keyboard_manager.register_handler("tab", self._handle_focus_next_section)
        self.keyboard_manager.register_handler("shift+tab", self._handle_focus_previous_section)

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
        # Use Textual's built-in method to run async functions

        # Textual's App class runs in an async context, so we can get the running loop
        try:
            loop = asyncio.get_running_loop()
            # Create task in the running loop
            task = loop.create_task(self._consult(query))
            # Store task reference to prevent garbage collection
            self._consultation_tasks.append(task)
            # Add cleanup callback to remove task when done
            task.add_done_callback(
                lambda t: self._consultation_tasks.remove(t)
                if t in self._consultation_tasks
                else None
            )
        except RuntimeError as e:
            # No event loop running - this shouldn't happen in Textual
            error_msg = f"Error: No async event loop available: {e}"
            self.response_panel.update(f"[red]{error_msg}[/red]")
            # Don't use threading fallback - it causes race conditions
            # Just report the error to the user

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
        try:
            self.response_panel.clear()
            self.thinking_panel._thinking_content = {}
        except Exception:
            self._consulting = False
            raise

        # Add to history
        try:
            self.history_panel.add_entry(query)
        except Exception:
            self._consulting = False
            raise

        # Update member statuses
        member_statuses = {}
        for member in self.council.list_members():
            member_statuses[member.id] = "waiting"
        self.status_panel.member_statuses = member_statuses

        try:
            # Import ConsultationMode - use the same pattern as app.py
            # From council_ai.cli.tui.screens, we need to go up to council_ai.core
            # The relative import ...core doesn't work because ... goes to council_ai.cli
            # So we use an absolute import which works when the package is installed
            # or when running from the src directory
            try:
                from council_ai.core.council import ConsultationMode
            except ImportError:
                # Fallback: if package not installed, use relative import with correct path
                # Go up 4 levels: screens -> tui -> cli -> council_ai, then down to core
                import os
                import sys

                current_file = os.path.abspath(__file__)
                src_dir = os.path.abspath(os.path.join(current_file, "../../../../"))
                if src_dir not in sys.path:
                    sys.path.insert(0, src_dir)
                from council_ai.core.council import ConsultationMode

            mode = ConsultationMode(self.council.config.mode.value)
            result = None

            # Helper coroutine for the consultation stream
            async def process_consultation():
                nonlocal result
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

                        # Persist response to memory
                        if persona_id in self.response_panel._responses:
                            response_content = self.response_panel._responses[persona_id]
                            thinking_content = self.thinking_panel._thinking_content.get(
                                persona_id, ""
                            )
                            self._persist_response(
                                persona_id, persona_name, response_content, thinking_content
                            )

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

            # Run consultation with 5-minute timeout
            try:
                await asyncio.wait_for(process_consultation(), timeout=300)
            except asyncio.TimeoutError:
                self.response_panel.add_error("Consultation timed out after 5 minutes")
                self._consulting = False

        except ImportError as e:
            error_msg = (
                f"Module import error: {e}\n\n"
                "This usually means council-ai is not installed properly.\n"
                "Try: pip install -e '.[tui]'"
            )
            try:
                self.response_panel.update(f"[red]{error_msg}[/red]")
            except Exception:
                pass  # Panel might not be available
        except Exception as e:
            # Show full error with traceback for debugging
            import traceback

            error_type = type(e).__name__
            error_details = (
                f"Error ({error_type}): {str(e)}\n\n" f"Full traceback:\n{traceback.format_exc()}"
            )
            # Truncate very long errors for display
            if len(error_details) > 1000:
                error_details = error_details[:1000] + "\n... (truncated)"
            try:
                self.response_panel.update(f"[red]{error_details}[/red]")
            except Exception:
                pass  # Panel might not be available
        finally:
            self._consulting = False
            # Clear member statuses
            self.status_panel.member_statuses = {}
            self.input_panel.focus()

    def action_exit(self) -> None:
        """Handle exit action."""
        self.app.exit()

    def action_help(self) -> None:
        """Show help."""
        # Show keyboard shortcuts and usage guide using HelpPanel
        help_content = self.help_panel.get_quick_start_help()
        self.response_panel.update(f"[blue]{help_content}[/blue]")

    def action_members(self) -> None:
        """Show members."""
        # Planned feature: Interactive member selection screen
        pass

    def action_config(self) -> None:
        """Show config."""
        # Planned feature: Configuration screen for provider, model, and settings
        pass

    def _persist_response(
        self, persona_id: str, persona_name: str, content: str, thinking: Optional[str] = None
    ) -> None:
        """Persist response content for session recovery."""
        self.content_manager.save_response(persona_id, persona_name, content, thinking)

    def _save_session_export(self, format: str = "markdown") -> str:
        """Export current session in specified format."""
        return self.content_manager.export_content(format=format)
