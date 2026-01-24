"""Tests for CLI quickstart command."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

import council_ai
from council_ai.cli import main
from council_ai.cli.commands import misc


def _set_misc_file(monkeypatch, tmp_path: Path) -> Path:
    misc_path = tmp_path / "project" / "src" / "council_ai" / "cli" / "commands"
    misc_path.mkdir(parents=True)
    fake_misc_file = misc_path / "misc.py"
    fake_misc_file.write_text("# placeholder")
    monkeypatch.setattr(misc, "__file__", str(fake_misc_file))
    return tmp_path / "project"


def test_quickstart_runs_from_repo_root(monkeypatch, tmp_path):
    runner = CliRunner()
    root_path = _set_misc_file(monkeypatch, tmp_path)
    quickstart_path = root_path / "examples" / "quickstart.py"
    quickstart_path.parent.mkdir(parents=True, exist_ok=True)
    quickstart_path.write_text("print('ok')")

    with patch("council_ai.cli.commands.misc.subprocess.run") as mock_run:
        result = runner.invoke(main, ["quickstart"])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0][1] == str(quickstart_path)


def test_quickstart_falls_back_to_package_root(monkeypatch, tmp_path):
    runner = CliRunner()
    _set_misc_file(monkeypatch, tmp_path)

    pkg_root = tmp_path
    pkg_init = pkg_root / "pkg" / "council_ai" / "__init__.py"
    pkg_init.parent.mkdir(parents=True)
    pkg_init.write_text("# placeholder")
    monkeypatch.setattr(council_ai, "__file__", str(pkg_init))

    quickstart_path = pkg_root / "examples" / "quickstart.py"
    quickstart_path.parent.mkdir(parents=True, exist_ok=True)
    quickstart_path.write_text("print('ok')")

    with patch("council_ai.cli.commands.misc.subprocess.run") as mock_run:
        result = runner.invoke(main, ["quickstart"])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0][1] == str(quickstart_path)


def test_quickstart_missing_outputs_message(monkeypatch, tmp_path):
    runner = CliRunner()
    _set_misc_file(monkeypatch, tmp_path)

    pkg_init = tmp_path / "pkg" / "council_ai" / "__init__.py"
    pkg_init.parent.mkdir(parents=True)
    pkg_init.write_text("# placeholder")
    monkeypatch.setattr(council_ai, "__file__", str(pkg_init))

    with patch("council_ai.cli.commands.misc.subprocess.run") as mock_run:
        result = runner.invoke(main, ["quickstart"])

    assert result.exit_code == 0
    mock_run.assert_not_called()
    assert "Quickstart demo not found" in result.output
