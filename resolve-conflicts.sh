#!/bin/bash
# Conflict Resolution Helper Script
# Usage: ./resolve-conflicts.sh <source-branch>

set -e

SOURCE_BRANCH="${1:-}"
CURRENT_BRANCH=$(git branch --show-current)

if [ -z "$SOURCE_BRANCH" ]; then
    echo "Usage: $0 <source-branch>"
    echo ""
    echo "Available remote branches with recent activity:"
    git branch -r --sort=-committerdate | head -10
    exit 1
fi

echo "🔍 Preparing to merge $SOURCE_BRANCH into $CURRENT_BRANCH..."
echo ""

# Fetch latest
git fetch origin

# Check if branch exists
if ! git rev-parse --verify "origin/$SOURCE_BRANCH" >/dev/null 2>&1; then
    echo "❌ Branch origin/$SOURCE_BRANCH not found"
    exit 1
fi

# Show what files will be affected
echo "📋 Files changed in $SOURCE_BRANCH:"
git diff --name-only "$CURRENT_BRANCH" "origin/$SOURCE_BRANCH" | grep -E "\.(tsx|ts)$" || echo "No TypeScript files changed"

echo ""
echo "🔄 Attempting merge (dry-run to see conflicts)..."
echo ""

# Attempt merge
if git merge --no-commit --no-ff "origin/$SOURCE_BRANCH" 2>&1; then
    echo "✅ No conflicts detected! Merge is clean."
    git merge --abort 2>/dev/null || true
else
    echo ""
    echo "⚠️  Conflicts detected! Files with conflicts:"
    git diff --name-only --diff-filter=U
    echo ""
    echo "📝 Next steps:"
    echo "   1. Review each conflicted file"
    echo "   2. Resolve conflicts manually"
    echo "   3. Run: git add <resolved-files>"
    echo "   4. Run: git commit"
fi
