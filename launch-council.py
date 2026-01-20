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
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple


def load_env_file(env_path: Optional[Path] = None) -> None:
    """Load environment variables from .env file if it exists."""
    if env_path is None:
        env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        try:
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue
                    # Parse KEY=VALUE
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        # Skip placeholder values
                        if value and "your-" not in value.lower() and "here" not in value.lower():
                            os.environ[key] = value
        except Exception:
            # Silently fail if .env can't be read
            pass


# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    try:
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
    cmd: list,
    check: bool = True,
    capture_output: bool = False,
    cwd: Optional[Path] = None,
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

        # On Windows, .cmd and .bat files need shell=True or cmd.exe wrapper
        use_shell = False
        if IS_WINDOWS and cmd:
            exe_path = str(cmd[0]).lower()
            if exe_path.endswith((".cmd", ".bat")) or (len(cmd) == 1 and not Path(cmd[0]).suffix):
                use_shell = True

        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True,
            shell=use_shell,
            env=env,
            cwd=str(cwd) if cwd is not None else None,
        )
        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""
        return (result.returncode, stdout, stderr)
    except subprocess.CalledProcessError as e:
        if capture_output:
            return (e.returncode, e.stdout or "", e.stderr or "")
        raise
    except FileNotFoundError:
        cmd_name = cmd[0] if cmd else "command"
        error_msg = f"Command '{cmd_name}' not found. Ensure it is installed and in your PATH."
        return (1, "", error_msg)


