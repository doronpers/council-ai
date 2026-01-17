#!/bin/bash
# One-click launcher for Council AI system
# Wrapper around the Python launcher

set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found.${NC}"
    exit 1
fi

# Check for venv, create if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed (basic check)
if ! python3 -c "import council_ai" &> /dev/null; then
    echo "Installing council-ai and dependencies..."
    if [ -d "../shared-ai-utils" ]; then
        echo "Installing local shared-ai-utils..."
        pip install -e "../shared-ai-utils"
    fi
    pip install -e ".[web]"
fi

# Hand over to the Python launcher
python3 launch-council.py "$@"
