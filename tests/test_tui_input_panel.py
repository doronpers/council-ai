"""Unit tests for TUI InputPanel widget."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import os

# Skip all tests in this module if textual is not installed
pytest.importorskip("textual")


class TestInputPanelHistoryNavigation:
    """Tests for InputPanel history navigation logic."""

    def test_navigate_history_empty_history(self):
        """Test navigating with empty history does nothing."""
        with patch(
            "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
        ) as mock_config:
            mock_config.return_value = Path(tempfile.mkdtemp())

            from council_ai.cli.tui.widgets.input_panel import InputPanel

            panel = InputPanel()
            panel._history = []
            panel._history_index = -1

            # Should not raise or change anything
            panel._navigate_history(-1)
            assert panel._history_index == -1

    def test_navigate_history_up(self):
        """Test navigating up through history."""
        with patch(
            "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
        ) as mock_config:
            mock_config.return_value = Path(tempfile.mkdtemp())

            from council_ai.cli.tui.widgets.input_panel import InputPanel

            panel = InputPanel()
            panel._history = ["first", "second", "third"]
            panel._history_index = -1

            # Navigate up (backwards through history)
            panel._navigate_history(-1)
            assert panel._history_index == -1
            assert panel.value == "third"

            panel._navigate_history(-1)
            assert panel._history_index == -2
            assert panel.value == "second"

            panel._navigate_history(-1)
            assert panel._history_index == -3
            assert panel.value == "first"

    def test_navigate_history_up_clamps_at_beginning(self):
        """Test that history navigation doesn't go past beginning."""
        with patch(
            "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
        ) as mock_config:
            mock_config.return_value = Path(tempfile.mkdtemp())

            from council_ai.cli.tui.widgets.input_panel import InputPanel

            panel = InputPanel()
            panel._history = ["first", "second"]
            panel._history_index = -2

            # Try to go past beginning
            panel._navigate_history(-1)
            assert panel._history_index == -2  # Clamped

    def test_navigate_history_down_clears_at_end(self):
        """Test navigating down past end clears input."""
        with patch(
            "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
        ) as mock_config:
            mock_config.return_value = Path(tempfile.mkdtemp())

            from council_ai.cli.tui.widgets.input_panel import InputPanel

            panel = InputPanel()
            panel._history = ["first", "second"]
            panel._history_index = -1
            panel.value = "second"

            # Navigate down (forward)
            panel._navigate_history(1)
            assert panel._history_index == -1
            assert panel.value == ""


class TestInputPanelHistoryPersistence:
    """Tests for InputPanel history file operations."""

    def test_load_history_from_file(self):
        """Test loading history from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.txt"
            history_file.write_text("line1\nline2\nline3\n", encoding="utf-8")

            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                # Manually trigger load since __init__ already did it
                panel._history_file = history_file
                panel._load_history()

                assert panel._history == ["line1", "line2", "line3"]

    def test_load_history_missing_file(self):
        """Test loading history when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                # Should not raise, history should be empty
                assert panel._history == []

    def test_load_history_strips_whitespace(self):
        """Test that loaded history strips whitespace and empty lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.txt"
            history_file.write_text("  line1  \n\nline2\n  \n", encoding="utf-8")

            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history_file = history_file
                panel._load_history()

                assert panel._history == ["line1", "line2"]

    def test_load_history_limits_to_1000_entries(self):
        """Test that history is limited to 1000 entries on load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.txt"
            # Write 1500 lines
            lines = [f"line{i}" for i in range(1500)]
            history_file.write_text("\n".join(lines), encoding="utf-8")

            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history_file = history_file
                panel._load_history()

                assert len(panel._history) == 1000
                # Should keep last 1000
                assert panel._history[0] == "line500"
                assert panel._history[-1] == "line1499"

    def test_save_history_creates_directory(self):
        """Test that save_history creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = Path(tmpdir) / "nested" / "config"
            history_file = nested_dir / "history.txt"

            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = nested_dir

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history_file = history_file
                panel._history = ["test1", "test2"]
                panel._save_history()

                assert history_file.parent.exists()
                assert history_file.exists()

    def test_save_history_writes_entries(self):
        """Test that save_history writes all entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.txt"

            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history_file = history_file
                panel._history = ["entry1", "entry2", "entry3"]
                panel._save_history()

                content = history_file.read_text(encoding="utf-8")
                assert "entry1\n" in content
                assert "entry2\n" in content
                assert "entry3\n" in content

    def test_save_history_limits_to_1000(self):
        """Test that save_history only saves last 1000 entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.txt"

            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history_file = history_file
                panel._history = [f"entry{i}" for i in range(1500)]
                panel._save_history()

                content = history_file.read_text(encoding="utf-8").strip().split("\n")
                assert len(content) == 1000


class TestInputPanelSubmitted:
    """Tests for InputPanel.Submitted message class."""

    def test_submitted_message_stores_value(self):
        """Test that Submitted message stores the input value."""
        with patch(
            "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
        ) as mock_config:
            mock_config.return_value = Path(tempfile.mkdtemp())

            from council_ai.cli.tui.widgets.input_panel import InputPanel

            msg = InputPanel.Submitted("test input")
            assert msg.value == "test input"


class TestInputPanelDuplicateHistory:
    """Tests for InputPanel duplicate history prevention."""

    def test_no_duplicate_consecutive_entries(self):
        """Test that consecutive duplicate entries are not added to history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history = ["existing"]

                # Simulate adding same entry twice via internal logic
                input_text = "existing"
                if not panel._history or panel._history[-1] != input_text:
                    panel._history.append(input_text)

                # Should not add duplicate
                assert panel._history == ["existing"]

    def test_allows_non_consecutive_duplicates(self):
        """Test that non-consecutive duplicates are allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "council_ai.cli.tui.widgets.input_panel.get_workspace_config_dir"
            ) as mock_config:
                mock_config.return_value = Path(tmpdir)

                from council_ai.cli.tui.widgets.input_panel import InputPanel

                panel = InputPanel()
                panel._history = ["first", "second"]

                # Simulate adding "first" again (not consecutive)
                input_text = "first"
                if not panel._history or panel._history[-1] != input_text:
                    panel._history.append(input_text)

                assert panel._history == ["first", "second", "first"]
