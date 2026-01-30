#!/usr/bin/env bash
# Bootstrap script to ensure codex-automation.sh exists
# Run this in Codex if the automation script is missing

set -e

cd /workspace/council-ai || exit 1

# Pull latest changes
echo "🔄 Pulling latest changes from main..."
git pull origin main 2>/dev/null || echo "⚠️  Git pull failed, continuing..."

# Check if automation script exists
if [ ! -f "scripts/codex-automation.sh" ]; then
    echo "❌ Automation script still not found after pull"
    echo "📝 Creating automation script from template..."

    # The script should exist on main, but if not, we'll need to create it
    # For now, just report the issue
    echo "⚠️  Please ensure you're on the main branch:"
    echo "   git checkout main"
    echo "   git pull origin main"
    exit 1
else
    echo "✅ Automation script found!"
    chmod +x scripts/codex-automation.sh
    echo "✅ Ready to use: CODEX_TASK=quick bash scripts/codex-automation.sh"
fi
