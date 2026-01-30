#!/bin/bash
# Resolve PR Conflicts Script
# Usage: ./resolve-pr-conflicts.sh <PR_NUMBER> or <BRANCH_NAME>

set -e

PR_OR_BRANCH="${1:-}"

if [ -z "$PR_OR_BRANCH" ]; then
    echo "Usage: $0 <PR_NUMBER> or <BRANCH_NAME>"
    echo ""
    echo "Example: $0 3"
    echo "Example: $0 claude/strengthen-types-mkjzqv9pv3m0q3ny-HqsR1"
    exit 1
fi

# Check if it's a number (PR) or branch name
if [[ "$PR_OR_BRANCH" =~ ^[0-9]+$ ]]; then
    echo "🔍 Fetching PR #$PR_OR_BRANCH..."
    git fetch origin "refs/pull/$PR_OR_BRANCH/head:pr-$PR_OR_BRANCH" 2>/dev/null || {
        echo "❌ Could not fetch PR #$PR_OR_BRANCH"
        exit 1
    }
    BRANCH="pr-$PR_OR_BRANCH"
    echo "✅ Fetched PR #$PR_OR_BRANCH as local branch: $BRANCH"
else
    echo "🔍 Using branch: $PR_OR_BRANCH"
    BRANCH="$PR_OR_BRANCH"
    # Try to fetch it
    git fetch origin "$BRANCH:$BRANCH" 2>/dev/null || echo "⚠️  Branch might be local or in a fork"
fi

# Make sure we're on main and up to date
echo ""
echo "📦 Updating main branch..."
git checkout main
git pull origin main

# Show what will be merged
echo ""
echo "📋 Files changed in $BRANCH:"
git diff --name-only main...$BRANCH 2>/dev/null | head -20 || {
    echo "⚠️  Could not compare. Branch might not exist locally."
    echo "💡 Try: git fetch origin $BRANCH:$BRANCH"
    exit 1
}

# Attempt merge
echo ""
echo "🔄 Attempting merge..."
if git merge --no-commit --no-ff "$BRANCH" 2>&1; then
    echo ""
    echo "✅ No conflicts! Merge is clean."
    echo "💡 Run 'git commit' to complete the merge, or 'git merge --abort' to cancel"
else
    CONFLICTS=$(git diff --name-only --diff-filter=U)
    CONFLICT_COUNT=$(echo "$CONFLICTS" | wc -l | tr -d ' ')
    echo ""
    echo "⚠️  Conflicts detected in $CONFLICT_COUNT file(s):"
    echo "$CONFLICTS" | nl
    echo ""
    echo "📝 Next steps:"
    echo "   1. Resolve conflicts in each file (remove <<<<<<<, =======, >>>>>>> markers)"
    echo "   2. Test your changes"
    echo "   3. Run: git add <resolved-files>"
    echo "   4. Run: git commit"
    echo ""
    echo "💡 To abort: git merge --abort"
fi
