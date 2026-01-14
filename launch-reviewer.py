#!/usr/bin/env python3
"""
LLM Response Reviewer Launcher

Quick launch script for the LLM Response Reviewer web application.
Opens directly to the reviewer interface.

Usage:
    python launch-reviewer.py [--port PORT] [--no-browser]
"""

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_dependencies():
    """Check that required dependencies are installed."""
    try:
        import uvicorn
        import fastapi
        return True
    except ImportError as e:
        print(f"Missing dependency: {e.name}")
        print("\nPlease install dependencies:")
        print("  pip install council-ai")
        print("  # or")
        print("  pip install -e .")
        return False


def check_env_file():
    """Check if .env file exists and has API keys configured."""
    env_path = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"

    if not env_path.exists():
        if env_example.exists():
            print("No .env file found.")
            print(f"\nPlease copy {env_example} to {env_path} and add your API keys:")
            print(f"  cp {env_example} {env_path}")
            print("  # Then edit .env to add your API keys")
        else:
            print("No .env file found. Please create one with your API keys.")
        return False

    # Check if any real API keys are set
    with open(env_path) as f:
        content = f.read()
        has_real_key = False
        for line in content.split('\n'):
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                value = value.strip()
                if value and 'your-' not in value.lower() and '-here' not in value.lower():
                    has_real_key = True
                    break

        if not has_real_key:
            print("Warning: No API keys appear to be configured in .env")
            print("The reviewer will require an API key to function.")
            print("\nPlease edit .env and add at least one API key:")
            print("  - ANTHROPIC_API_KEY for Claude")
            print("  - OPENAI_API_KEY for GPT")
            print("  - AI_GATEWAY_API_KEY for Vercel AI Gateway")
            # Don't return False - let user proceed and enter key in UI

    return True


def find_open_port(start_port=8765, max_attempts=10):
    """Find an available port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    return start_port  # Return default and let it fail if needed


def main():
    parser = argparse.ArgumentParser(
        description="Launch the LLM Response Reviewer web application"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8765,
        help="Port to run the server on (default: 8765)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open the browser"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    args = parser.parse_args()

    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)

    check_env_file()  # Warning only, don't exit

    # Find available port
    port = find_open_port(args.port)
    if port != args.port:
        print(f"Port {args.port} is in use, using {port} instead")

    url = f"http://{args.host}:{port}/reviewer"

    print("\n" + "=" * 60)
    print("  LLM Response Reviewer")
    print("  Supreme Court-style review of AI responses")
    print("=" * 60)
    print(f"\n  Starting server at: {url}")
    print(f"  Main Council UI:    http://{args.host}:{port}/")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    # Open browser after a short delay
    if not args.no_browser:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(url)

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "council_ai.webapp.app:app",
            host=args.host,
            port=port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")


if __name__ == "__main__":
    main()
