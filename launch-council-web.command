#!/bin/bash
# Council AI - Desktop Launcher for Web UI
# Double-click this file to launch the Council AI web interface
# macOS: Make executable with: chmod +x launch-council-web.command

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Clear screen and show banner
clear
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║              🏛️  Council AI Web Interface                 ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 not found!${NC}"
    echo "Please install Python 3.11+ to run Council AI."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 detected: $(python3 --version)"
echo ""

# Check if council-ai is installed
if ! python3 -c "import council_ai" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Council AI not installed"
    echo -e "${BLUE}ℹ${NC}  Installing in development mode..."

    # Check for shared-ai-utils sibling directory
    SHARED_UTILS_DIR="../shared-ai-utils"
    if [ -d "$SHARED_UTILS_DIR" ]; then
        echo -e "${BLUE}ℹ${NC}  Installing local dependency: shared-ai-utils..."
        python3 -m pip install -e "$SHARED_UTILS_DIR" --quiet
    fi

    if python3 -m pip install -e ".[web]" --quiet; then
        echo -e "${GREEN}✓${NC}  Installation complete"
    else
        echo -e "${RED}❌${NC}  Installation failed"
        # Try without --quiet to show error
        echo -e "${BLUE}ℹ${NC}  Retrying with verbose output to diagnose..."
        python3 -m pip install -e ".[web]"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo ""
fi

# Show notification (macOS)
if command -v osascript &> /dev/null; then
    osascript -e 'display notification "Launching Council AI web interface..." with title "Council AI"' 2>/dev/null
fi

echo -e "${BLUE}🚀${NC}  Launching Council AI web interface..."
echo -e "${CYAN}💡${NC}  The web interface will open in your default browser"
echo -e "${CYAN}💡${NC}  Press Ctrl+C to stop the server"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Launch the web app with auto-open browser
python3 launch-council.py --open --port 8000 "$@"
EXIT_CODE=$?

# If success or already running, we don't need to alert the user
if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 2 ]; then
    exit 0
fi

# If the script exits with an error, show a message and wait
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}❌${NC}  Council AI web interface has stopped unexpectedly (Exit code: $EXIT_CODE)"
read -p "Press Enter to close this window..."
