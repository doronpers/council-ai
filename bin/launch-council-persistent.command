#!/bin/bash
# Council AI - Persistent Launcher
# Keeps the server running even if it crashes

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Launch with retry flag, without opening browser automatically (to avoid tab spam on restart)
# We use python3 directly instead of the wrapper to control flags precisely
python3 launch-council.py --retry --port 8000
