#!/bin/bash
# Council AI - LAN Access Launcher
# Binds to your local IP so other devices can connect

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Launch the web app with network flag
./launch-council-web.command --network
