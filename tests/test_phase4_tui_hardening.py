"""Tests for Phase 4 TUI Hardening improvements."""

import pytest

# Skip all tests in this module if textual is not installed
pytest.importorskip("textual")

from council_ai.cli.tui.keyboard import HelpPanel, KeyboardShortcutManager, NavigationHints
from council_ai.cli.tui.scrolling import (
    ContentPersistenceManager,
    ResponseNavigator,
    ScrollPositionManager,
)


class TestResponseNavigator:
    """Test response navigation"""

    def test_navigator_initialization(self):
        """Test navigator initializes correctly"""
        navigator = ResponseNavigator()
        assert navigator.current_section_index == 0
        assert len(navigator.sections) == 0

    def test_register_section(self):
        """Test registering sections"""
        navigator = ResponseNavigator()
        assert len(navigator.sections) == 0
        # Note: We can't easily test with actual Textual widgets in unit tests
        # So we just verify the registration method works

    def test_focus_navigation(self):
        """Test focus navigation logic"""
        navigator = ResponseNavigator()

        # Without sections, should return None
        assert navigator.focus_next_section() is None
        assert navigator.focus_previous_section() is None
        assert navigator.focus_section(0) is None


class TestScrollPositionManager:
    """Test scroll position persistence"""

    def test_save_and_restore_position(self):
        """Test saving and restoring scroll position"""
        manager = ScrollPositionManager()

        manager.save_position("widget1", 150)
        assert manager.get_position("widget1") == 150

        manager.save_position("widget2", 300)
        assert manager.get_position("widget2") == 300

    def test_default_position_is_zero(self):
        """Test default position is 0"""
        manager = ScrollPositionManager()
        assert manager.get_position("unknown_widget") == 0

    def test_clear_positions(self):
        """Test clearing all positions"""
        manager = ScrollPositionManager()
        manager.save_position("widget1", 100)
        manager.save_position("widget2", 200)

        manager.clear_positions()
        assert manager.get_position("widget1") == 0
        assert manager.get_position("widget2") == 0


class TestContentPersistenceManager:
    """Test content persistence"""

    def test_save_response(self):
        """Test saving response"""
        manager = ContentPersistenceManager()

        manager.save_response(
            persona_id="rams",
            persona_name="Robert Rams",
            content="Test response content",
        )

        assert len(manager.content_history) == 1
        entry = manager.content_history[0]
        assert entry["persona_id"] == "rams"
        assert entry["persona_name"] == "Robert Rams"
        assert entry["content"] == "Test response content"

    def test_get_response(self):
        """Test retrieving response"""
        manager = ContentPersistenceManager()

        manager.save_response("rams", "Robert Rams", "Response 1")
        manager.save_response("grove", "Andy Grove", "Response 2")

        assert manager.get_response(0)["persona_name"] == "Robert Rams"
        assert manager.get_response(1)["persona_name"] == "Andy Grove"
        assert manager.get_response(999) is None

    def test_get_persona_responses(self):
        """Test getting all responses from persona"""
        manager = ContentPersistenceManager()

        manager.save_response("rams", "Robert Rams", "Response 1")
        manager.save_response("grove", "Andy Grove", "Response 1")
        manager.save_response("rams", "Robert Rams", "Response 2")

        rams_responses = manager.get_persona_responses("rams")
        assert len(rams_responses) == 2
        assert all(r["persona_id"] == "rams" for r in rams_responses)

    def test_max_history_limit(self):
        """Test max history limit"""
        manager = ContentPersistenceManager(max_history=5)

        for i in range(10):
            manager.save_response(f"persona{i}", f"Name {i}", f"Response {i}")

        assert len(manager.content_history) == 5
        # Should keep most recent 5
        assert manager.content_history[0]["persona_id"] == "persona5"
        assert manager.content_history[-1]["persona_id"] == "persona9"

    def test_export_markdown(self):
        """Test exporting as markdown"""
        manager = ContentPersistenceManager()

        manager.save_response("rams", "Robert Rams", "Strategic response")
        manager.save_response(
            "grove", "Andy Grove", "Management response", "Thinking about efficiency"
        )

        markdown = manager.export_content(format="markdown")
        assert "# Council AI Session" in markdown
        assert "## Robert Rams" in markdown
        assert "## Andy Grove" in markdown
        assert "Strategic response" in markdown

    def test_export_json(self):
        """Test exporting as JSON"""
        manager = ContentPersistenceManager()

        manager.save_response("rams", "Robert Rams", "Response text")

        json_output = manager.export_content(format="json")
        assert "Robert Rams" in json_output
        assert "Response text" in json_output

    def test_export_text(self):
        """Test exporting as plain text"""
        manager = ContentPersistenceManager()

        manager.save_response("rams", "Robert Rams", "Response text")

        text_output = manager.export_content(format="text")
        assert "Robert Rams" in text_output
        assert "Response text" in text_output

    def test_clear_history(self):
        """Test clearing history"""
        manager = ContentPersistenceManager()

        manager.save_response("rams", "Robert Rams", "Response")
        assert len(manager.content_history) == 1

        manager.clear_history()
        assert len(manager.content_history) == 0


