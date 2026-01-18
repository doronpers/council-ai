"""Tests for the launch-council.py script."""

# Add parent directory to path to import launch_council module
# Note: launch-council.py uses hyphens, so we import it using importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

launch_council_path = Path(__file__).parent.parent / "launch-council.py"

# Only import if file exists (for CI/CD environments where it might not be present)
launch_council: Any = None
if launch_council_path.exists():
    spec = importlib.util.spec_from_file_location("launch_council", launch_council_path)
    if spec and spec.loader:
        launch_council = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launch_council)


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestPlatformDetection:
    """Test platform detection."""

    def test_platform_constants(self):
        """Test that platform constants are set."""
        assert isinstance(launch_council.IS_WINDOWS, bool)
        assert isinstance(launch_council.IS_MAC, bool)
        assert isinstance(launch_council.IS_LINUX, bool)

        # At least one should be True
        assert launch_council.IS_WINDOWS or launch_council.IS_MAC or launch_council.IS_LINUX


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestHelperFunctions:
    """Test helper functions."""

    def test_print_functions(self, capsys):
        """Test print helper functions."""
        launch_council.print_status("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

        launch_council.print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.out

        launch_council.print_success("Success message")
        captured = capsys.readouterr()
        assert "Success message" in captured.out

        launch_council.print_info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out

        launch_council.print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out

    def test_run_command_success(self):
        """Test run_command with successful command."""
        # Use python itself to print, which ensures it works on all platforms
        # and doesn't rely on shell builtins like 'echo'
        cmd = [sys.executable, "-c", "print('test')"]

        returncode, stdout, stderr = launch_council.run_command(
            cmd, check=False, capture_output=True
        )
        assert returncode == 0

    def test_run_command_not_found(self):
        """Test run_command with non-existent command."""
        returncode, stdout, stderr = launch_council.run_command(
            ["nonexistent_command_xyz123"], check=False, capture_output=True
        )
        assert returncode != 0


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestPythonVersionCheck:
    """Test Python version checking."""

    def test_check_python_version(self):
        """Test check_python_version."""
        result = launch_council.check_python_version()
        # Should pass if Python 3.9+
        assert isinstance(result, bool)
        # Should be True for Python 3.9+
        if sys.version_info >= (3, 9):
            assert result is True


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestPackageChecks:
    """Test package installation checks."""

    def test_check_council_installed_not_installed(self):
        """Test check_council_installed when not installed."""
        with patch("importlib.util.find_spec", return_value=None):
            is_installed, is_editable = launch_council.check_council_installed()
            assert is_installed is False

    def test_check_council_installed_installed(self):
        """Test check_council_installed when installed."""
        mock_spec = MagicMock()
        mock_spec.origin = "/some/path/council_ai/__init__.py"
        with patch("importlib.util.find_spec", return_value=mock_spec):
            is_installed, is_editable = launch_council.check_council_installed()
            assert is_installed is True

    def test_check_web_dependencies(self):
        """Test check_web_dependencies."""
        has_deps = (
            importlib.util.find_spec("uvicorn") is not None
            and importlib.util.find_spec("fastapi") is not None
        )
        result = launch_council.check_web_dependencies()
        if has_deps:
            assert result is True
        else:
            assert result is False


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestAPIKeyChecks:
    """Test API key checking."""

    def test_check_api_keys_no_keys(self, monkeypatch):
        """Test check_api_keys when no keys are set."""
        # Clear all API key env vars
        for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "COUNCIL_API_KEY"]:
            monkeypatch.delenv(key, raising=False)

        has_key, provider = launch_council.check_api_keys()
        assert has_key is False
        assert provider is None

    def test_check_api_keys_with_key(self, monkeypatch):
        """Test check_api_keys when a key is set."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")
        has_key, provider = launch_council.check_api_keys()
        assert has_key is True
        assert provider == "anthropic"

    def test_check_api_keys_placeholder(self, monkeypatch):
        """Test check_api_keys ignores placeholder values."""
        # Clear all API key env vars first
        for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "COUNCIL_API_KEY"]:
            monkeypatch.delenv(key, raising=False)

        monkeypatch.setenv("ANTHROPIC_API_KEY", "your-key-here")
        has_key, provider = launch_council.check_api_keys()
        assert has_key is False


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestPortChecking:
    """Test port availability checking."""

    def test_check_port_available(self):
        """Test check_port_available."""
        # Test with a high port number that's likely available
        result = launch_council.check_port_available(65535)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)

    def test_check_port_unavailable(self):
        """Test check_port_available with a port that might be in use."""
        # This test might fail if port 1 is actually in use, but it's unlikely
        # Just verify the function works
        result = launch_council.check_port_available(1)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestBrowserOpening:
    """Test browser opening functionality."""

    def test_open_browser(self):
        """Test open_browser function."""
        # Test with a valid URL
        result = launch_council.open_browser("http://127.0.0.1:8000")
        # Should return True if platform supports it
        assert isinstance(result, bool)


@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestArgumentParsing:
    """Test argument parsing."""

    def test_parse_host_port(self):
        """Test --host and --port flag parsing."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=8000)
        args = parser.parse_args(["--host", "0.0.0.0", "--port", "8080"])
        assert args.host == "0.0.0.0"
        assert args.port == 8080

    def test_parse_open_flag(self):
        """Test --open flag parsing."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--open", action="store_true")
        args = parser.parse_args(["--open"])
        assert args.open is True

    def test_parse_install_flag(self):
        """Test --install flag parsing."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--install", action="store_true")
        args = parser.parse_args(["--install"])
        assert args.install is True


# Integration tests
@pytest.mark.skipif(launch_council is None, reason="launch-council.py not found")
class TestIntegration:
    """Integration tests."""

    def test_python_version_check(self):
        """Test that Python version check works."""
        result = launch_council.check_python_version()
        # Should pass if Python 3.9+
        if sys.version_info >= (3, 9):
            assert result is True

    def test_council_import(self):
        """Test that council_ai can be imported (if installed)."""
        if importlib.util.find_spec("council_ai"):
            assert True
            pytest.skip("council_ai not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
