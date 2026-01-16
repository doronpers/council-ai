#!/usr/bin/env python3
"""
One-click launch script for Council AI Web App
Cross-platform: Works on Windows, macOS, and Linux

Launches the Council AI web interface for end users.
"""

import argparse
import importlib.util
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# Colors for output
try:
    if IS_WINDOWS:
        try:
            import colorama

            colorama.init()
        except ImportError:
            pass
    # ANSI color codes
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
except Exception:
    # Failed to set up colors (e.g., unsupported terminal)
    GREEN = YELLOW = RED = BLUE = CYAN = MAGENTA = RESET = BOLD = ""

QUIET = False


def print_status(message: str, color: str = "", force: bool = False):
    """Print a status message with optional color."""
    if QUIET and not force:
        return
    print(f"{color}{message}{RESET}")


def print_error(message: str):
    """Print an error message."""
    print_status(f"❌ {message}", RED, force=True)


def print_success(message: str):
    """Print a success message."""
    print_status(f"✅ {message}", GREEN)


def print_info(message: str):
    """Print an info message."""
    print_status(f"ℹ️  {message}", BLUE)


def print_warning(message: str):
    """Print a warning message."""
    print_status(f"⚠️  {message}", YELLOW)


def run_command(
    cmd: list, check: bool = True, capture_output: bool = False
) -> Tuple[int, str, str]:
    """
    Run a command and return the result.

    Returns:
        (returncode, stdout, stderr)
    """
    try:
        # Enforce UTF-8 on Windows for subprocesses
        env = os.environ.copy()
        if IS_WINDOWS:
            env["PYTHONUTF8"] = "1"

        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            shell=IS_WINDOWS and len(cmd) == 1,
            env=env,
        )
        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""
        return (result.returncode, stdout, stderr)
    except subprocess.CalledProcessError as e:
        if capture_output:
            return (e.returncode, e.stdout or "", e.stderr or "")
        raise
    except FileNotFoundError:
        return (1, "", "Command not found")