class TestKeyboardShortcutManager:
    """Test keyboard shortcuts"""

    def test_default_bindings_exist(self):
        """Test default bindings are loaded"""
        manager = KeyboardShortcutManager()
        assert len(manager.bindings) > 0

    def test_get_binding(self):
        """Test getting binding"""
        manager = KeyboardShortcutManager()

        binding = manager.get_binding("tab")
        assert binding is not None
        assert binding.key == "Tab"

    def test_unknown_binding_returns_none(self):
        """Test unknown binding returns None"""
        manager = KeyboardShortcutManager()
        assert manager.get_binding("unknown_key") is None

    def test_get_bindings_by_category(self):
        """Test getting bindings by category"""
        manager = KeyboardShortcutManager()

        nav_bindings = manager.get_bindings_by_category("navigation")
        assert len(nav_bindings) > 0
        assert all(b.category == "navigation" for b in nav_bindings.values())

    def test_register_handler(self):
        """Test registering action handler"""
        manager = KeyboardShortcutManager()

        called = []

        def test_action():
            called.append(True)

        manager.register_handler("test_action", test_action)
        assert "test_action" in manager.handlers

    def test_trigger_action_success(self):
        """Test triggering action successfully"""
        manager = KeyboardShortcutManager()

        called = []

        def test_action():
            called.append(True)

        manager.register_handler("submit_query", test_action)

        # Should work since "enter" maps to "submit_query"
        result = manager.trigger_action("enter")
        assert result is True
        assert len(called) == 1

    def test_trigger_action_no_handler(self):
        """Test triggering action with no handler"""
        manager = KeyboardShortcutManager()

        result = manager.trigger_action("tab")
        assert result is False  # No handler registered


class TestNavigationHints:
    """Test navigation hint generation"""

    def test_basic_hints_not_empty(self):
        """Test basic hints are not empty"""
        hints = NavigationHints.display_basic_hints()
        assert len(hints) > 0
        assert "Navigation" in hints

    def test_section_hints_not_empty(self):
        """Test section hints"""
        hints = NavigationHints.display_section_hints()
        assert len(hints) > 0
        assert "Section" in hints

    def test_input_hints_not_empty(self):
        """Test input hints"""
        hints = NavigationHints.display_input_hints()
        assert len(hints) > 0
        assert "Input" in hints


class TestHelpPanel:
    """Test help content generation"""

    def test_quick_start_help_content(self):
        """Test quick start help"""
        help_text = HelpPanel.get_quick_start_help()
        assert "Quick Start" in help_text
        assert "Input Section" in help_text
        assert "Navigation" in help_text

    def test_advanced_help_content(self):
        """Test advanced help"""
        help_text = HelpPanel.get_advanced_help()
        assert "Advanced Tips" in help_text
        assert "Performance" in help_text


class TestIntegrationTUI:
    """Integration tests for TUI components"""

    def test_full_session_workflow(self):
        """Test complete session workflow"""
        # Initialize managers
        content_manager = ContentPersistenceManager()
        position_manager = ScrollPositionManager()
        keyboard_manager = KeyboardShortcutManager()

        # Add some content
        content_manager.save_response("rams", "Robert Rams", "Strategic advice")
        content_manager.save_response("grove", "Andy Grove", "Management tips")

        # Save positions
        position_manager.save_position("thinking", 50)
        position_manager.save_position("response", 100)

        # Register keyboard handlers
        keyboard_manager.register_handler("clear_view", content_manager.clear_history)

        # Verify state
        assert len(content_manager.content_history) == 2
        assert position_manager.get_position("thinking") == 50

        # Trigger clear
        keyboard_manager.trigger_action("ctrl+l")  # clear_view
        assert len(content_manager.content_history) == 0

    def test_keyboard_navigation_workflow(self):
        """Test keyboard navigation workflow"""
        keyboard_manager = KeyboardShortcutManager()

        # Get various categories
        nav = keyboard_manager.get_bindings_by_category("navigation")
        session = keyboard_manager.get_bindings_by_category("session")
        editing = keyboard_manager.get_bindings_by_category("editing")

        assert len(nav) > 0
        assert len(session) > 0
        assert len(editing) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