def resolve_executable(candidates: list[str]) -> Optional[str]:
    """
    Resolve an executable path from a list of candidate command names.

    On Windows, this handles common cases like `npm.cmd` vs `npm`.
    """
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def check_python_version() -> bool:
    """Check if Python 3.11+ is installed."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_error(f"Python 3.11+ required, found {version.major}.{version.minor}")
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
    """Check if web dependencies (uvicorn, fastapi, aiohttp) are installed."""
    try:
        has_fastapi = importlib.util.find_spec("fastapi") is not None
        has_uvicorn = importlib.util.find_spec("uvicorn") is not None
        has_aiohttp = importlib.util.find_spec("aiohttp") is not None
        return has_fastapi and has_uvicorn and has_aiohttp
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


def detect_personal_integration() -> Tuple[bool, Optional[str]]:
    """
    Detect if council-ai-personal is available.

    Returns:
        (is_detected, repo_path)
    """
    try:
        from council_ai.core.personal_integration import detect_personal_repo

        repo_path = detect_personal_repo()
        if repo_path:
            return (True, str(repo_path))
    except ImportError:
        # Module not available yet (during initial setup)
        pass
    except Exception:
        pass

    # Fallback: check common locations
    script_dir = Path(__file__).parent.resolve()
    sibling_path = script_dir.parent / "council-ai-personal"
    if sibling_path.exists() and (sibling_path / "personal").exists():
        return (True, str(sibling_path))

    home_path = Path.home() / "council-ai-personal"
    if home_path.exists() and (home_path / "personal").exists():
        return (True, str(home_path))

    return (False, None)


def is_first_run() -> bool:
    """
    Check if this is the first run of Council AI.

    Returns:
        True if this appears to be the first run
    """
    config_dir = Path.home() / ".config" / "council-ai"
    first_run_flag = config_dir / ".first_run_complete"

    # If flag exists, not first run
    if first_run_flag.exists():
        return False

    # Check if config directory is empty or doesn't exist
    if not config_dir.exists():
        return True

    # Check if config.yaml exists and has meaningful content
    config_file = config_dir / "config.yaml"
    if not config_file.exists():
        return True

    try:
        with open(config_file, encoding="utf-8") as f:
            content = f.read().strip()
            # If config is empty or just has defaults, consider it first run
            if not content or len(content) < 50:
                return True
    except Exception:
        return True

    return False


def mark_first_run_complete() -> None:
    """Mark that first run setup is complete."""
    config_dir = Path.home() / ".config" / "council-ai"
    config_dir.mkdir(parents=True, exist_ok=True)
    first_run_flag = config_dir / ".first_run_complete"
    first_run_flag.touch()


def offer_personal_integration(repo_path: str) -> bool:
    """
    Offer to integrate council-ai-personal.

    Args:
        repo_path: Path to council-ai-personal repository

    Returns:
        True if user accepted integration, False otherwise
    """
    if QUIET:
        return False

    print_info(f"\n📦 Found council-ai-personal at: {repo_path}")
    print_info("This repository contains personal configurations and personas.")
    print_status(
        "Would you like to integrate it now? (This will copy configs to ~/.config/council-ai/)",
        CYAN,
    )

    try:
        response = input("Integrate now? [Y/n]: ").strip().lower()
        if response in ("", "y", "yes"):
            return True
    except (EOFError, KeyboardInterrupt):
        print()
        return False

    return False


def install_council(editable: bool = True) -> bool:
    """Install council-ai package."""
    print_info("Upgrading pip...")

    # Upgrade pip first
    upgrade_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
    returncode, _, _ = run_command(upgrade_cmd, check=False, capture_output=True)

    if returncode == 0:
        print_success("pip upgraded successfully")
    else:
        print_warning("Could not upgrade pip (continuing anyway)")

    # Check for shared-ai-utils sibling directory (development mode)
    script_dir = Path(__file__).parent.resolve()
    shared_utils_dir = script_dir.parent / "shared-ai-utils"

    if shared_utils_dir.exists():
        print_info(f"Found local dependency: {shared_utils_dir.name}")
        print_info("Installing shared-ai-utils from local path (development mode)...")
        cmd_shared = [sys.executable, "-m", "pip", "install", "-e", str(shared_utils_dir)]
        rc, _, err = run_command(cmd_shared, check=False, capture_output=True)
        if rc != 0:
            print_warning(f"Failed to install shared-ai-utils from local path: {err}")
            print_info("Falling back to pip dependency resolution...")
        else:
            print_success("shared-ai-utils installed from local path")
    else:
        print_info("No local shared-ai-utils found (standalone mode)")
        print_info(
            "shared-ai-utils will be installed automatically from git dependency in pyproject.toml"
        )

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


def save_host_config(host: str, port: int, config_file: str = ".council_host"):
    """Save host address to configuration file."""
    try:
        path = Path(config_file)
        # Use full address if host is not localhost, else just localhost
        address = host
        if host == "0.0.0.0":
            address = get_local_ip()

        content = f"{address}:{port}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print_warning(f"Could not save host config: {e}")
        return False


def get_stored_host(config_file: str = ".council_host") -> Optional[str]:
    """Read stored host from configuration file."""
    try:
        path = Path(config_file)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass
    return None


def find_open_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        # Check if port is available by trying to connect to it
        # If we can connect, something is already listening
        is_listening = False
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(0.1)
            result = test_socket.connect_ex(("127.0.0.1", port))
            test_socket.close()
            if result == 0:
                # Port is in use (we could connect)
                is_listening = True
        except Exception:
            pass

        if is_listening:
            continue

        # Port appears free, try to bind to it to confirm
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    # If no port found, return start_port anyway (caller should handle the error)
    return start_port


def check_port_available(port: int) -> Tuple[bool, Optional[int]]:
    """
    Check if a port is available.

    Returns:
        (is_available, pid_using_port)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True, None
        except OSError:
            # Try to find PID using lsof on Mac/Linux
            pid = None
            if not IS_WINDOWS:
                try:
                    result = subprocess.run(
                        ["lsof", "-t", f"-i:{port}"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.stdout.strip():
                        pid = int(result.stdout.strip().split("\n")[0])
                except Exception:
                    pass
            return False, pid


def kill_process_on_port(port: int) -> bool:
    """Kill any process running on the specified port."""
    is_avail, pid = check_port_available(port)
    if is_avail:
        return True

    if pid:
        print_info(f"Killing process {pid} on port {port}...")
        try:
            import signal

            os.kill(pid, signal.SIGTERM)
            # Wait a moment for it to die
            import time

            time.sleep(1)
            return check_port_available(port)[0]
        except Exception as e:
            print_error(f"Failed to kill process {pid}: {e}")
            return False
    return False


def open_browser(url: str) -> bool:
    """Open a URL in the default browser (platform-specific)."""
    try:
        if IS_WINDOWS:
            os.startfile(url)  # type: ignore[attr-defined]
        elif IS_MAC:
            subprocess.run(["open", url], check=False)
        elif IS_LINUX:
            subprocess.run(["xdg-open", url], check=False)
        else:
            return False
        return True
    except Exception:
        return False


def get_local_ip() -> str:
    """Get the local IP address of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def is_council_service(url: str) -> bool:
    """Check if the service at the given URL is actually Council AI."""
    try:
        import json
        import urllib.request

        # Try to fetch the /api/info endpoint which Council AI provides
        info_url = f"{url}/api/info" if not url.endswith("/") else f"{url}api/info"
        req = urllib.request.Request(info_url)
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            # Council AI's /api/info returns a structure with "providers", "domains", etc.
            # Check for these characteristic fields
            if isinstance(data, dict):
                # Council AI has these specific fields in /api/info
                if "providers" in data and "domains" in data and "defaults" in data:
                    return True
        return False
    except Exception:
        # If we can't verify, assume it's NOT Council AI to be safe
        return False


def launch_web_app(
    host: str = "127.0.0.1", port: int = 8000, reload: bool = True, open_browser_flag: bool = False
) -> int:
    """Launch the Council AI web app."""
    display_host = host
    if host == "0.0.0.0":
        display_host = get_local_ip()

    url = f"http://{display_host}:{port}"

    # Check if port is available
    is_avail, pid = check_port_available(port)
    if not is_avail:
        print_warning(f"Port {port} is already in use")
        if pid:
            print_info(f"Process {pid} is currently using this port.")
            if not IS_WINDOWS:
                print_info(f"To kill it, run: kill {pid}")
            else:
                print_info(f"To kill it, run: taskkill /PID {pid} /F")

        # Verify it's actually Council AI before assuming it is
        print_info("Checking if the service on this port is Council AI...")
        if is_council_service(url):
            print_info("Council AI service detected on this port.")
            if open_browser_flag:
                open_browser(url)
            print_success(f"Web app should be available at {url}")
            return 2  # Special code for "already running"
        else:
            print_error(f"Port {port} is in use by a different service (not Council AI)")
            # Try to find an available port automatically
            alt_port = find_open_port(port + 1, max_attempts=5)
            if alt_port != port:
                print_info(f"Found available port: {alt_port}")
                print_info(f"Re-run with: --port {alt_port}")
                print_info(
                    "Or the script will automatically use the next available port on next run."
                )
            else:
                print_info("Please use a different port or stop the service using this port.")
                print_info("You can:")
                print_info("  1. Use --port <different_port> to use a different port")
                print_info("  2. Use --kill to attempt to free the port (use with caution)")
            return 1  # Error: port conflict with non-Council service

    print_info(f"Launching Council AI web app on {url}")
    print_status("💡 Tip: Press Ctrl+C to stop the server", YELLOW)
    if not QUIET:
        print()

    # Check personal integration status
    personal_status = ""
    try:
        from council_ai.core.personal_integration import get_personal_status

        status = get_personal_status()
        if status.get("configured"):
            personal_status = f"\n{BOLD}Personal Integration:{RESET} ✅ Active"
        elif status.get("detected"):
            personal_status = (
                f"\n{BOLD}Personal Integration:{RESET} ⚠️  Detected but not integrated"
                f"\n  Run 'council personal integrate' to activate"
            )
    except Exception:
        pass

    # Welcome message
    access_msg = f"  {CYAN}{url}{RESET}"
    if host == "0.0.0.0":
        access_msg += f"\n  {CYAN}http://{socket.gethostname()}.local:{port}{RESET} (mDNS)"

    welcome = f"""
{BOLD}{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
{BOLD}  🏛️  Council AI Web App{RESET}
{BOLD}{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}

{BOLD}Access the web interface at:{RESET}
{access_msg}{personal_status}

{BOLD}Features:{RESET}
  • Consult with multiple AI personas
  • Choose from 12+ domain presets
  • Multiple consultation modes (synthesis, debate, vote)
  • Text-to-speech support (if configured)
  • Consultation history
  • Personal configurations (if integrated)

{BOLD}To stop:{RESET} Press {CYAN}Ctrl+C{RESET}

"""
    if not QUIET:
        print(welcome)

    # Open browser if requested
    if open_browser_flag:
        print_info("Opening browser...")
        # Small delay to let server start
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


def check_npm_installed() -> bool:
    """Check if npm is installed."""
    node_candidates = ["node"]
    npm_candidates = ["npm"]
    if IS_WINDOWS:
        node_candidates = ["node.exe", "node.cmd", "node.bat", "node"]
        npm_candidates = ["npm.cmd", "npm.exe", "npm.bat", "npm"]

    node_exe = resolve_executable(node_candidates)
    npm_exe = resolve_executable(npm_candidates)
    if not node_exe or not npm_exe:
        return False

    # Verify they actually execute (without relying on Windows shell resolution).
    node_rc, _, _ = run_command([node_exe, "--version"], check=False, capture_output=True)
    if node_rc != 0:
        return False
    npm_rc, _, _ = run_command([npm_exe, "--version"], check=False, capture_output=True)
    return npm_rc == 0


def diagnose_npm_issue() -> str:
    """Diagnose npm installation issues and return helpful message."""
    try:
        node_candidates = ["node"]
        npm_candidates = ["npm"]
        if IS_WINDOWS:
            node_candidates = ["node.exe", "node.cmd", "node.bat", "node"]
            npm_candidates = ["npm.cmd", "npm.exe", "npm.bat", "npm"]

        node_exe = resolve_executable(node_candidates)
        npm_exe = resolve_executable(npm_candidates)

        if not node_exe:
            return "Node.js is not installed or not in PATH"

        node_rc, node_out, node_err = run_command(
            [node_exe, "--version"], check=False, capture_output=True
        )
        node_version = (node_out or node_err).strip()
        if node_rc != 0 or not node_version:
            return "Node.js is installed but could not be executed (check PATH / App Execution Aliases)"

        if not npm_exe:
            return (
                f"Node.js {node_version} is installed, but npm is not in your PATH.\n"
                "This usually means:\n"
                "  1. Node.js was installed but PATH wasn't updated\n"
                "  2. You need to restart your terminal/command prompt\n"
                "  3. npm wasn't added to PATH during installation\n\n"
                "Solutions:\n"
                "  • Restart your terminal/command prompt\n"
                "  • Run: fix-npm-path.bat (diagnostic and fix guide)\n"
                "  • Reinstall Node.js and ensure 'Add to PATH' is checked"
            )

        npm_rc, npm_out, npm_err = run_command(
            [npm_exe, "--version"], check=False, capture_output=True
        )
        npm_version = (npm_out or npm_err).strip()
        if npm_rc != 0 or not npm_version:
            return (
                f"Found npm at: {npm_exe}\n"
                "…but it failed to run. Try restarting your terminal and re-running this launcher."
            )

        return f"npm is working (version: {npm_version})"
    except Exception as e:
        return f"Could not diagnose npm issue: {e}"


def get_npm_install_instructions() -> str:
    """Get instructions for installing npm/Node.js."""
    if IS_MAC:
        return (
            "📦 Install Node.js:\n"
            "   Option 1: Download from https://nodejs.org/ (LTS version recommended)\n"
            "   Option 2: Use Homebrew: brew install node"
        )
    elif IS_WINDOWS:
        return (
            "📦 Install Node.js:\n"
            "   1. Visit https://nodejs.org/\n"
            "   2. Download the Windows Installer (LTS version recommended)\n"
            "   3. Run the installer and follow the setup wizard\n"
            "   4. Restart your command prompt/PowerShell after installation\n"
            "   5. Verify: node --version and npm --version"
        )
    else:
        return (
            "📦 Install Node.js:\n"
            "   Option 1: Download from https://nodejs.org/\n"
            "   Option 2: Use package manager:\n"
            "     • Debian/Ubuntu: sudo apt-get install nodejs npm\n"
            "     • RHEL/CentOS: sudo yum install nodejs npm\n"
            "     • Arch: sudo pacman -S nodejs npm"
        )


def build_frontend() -> bool:
    """Install dependencies and build the frontend."""
    # Check npm first
    if not check_npm_installed():
        print_error("npm/Node.js is not installed or not in PATH")
        print_info("")
        print_info("To build the frontend, you need to install Node.js:")
        print_info("")
        instructions = get_npm_install_instructions()
        for line in instructions.split("\n"):
            print_info(f"  {line}")
        print_info("")
        print_info("After installing Node.js:")
        print_info("  1. Restart your terminal/command prompt")
        print_info("  2. Run this launcher again")
        print_info("")
        print_info("Alternatively, you can use Council AI via CLI:")
        print_info('  council consult "Your question"')
        print_info("  council interactive")
        return False

    print_info("Building frontend assets (this may take a minute)...")

    try:
        project_root = Path(__file__).parent.resolve()
        npm_candidates = ["npm"]
        if IS_WINDOWS:
            npm_candidates = ["npm.cmd", "npm.exe", "npm.bat", "npm"]

        npm_exe = resolve_executable(npm_candidates)
        if not npm_exe:
            print_error("npm command not found")
            print_info("")
            diagnosis = diagnose_npm_issue()
            print_info("Diagnosis:")
            for line in diagnosis.split("\n"):
                print_info(f"  {line}")
            return False

        # Install dependencies
        print_status("Installing npm dependencies...", CYAN)
        returncode, stdout, stderr = run_command(
            [npm_exe, "install"], check=False, capture_output=True, cwd=project_root
        )
        if returncode != 0:
            print_error("Failed to install npm dependencies")
            if stderr:
                print_info(f"Error output: {stderr}")
            if stdout:
                print_info(f"Output: {stdout}")
            print_info("")
            print_info("Troubleshooting:")
            print_info("  • Ensure Node.js is properly installed: node --version")
            print_info("  • Try running 'npm install' manually in the project directory")
            if "Command" in stderr and "not found" in stderr:
                print_info("")
                print_info("Diagnosis:")
                diagnosis = diagnose_npm_issue()
                for line in diagnosis.split("\n"):
                    print_info(f"  {line}")
            return False

        # Build
        print_status("Building React app...", CYAN)
        returncode, stdout, stderr = run_command(
            [npm_exe, "run", "build"], check=False, capture_output=True, cwd=project_root
        )
        if returncode != 0:
            print_error("Failed to build frontend")
            if stderr:
                print_info(f"Error output: {stderr}")
            if stdout:
                print_info(f"Output: {stdout}")
            print_info("")
            print_info("Troubleshooting:")
            print_info("  • Check that all npm dependencies installed correctly")
            print_info("  • Try running 'npm run build' manually in the project directory")
            return False

        print_success("Frontend built successfully")
        return True
    except FileNotFoundError:
        print_error("npm command not found")
        print_info("Node.js/npm is not installed or not in your PATH")
        print_info("")
        instructions = get_npm_install_instructions()
        for line in instructions.split("\n"):
            print_info(f"  {line}")
        return False
    except Exception as e:
        print_error(f"Build failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_frontend_ready() -> bool:
    """
    Check if frontend assets are built, and offer to build them if not.

    Returns:
        bool: True if ready to launch, False otherwise.
    """
    # Check for built index.html
    # Path logic: launch-council.py is in root
    # Build output is in src/council_ai/webapp/static/index.html
    script_dir = Path(__file__).parent.resolve()
    static_index = script_dir / "src" / "council_ai" / "webapp" / "static" / "index.html"

    if static_index.exists():
        return True

    print_warning("Frontend assets not found (fresh install?)")

    if not check_npm_installed():
        print_error("npm is not available. Cannot build frontend.")
        print_info("")

        # Diagnose the issue
        diagnosis = diagnose_npm_issue()
        print_info("Diagnosis:")
        for line in diagnosis.split("\n"):
            print_info(f"  {line}")
        print_info("")

        if IS_WINDOWS:
            print_info("🔧 Quick fix tools:")
            print_info("   • Run: fix-npm-path.bat (diagnostic and fix guide)")
            print_info("   • Run: install-nodejs.bat (reinstall Node.js)")
            print_info("")

        print_info("💡 Alternative: Use Council AI via CLI (no npm required):")
        print_info('   council consult "Your question"')
        print_info("   council interactive")
        print_info("   Or use: launch-council-cli.bat")
        return False

    if not QUIET:
        # If interactive or force, ask user
        # But for simplified launcher, we might just want to do it or fail
        # Let's try to build automatically if we can
        print_info("Frontend needs to be built before first launch.")
        try:
            # Simple timeout-based input implementation or just go ahead
            # For this script, let's just do it
            if not build_frontend():
                return False
        except Exception:
            return False

    return True


def main():
    """Main entry point."""
    # Load .env file early if it exists
    load_env_file()

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
    parser.add_argument(
        "--network",
        action="store_true",
        help="Enable network access (binds to 0.0.0.0 instead of 127.0.0.1)",
    )
    parser.add_argument(
        "--retry",
        action="store_true",
        help="Automatically restart the server if it crashes",
    )
    parser.add_argument(
        "--kill",
        action="store_true",
        help="Kill any existing process on the port before starting",
    )
    parser.add_argument(
        "--role",
        choices=["host", "satellite", "auto"],
        default="host",
        help="Role to run as (host: run server, satellite: connect to host)",
    )
    parser.add_argument(
        "--host-file",
        default=".council_host",
        help="File to store/read host address (default: .council_host)",
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip frontend build check (use CLI mode only)",
    )
    parser.add_argument(
        "--open-nodejs",
        action="store_true",
        help="Open Node.js download page in browser",
    )
    args = parser.parse_args()

    global QUIET
    QUIET = args.quiet

    host = args.host
    if args.network and host == "127.0.0.1":
        host = "0.0.0.0"

    if not QUIET:
        print_status(f"{BOLD}🏛️  Council AI Launch Script{RESET}\n")

    # Handle auto role
    if args.role == "auto":
        is_avail, _ = check_port_available(args.port)
        if not is_avail:
            # Local port is busy, verify it's actually Council AI before acting as satellite
            test_url = f"http://127.0.0.1:{args.port}"
            print_info(f"Port {args.port} is in use. Verifying if it's Council AI...")
            if is_council_service(test_url):
                print_status("🏛️  Local Council AI instance detected. Acting as satellite.", CYAN)
                args.role = "satellite"
            else:
                print_warning(f"Port {args.port} is in use by a different service (not Council AI)")
                print_info("Will launch Council AI on a different port instead.")
                args.role = "host"
        else:
            # Local port is free. Check if there's a remote host we should connect to.
            stored_host = get_stored_host(args.host_file)
            if stored_host and "127.0.0.1" not in stored_host and "localhost" not in stored_host:
                # Try to see if remote host is reachable
                host_part = stored_host.split(":")[0]
                port_part = int(stored_host.split(":")[1]) if ":" in stored_host else args.port

                print_info(f"Checking for remote host at {stored_host}...")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.5)
                    try:
                        s.connect((host_part, port_part))
                        print_status(
                            f"🌐 Remote Council AI host found at {stored_host}. Acting as satellite.",
                            CYAN,
                        )
                        args.role = "satellite"
                    except (socket.timeout, OSError):
                        print_info("Remote host not reachable. Launching as local host.")
                        args.role = "host"
            else:
                args.role = "host"

    # Execute satellite logic if role is satellite
    if args.role == "satellite":
        stored_host = get_stored_host(args.host_file) or f"127.0.0.1:{args.port}"
        url = f"http://{stored_host}"
        if ":" not in stored_host:
            url = f"http://{stored_host}:{args.port}"

        # Verify it's actually Council AI before connecting
        print_info(f"Verifying Council AI service at {url}...")
        if not is_council_service(url):
            print_error(f"Service at {url} is not Council AI")
            print_info("Switching to host mode to launch Council AI on a different port...")
            args.role = "host"
        else:
            print_info(f"Connecting to Council AI at {url}...")
            if open_browser(url):
                print_success("Browser opened successfully")
                return 0
            else:
                print_error(f"Failed to open browser. Please visit {url} manually.")
                return 1

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

    # Handle --open-nodejs flag
    if args.open_nodejs:
        nodejs_url = "https://nodejs.org/"
        print_info(f"Opening Node.js download page: {nodejs_url}")
        if open_browser(nodejs_url):
            print_success("Browser opened. Download the LTS version for Windows.")
        else:
            print_info(f"Please visit: {nodejs_url}")
        return 0

    # Check Frontend Build (New Step)
    if not args.skip_frontend:
        frontend_ready = check_frontend_ready()
        if not frontend_ready:
            # Offer CLI mode as alternative
            print_info("")
            print_info("💡 You can use Council AI via CLI without Node.js:")
            print_info('   council consult "Your question"')
            print_info("   council interactive")
            print_info("")
            print_info("Or install Node.js and try again:")
            print_info("   Run: python launch-council.py --open-nodejs")
            return 1
    else:
        print_info("Skipping frontend build check (CLI mode)")

    # Check for first run and personal integration
    if is_first_run():
        print_info("\n🎉 Welcome to Council AI! This appears to be your first launch.")
        print_info("We'll help you get set up.\n")

        # Check for personal integration
        personal_detected, personal_path = detect_personal_integration()
        if personal_detected and personal_path:
            if offer_personal_integration(personal_path):
                print_info("Integrating council-ai-personal...")
                try:
                    from council_ai.core.personal_integration import integrate_personal

                    if integrate_personal(Path(personal_path)):
                        print_success("Personal integration completed!")
                    else:
                        print_warning("Personal integration failed, but continuing...")
                except Exception as e:
                    print_warning(f"Personal integration error: {e}")
                    print_info("You can integrate later with: council personal integrate")

        # Mark first run as complete
        mark_first_run_complete()

    # Check API keys (warning only, not blocking)
    has_key, provider = check_api_keys()
    if not has_key:
        print_warning("No API key detected")
        print_info("You can set one of:")
        print_info("  • ANTHROPIC_API_KEY (for Claude) - https://console.anthropic.com/")
        print_info("  • OPENAI_API_KEY (for GPT-4) - https://platform.openai.com/api-keys")
        print_info("  • GEMINI_API_KEY (for Gemini) - https://ai.google.dev/")
        print_info("  • COUNCIL_API_KEY (generic)")
        print_info("")
        print_info("The web app will start, but you'll need to configure an API key in the UI")
        print_info("Or run 'council init' for guided setup")
    else:
        print_success(f"API key detected for {provider}")

    if not QUIET:
        print()
    # Handle --kill flag
    if args.kill:
        kill_process_on_port(args.port)

    # Find available port if not specified
    port = args.port
    if not args.kill:  # If we didn't kill, find an open one
        port = find_open_port(args.port)
        if port != args.port:
            print_warning(f"Port {args.port} is in use, using {port} instead")

    # Save host config if we are hosting and it's a network host
    host_to_save = host
    if args.network or host != "127.0.0.1":
        save_host_config(host_to_save, port, args.host_file)
        print_info(f"Host configuration saved to {args.host_file}")

    # Launch web app
    while True:
        exit_code = launch_web_app(
            host=host, port=port, reload=not args.no_reload, open_browser_flag=args.open
        )

        # Exit if successful (0) or if we're not retrying
        if not args.retry:
            return exit_code

        # If already running (2), don't crash loop, just message and exit 0
        if exit_code == 2:
            print_info("Active instance detected. Keeping it alive.")
            # For persistent mode, we'll just wait indefinitely to keep the script alive
            # actually, maybe it's better to just return 0 to avoid multiple supervisors.
            return 0

        # Only retry on actual errors/crashes
        if exit_code == 0:
            return 0

        print_warning("Server crashed or exited with error. Restarting in 3 seconds...")
        import time

        time.sleep(3)


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
