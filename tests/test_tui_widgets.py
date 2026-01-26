"""Unit tests for TUI widget components."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Skip all tests in this module if textual is not installed
pytest.importorskip("textual")

from council_ai.cli.tui.widgets.status_panel import StatusPanel  # noqa: E402
from council_ai.cli.tui.widgets.response_panel import ResponsePanel  # noqa: E402
from council_ai.cli.tui.widgets.thinking_panel import ThinkingPanel  # noqa: E402
from council_ai.cli.tui.widgets.history_panel import HistoryPanel  # noqa: E402


class TestStatusPanel:
    """Tests for StatusPanel widget."""

    def test_init_default_values(self):
        """Test that StatusPanel initializes with correct defaults."""
        panel = StatusPanel()

        assert panel._domain == "general"
        assert panel._members == []
        assert panel._session_id is None
        assert panel._mode == "synthesis"
        assert panel._member_statuses == {}

    def test_domain_property(self):
        """Test domain property getter and setter."""
        panel = StatusPanel()

        panel.domain = "tech"
        assert panel.domain == "tech"

    def test_members_property(self):
        """Test members property getter and setter."""
        panel = StatusPanel()

        panel.members = ["analyst", "critic"]
        assert panel.members == ["analyst", "critic"]

    def test_session_id_property(self):
        """Test session_id property getter and setter."""
        panel = StatusPanel()

        panel.session_id = "test-session-123"
        assert panel.session_id == "test-session-123"

    def test_mode_property(self):
        """Test mode property getter and setter."""
        panel = StatusPanel()

        panel.mode = "debate"
        assert panel.mode == "debate"

    def test_member_statuses_property(self):
        """Test member_statuses property getter and setter."""
        panel = StatusPanel()

        statuses = {"analyst": "thinking", "critic": "completed"}
        panel.member_statuses = statuses
        assert panel.member_statuses == statuses

    def test_update_display_basic(self):
        """Test that update_display generates correct content."""
        panel = StatusPanel()

        # Mock the update method
        panel.update = MagicMock()

        panel._domain = "general"
        panel._mode = "synthesis"
        panel.update_display()

        # Check that update was called with content containing domain and mode
        call_args = panel.update.call_args[0][0]
        assert "Domain: general" in call_args
        assert "Mode: synthesis" in call_args

    def test_update_display_with_members(self):
        """Test update_display with member list."""
        panel = StatusPanel()
        panel.update = MagicMock()

        panel._members = ["analyst", "critic", "advisor"]
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "Members:" in call_args
        assert "analyst" in call_args

    def test_update_display_truncates_members(self):
        """Test that member list is truncated when too long."""
        panel = StatusPanel()
        panel.update = MagicMock()

        panel._members = ["a", "b", "c", "d", "e"]
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "(+2)" in call_args  # 5 members, showing 3, so +2

    def test_update_display_with_session_id(self):
        """Test update_display with session ID."""
        panel = StatusPanel()
        panel.update = MagicMock()

        panel._session_id = "abcdefgh12345678"
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "Session: abcdefgh" in call_args  # First 8 chars

    def test_update_display_with_member_statuses(self):
        """Test update_display with member status indicators."""
        panel = StatusPanel()
        panel.update = MagicMock()

        panel._member_statuses = {
            "analyst": "thinking",
            "critic": "responding",
            "advisor": "completed",
        }
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        # Check for status emoji indicators
        assert "analyst:" in call_args
        assert "critic:" in call_args
        assert "advisor:" in call_args


class TestResponsePanel:
    """Tests for ResponsePanel widget."""

    def test_init(self):
        """Test ResponsePanel initializes correctly."""
        panel = ResponsePanel()

        assert panel._responses == {}
        assert panel._synthesis == ""

    def test_add_response_chunk(self):
        """Test adding response chunks for a persona."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel.add_response_chunk("analyst", "Hello ")
        assert panel._responses["analyst"] == "Hello "

        panel.add_response_chunk("analyst", "world!")
        assert panel._responses["analyst"] == "Hello world!"

    def test_set_response(self):
        """Test setting full response for a persona."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel.set_response("analyst", "Full response content")
        assert panel._responses["analyst"] == "Full response content"

    def test_set_synthesis(self):
        """Test setting synthesis content."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel.set_synthesis("Synthesized response")
        assert panel._synthesis == "Synthesized response"

    def test_add_synthesis_chunk(self):
        """Test adding synthesis chunks."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel.add_synthesis_chunk("Part 1 ")
        assert panel._synthesis == "Part 1 "

        panel.add_synthesis_chunk("Part 2")
        assert panel._synthesis == "Part 1 Part 2"

    def test_clear(self):
        """Test clearing all responses."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel._responses = {"analyst": "response"}
        panel._synthesis = "synthesis"

        panel.clear()

        assert panel._responses == {}
        assert panel._synthesis == ""

    def test_add_error(self):
        """Test adding error message."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel.add_error("Something went wrong")

        call_args = panel.update.call_args[0][0]
        assert "Error: Something went wrong" in call_args

    def test_update_display_empty(self):
        """Test update_display with no responses."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "Waiting for responses" in call_args

    def test_update_display_truncates_long_responses(self):
        """Test that long responses are truncated in display."""
        panel = ResponsePanel()
        panel.update = MagicMock()

        # Create a response longer than 500 chars
        long_response = "x" * 600
        panel._responses["analyst"] = long_response
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "..." in call_args  # Truncation indicator


