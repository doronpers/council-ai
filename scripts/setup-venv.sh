#!/bin/bash
# Council AI Virtual Environment Setup Script (Unix/macOS)
# Creates a virtual environment and configures it with your API keys

set -e

echo "🏛️  Council AI Virtual Environment Setup"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi
python3 --version
echo "✓ Python found"
echo ""

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies (if not skipped)
if [ "$1" != "--skip-install" ]; then
    echo "Installing Council AI dependencies..."

    # Check for shared-ai-utils sibling (development mode)
    SHARED_UTILS="$(dirname "$SCRIPT_DIR")/shared-ai-utils"
    if [ -d "$SHARED_UTILS" ]; then
        echo "Found local shared-ai-utils, installing in development mode..."
        pip install -e "$SHARED_UTILS" --quiet
    fi

    # Install council-ai
    pip install -e ".[web]" --quiet
    echo "✓ Dependencies installed"
    echo ""
fi

# Setup .env file
if [ "$1" != "--skip-env" ]; then
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            echo "Creating .env file from template..."
            cp .env.example .env
            echo "✓ .env file created from .env.example"
            echo "⚠️  Please edit .env and add your API keys"
        else
            echo "Creating .env file..."
            cat > .env << 'EOF'
# Council AI Environment Variables
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
ELEVENLABS_API_KEY=
TAVILY_API_KEY=
PYTHONUTF8=1
EOF
            echo "✓ .env file created"
            echo "⚠️  Please edit .env and add your API keys"
        fi
    else
        echo "✓ .env file already exists"
    fi
    echo ""
fi

# Create activation script with .env loading
echo "Creating enhanced activation script..."
cat > venv/bin/activate-env << 'ACTIVATE_EOF'
#!/bin/bash
# Enhanced venv activation with .env loading
source "$(dirname "$BASH_SOURCE")/activate"

# Load .env file if it exists
ENV_FILE="$(dirname "$(dirname "$BASH_SOURCE")")/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | grep -v 'your-.*-here' | xargs)
    echo "✓ Loaded environment variables from .env"
fi
ACTIVATE_EOF
chmod +x venv/bin/activate-env

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment with your secrets:"
echo "  source venv/bin/activate-env"
echo ""
echo "Or use the launcher:"
echo "  ./launch-council.py --open"
echo ""
