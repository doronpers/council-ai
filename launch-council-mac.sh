#!/bin/bash
# Council AI - Mac Launch Script
# Double-click to launch or run: ./launch-council-mac.sh

# Directory safety
cd "$(dirname "$0")" || exit

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║              Council AI Application Launcher              ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}ℹ️  Initializing environment...${NC}"

# Check for Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 detected${NC}"
    # Run the main Python launcher
    python3 launch-council.py --open
else
    echo -e "\033[0;31m❌ Error: Python 3 not found!${NC}"
    echo "Please install Python 3.9+ to run Council AI."
    # Pause to let user see the error if double-clicked
    read -p "Press any key to exit..."
    exit 1
fi
