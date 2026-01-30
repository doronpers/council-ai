#!/bin/bash
# Personal Council AI Launcher - Mac
# Launches Council AI with personal settings and memory active

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Change to project root
cd "$SCRIPT_DIR/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set personal configuration environment
export COUNCIL_CONFIG_DIR="$HOME/.config/council-ai"

# Auto-detect council-ai-personal if it exists as sibling
if [ -d "../council-ai-personal" ]; then
    export COUNCIL_AI_PERSONAL_PATH="$(cd "../council-ai-personal" && pwd)"
    echo "📦 Found council-ai-personal at: $COUNCIL_AI_PERSONAL_PATH"
fi

# Set MemU path if it exists (common locations)
# User can override by setting MEMU_PATH environment variable
if [ -z "$MEMU_PATH" ]; then
    # Try common locations
    if [ -d "$HOME/memu" ]; then
        export MEMU_PATH="$HOME/memu"
    elif [ -d "$HOME/.memu" ]; then
        export MEMU_PATH="$HOME/.memu"
    elif [ -d "/opt/memu" ]; then
        export MEMU_PATH="/opt/memu"
    fi

    if [ -n "$MEMU_PATH" ]; then
        echo "🧠 Found MemU at: $MEMU_PATH"
    fi
fi

# Show configuration
echo "🏛️  Council AI Personal Mode"
echo "Config directory: $COUNCIL_CONFIG_DIR"
if [ -n "$COUNCIL_AI_PERSONAL_PATH" ]; then
    echo "Personal repo: $COUNCIL_AI_PERSONAL_PATH"
fi
if [ -n "$MEMU_PATH" ]; then
    echo "MemU path: $MEMU_PATH"
fi
echo ""

# Launch with personal settings
python3 bi./bin/launch-council.py --open --install