def check_python_version() -> bool:
    """Check if Python 3.9+ is installed."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python 3.9+ required, found {version.major}.{version.minor}")
        print_info("Please upgrade Python: https://www.python.org/downloads/")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_council_installed() -> Tuple[bool, bool]:
    """
    Check if council-ai is installed.

    Returns:
        (is_installed, is_editable)
    """
    try:
        # Try finding spec
        is_installed = importlib.util.find_spec("council_ai") is not None

        # Check if it's installed in editable mode (development)
        try:
            spec = importlib.util.find_spec("council_ai")
            if spec and spec.origin:
                # Check if it's from the current directory (editable install)
                current_dir = Path(__file__).parent.resolve()
                origin_path = Path(spec.origin).parent.parent
                is_editable = (
                    current_dir in origin_path.parents or current_dir == origin_path.parent
                )
            else:
                is_editable = False
        except Exception:
            # Could not determine install type
            is_editable = False

        return (is_installed, is_editable)
    except ImportError:
        return (False, False)


def check_web_dependencies() -> bool:
    """Check if web dependencies (uvicorn, fastapi) are installed."""
    try:
        has_fastapi = importlib.util.find_spec("fastapi") is not None
        has_uvicorn = importlib.util.find_spec("uvicorn") is not None
        return has_fastapi and has_uvicorn
    except ImportError:
        return False


def check_api_keys() -> Tuple[bool, Optional[str]]:
    """
    Check if at least one API key is configured.

    Returns:
        (has_key, provider_name)
    """
    api_keys = {
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "openai": os.environ.get("OPENAI_API_KEY"),
        "gemini": os.environ.get("GEMINI_API_KEY"),
    }

    # Also check for COUNCIL_API_KEY (generic)
    council_key = os.environ.get("COUNCIL_API_KEY")

    for provider, key in api_keys.items():
        if key and key.strip() and "your-" not in key.lower() and "here" not in key.lower():
            return (True, provider)

    if council_key and council_key.strip() and "your-" not in council_key.lower():
        return (True, "generic")

    return (False, None)


def install_council(editable: bool = True) -> bool:
    """Install council-ai package."""
    print_info("Installing council-ai...")

    if editable:
        cmd = [sys.executable, "-m", "pip", "install", "-e", ".[web]"]
    else:
        cmd = [sys.executable, "-m", "pip", "install", "council-ai[web]"]

    returncode, stdout, stderr = run_command(cmd, check=False, capture_output=True)

    if returncode != 0:
        print_error("Failed to install council-ai")
        print_info(f"Error: {stderr}")
        return False

    print_success("council-ai installed successfully")
    return True


def check_port_available(port: int) -> bool:
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def open_browser(url: str) -> bool:
    """Open a URL in the default browser (platform-specific)."""
    try:
        if IS_WINDOWS:
            os.startfile(url)
        elif IS_MAC:
            subprocess.run(["open", url], check=False)
        elif IS_LINUX:
            subprocess.run(["xdg-open", url], check=False)
        else:
            return False
        return True
    except Exception:
        return False


def launch_web_app(
    host: str = "127.0.0.1", port: int = 8000, reload: bool = True, open_browser_flag: bool = False
) -> int:
    """Launch the Council AI web app."""
    url = f"http://{host}:{port}"

    # Check if port is available
    if not check_port_available(port):
        print_warning(f"Port {port} is already in use")
        print_info("Trying to use the existing service...")
        if open_browser_flag:
            open_browser(url)
        print_success(f"Web app should be available at {url}")
        return 0

    print_info(f"Launching Council AI web app on {url}")
    print_status("💡 Tip: Press Ctrl+C to stop the server", YELLOW)
    if not QUIET:
        print()

    # Welcome message
    welcome = f"""
{BOLD}{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
{BOLD}  🏛️  Council AI Web App{RESET}
{BOLD}{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}

{BOLD}Access the web interface at:{RESET}
  {CYAN}{url}{RESET}

{BOLD}Features:{RESET}
  • Consult with multiple AI personas
  • Choose from 12 domain presets
  • Multiple consultation modes (synthesis, debate, vote)
  • Text-to-speech support (if configured)
  • Consultation history

{BOLD}To stop:{RESET} Press {CYAN}Ctrl+C{RESET}

"""
    if not QUIET:
        print(welcome)

    # Open browser if requested
    if open_browser_flag:
        print_info("Opening browser...")
        # Small delay to let server start
        import time

        time.sleep(1)
        if not open_browser(url):
            print_warning("Could not open browser automatically")
            print_info(f"Please open {url} manually")

    # Launch the web app
    try:
        # Use the council CLI command
        cmd = [sys.executable, "-m", "council_ai.cli", "web", "--host", host, "--port", str(port)]
        if reload:
            cmd.append("--reload")

        # Enforce UTF-8 on Windows for the web app process
        env = os.environ.copy()
        if IS_WINDOWS:
            env["PYTHONUTF8"] = "1"

        returncode = subprocess.call(cmd, env=env)
        return returncode
    except KeyboardInterrupt:
        print()
        print_info("Web app stopped by user")
        return 0
    except Exception as e:
        print_error(f"Failed to launch web app: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Launch the Council AI web app")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the web server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the web server (default: 8000)"
    )
    parser.add_argument(
        "--no-reload", action="store_true", help="Disable auto-reload (production mode)"
    )
    parser.add_argument("--open", action="store_true", help="Open browser automatically")
    parser.add_argument("--install", action="store_true", help="Install council-ai if not found")
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Silent mode (suppress non-error output)",
    )
    args = parser.parse_args()

    global QUIET
    QUIET = args.quiet

    print_status(f"{BOLD}🏛️  Council AI Launch Script{RESET}\n")

    # Check Python version
    print_status("Checking prerequisites...", CYAN)
    if not check_python_version():
        return 1

    # Check if council-ai is installed
    is_installed, is_editable = check_council_installed()
    if not is_installed:
        print_warning("council-ai is not installed")
        if args.install:
            if not install_council(editable=True):
                return 1
        else:
            print_info("Run with --install to install automatically")
            print_info("Or install manually: pip install -e '.[web]'")
            return 1
    else:
        print_success("council-ai is installed")
        if is_editable:
            print_info("Running in development mode (editable install)")

    # Check web dependencies
    if not check_web_dependencies():
        print_warning("Web dependencies (uvicorn, fastapi) are missing")
        print_info("Installing web dependencies...")
        if not install_council(editable=is_editable):
            return 1
    else:
        print_success("Web dependencies are available")

    # Check API keys (warning only, not blocking)
    has_key, provider = check_api_keys()
    if not has_key:
        print_warning("No API key detected")
        print_info("You can set one of:")
        print_info("  • ANTHROPIC_API_KEY (for Claude)")
        print_info("  • OPENAI_API_KEY (for GPT-4)")
        print_info("  • GEMINI_API_KEY (for Gemini)")
        print_info("  • COUNCIL_API_KEY (generic)")
        print_info("")
        print_info("The web app will start, but you'll need to configure an API key in the UI")
    else:
        print_success(f"API key detected for {provider}")

    if not QUIET:
        print()

    # Launch web app
    return launch_web_app(
        host=args.host, port=args.port, reload=not args.no_reload, open_browser_flag=args.open
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print_info("Launch cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