class TestThinkingPanel:
    """Tests for ThinkingPanel widget."""

    def test_init(self):
        """Test ThinkingPanel initializes correctly."""
        panel = ThinkingPanel()

        assert panel._thinking_content == {}

    def test_set_thinking(self):
        """Test setting thinking content for a persona."""
        panel = ThinkingPanel()
        panel.update = MagicMock()

        panel.set_thinking("analyst", "Processing query...")
        assert panel._thinking_content["analyst"] == "Processing query..."

    def test_clear_persona(self):
        """Test clearing thinking for a specific persona."""
        panel = ThinkingPanel()
        panel.update = MagicMock()

        panel._thinking_content = {
            "analyst": "thinking...",
            "critic": "also thinking...",
        }

        panel.clear_persona("analyst")

        assert "analyst" not in panel._thinking_content
        assert "critic" in panel._thinking_content

    def test_clear_persona_nonexistent(self):
        """Test clearing thinking for non-existent persona doesn't error."""
        panel = ThinkingPanel()
        panel.update = MagicMock()

        panel._thinking_content = {"analyst": "thinking..."}

        # Should not raise
        panel.clear_persona("nonexistent")
        assert panel._thinking_content == {"analyst": "thinking..."}

    def test_thinking_content_property(self):
        """Test thinking_content property getter and setter."""
        panel = ThinkingPanel()
        panel.update = MagicMock()

        content = {"analyst": "deep thoughts"}
        panel.thinking_content = content
        assert panel.thinking_content == content

    def test_update_display_empty(self):
        """Test update_display with no thinking content."""
        panel = ThinkingPanel()
        panel.update = MagicMock()

        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert call_args == ""

    def test_update_display_truncates_long_thinking(self):
        """Test that long thinking content is truncated."""
        panel = ThinkingPanel()
        panel.update = MagicMock()

        # Create thinking content longer than 200 chars
        long_thinking = "x" * 250
        panel._thinking_content["analyst"] = long_thinking
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "..." in call_args  # Truncation indicator


class TestHistoryPanel:
    """Tests for HistoryPanel widget."""

    def test_init(self):
        """Test HistoryPanel initializes correctly."""
        panel = HistoryPanel()

        assert panel._history == []

    def test_add_entry(self):
        """Test adding history entry."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        panel.add_entry("What is AI?", "AI is artificial intelligence.")

        assert len(panel._history) == 1
        assert panel._history[0]["question"] == "What is AI?"
        assert panel._history[0]["synthesis"] == "AI is artificial intelligence."

    def test_add_entry_no_synthesis(self):
        """Test adding history entry without synthesis."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        panel.add_entry("What is AI?")

        assert panel._history[0]["synthesis"] == ""

    def test_history_limit(self):
        """Test that history is limited to 50 entries."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        # Add 60 entries
        for i in range(60):
            panel.add_entry(f"Question {i}", f"Answer {i}")

        assert len(panel._history) == 50
        # Should keep the most recent entries
        assert panel._history[0]["question"] == "Question 10"
        assert panel._history[-1]["question"] == "Question 59"

    def test_history_property(self):
        """Test history property getter and setter."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        history = [{"question": "Q1", "synthesis": "A1"}]
        panel.history = history
        assert panel.history == history

    def test_update_display_empty(self):
        """Test update_display with no history."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "No questions yet" in call_args

    def test_update_display_shows_last_10(self):
        """Test update_display only shows last 10 entries."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        # Add 15 entries
        panel._history = [
            {"question": f"Q{i}", "synthesis": f"A{i}"}
            for i in range(15)
        ]
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        # Should contain Q5-Q14 (last 10)
        assert "Q14" in call_args
        assert "Q5" in call_args
        # Should not contain Q0-Q4
        assert "Q0" not in call_args

    def test_update_display_truncates_long_questions(self):
        """Test that long questions are truncated in display."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        long_question = "x" * 100
        panel._history = [{"question": long_question, "synthesis": "answer"}]
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "..." in call_args  # Truncation indicator

    def test_update_display_truncates_long_synthesis(self):
        """Test that long synthesis is truncated in display."""
        panel = HistoryPanel()
        panel.update = MagicMock()

        long_synthesis = "x" * 100
        panel._history = [{"question": "Q1", "synthesis": long_synthesis}]
        panel.update_display()

        call_args = panel.update.call_args[0][0]
        assert "..." in call_args  # Truncation indicator
