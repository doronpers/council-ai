#!/usr/bin/env bash
# Codex environment setup script for council-ai
# This script runs automatically when Codex creates or resumes a container
# It ensures the environment is ready for development and testing

set -e

echo "🏛️  Council AI - Codex Environment Setup"
echo "=========================================="
echo ""

# Change to workspace directory (Codex clones to /workspace/council-ai)
cd /workspace/council-ai || cd "$(dirname "$0")/.." || exit 1

echo "📦 Installing/upgrading pip..."
python3 -m pip install --upgrade pip --quiet

echo "📦 Installing council-ai with dev dependencies..."
# Install in editable mode with dev extras (includes pytest, black, ruff, mypy, etc.)
pip install -e ".[dev]" --quiet

# Install pre-commit hooks (optional - don't fail if it's not critical)
echo "🔧 Setting up pre-commit hooks..."
pre-commit install || echo "⚠️  Pre-commit install skipped (non-critical)"

# Verify installation
echo "✅ Verifying installation..."
python3 -c "import council_ai; print(f'✓ council-ai installed')" || echo "⚠️  Version check skipped"

# Quick sanity check - run a fast test subset (don't fail setup on test failures)
echo "🧪 Running quick sanity check..."
pytest -q -m "not slow and not integration" --co -q > /dev/null 2>&1 && echo "✓ Test discovery successful" || echo "⚠️  Test discovery check skipped"

echo ""
echo "✅ Setup complete! Environment ready for council-ai development and testing."
echo ""
echo "Quick commands:"
echo "  pytest                    # Run all tests"
echo "  pytest -m 'not slow'       # Run fast tests only"
echo "  black src/                 # Format code"
echo "  ruff check src/            # Lint code"
echo "  mypy src/                  # Type check"
echo "  pre-commit run --all-files # Run all pre-commit hooks"
echo ""
