"""Tests for TUI keyboard shortcuts and manager."""

from typing import List

from council_ai.cli.tui.keyboard import KeyBinding, KeyboardShortcutManager


def test_register_and_trigger_action_calls_handler():
    manager = KeyboardShortcutManager()

    called: List[str] = []

    def handler():
        called.append("ok")

    manager.register_handler("submit_query", handler)

    # 'enter' is mapped to 'submit_query'
    assert manager.trigger_action("enter") is True
    assert called == ["ok"]


def test_trigger_action_no_binding_returns_false():
    manager = KeyboardShortcutManager()

    assert manager.trigger_action("nonexistent") is False


def test_trigger_action_handler_raises_returns_false(capfd):
    manager = KeyboardShortcutManager()

    def bad():
        raise RuntimeError("boom")

    manager.register_handler("submit_query", bad)

    assert manager.trigger_action("enter") is False
    captured = capfd.readouterr()
    assert "Error executing action" in captured.out


def test_get_bindings_by_category_returns_expected():
    manager = KeyboardShortcutManager()

    session_bindings = manager.get_bindings_by_category("session")
    assert isinstance(session_bindings, dict)
    assert "enter" in session_bindings


def test_get_binding_returns_correct_keybinding():
    manager = KeyboardShortcutManager()

    binding = manager.get_binding("enter")
    assert isinstance(binding, KeyBinding)
    assert binding.action == "submit_query"


def test_display_shortcuts_runs_without_error(capsys):
    manager = KeyboardShortcutManager()
    # Shouldn't raise
    manager.display_shortcuts()
    captured = capsys.readouterr()
    # Some output expected
    assert "Keyboard Shortcuts" in captured.out or captured.out.strip() != ""
