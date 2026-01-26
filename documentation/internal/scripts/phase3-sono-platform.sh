#!/bin/bash

# Phase 3 Execution: Reorganize sono-platform Documentation
# Run this after committing active development changes to sono-platform
# Date: January 25, 2026

set -e  # Exit on error

REPO_DIR="/Volumes/Treehorn/Gits/sono-platform"
cd "$REPO_DIR"

echo "=========================================="
echo "Phase 3: sono-platform Documentation"
echo "=========================================="

# Verify clean state
if [[ $(git status --short) ]]; then
    echo "❌ ERROR: Repository has uncommitted changes"
    echo "Run 'git commit' first to save active development work"
    exit 1
fi

if [[ $(git rev-parse --abbrev-ref HEAD) != "main" ]]; then
    echo "❌ ERROR: Not on main branch"
    exit 1
fi

# Create directories if needed
mkdir -p documentation/internal

echo "📁 Creating directories..."
echo "   ✓ documentation/internal/"

# Archive QUICKSTART (overlaps with README)
echo ""
echo "📦 Archiving redundant setup guide..."
if [[ -f "QUICKSTART.md" ]]; then
    mkdir -p Archive
    git mv QUICKSTART.md Archive/QUICKSTART.md.archived
    echo "   ✓ Archived QUICKSTART.md"
else
    echo "   ℹ️  QUICKSTART.md not found"
fi

# Move internal documentation
echo ""
echo "🔧 Moving internal documentation..."
if [[ -f "CODEX_ENV_SETUP.md" ]]; then
    git mv CODEX_ENV_SETUP.md documentation/internal/
    echo "   ✓ Moved CODEX_ENV_SETUP.md"
fi

if [[ -f "GEMINI.md" ]]; then
    git mv GEMINI.md documentation/internal/GEMINI_NOTES.md
    echo "   ✓ Moved GEMINI.md → GEMINI_NOTES.md"
fi

# Move reporting documentation
echo ""
echo "📊 Moving reporting documentation..."
if [[ -f "TEST_COVERAGE_ASSESSMENT.md" ]]; then
    git mv TEST_COVERAGE_ASSESSMENT.md documentation/
    echo "   ✓ Moved TEST_COVERAGE_ASSESSMENT.md"
fi

# Show summary
echo ""
echo "=========================================="
echo "✅ Phase 3: sono-platform Complete"
echo "=========================================="
git status --short
echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git diff --cached"
echo "   2. Commit: git commit -m 'docs: reorganize documentation structure'"
echo "   3. Push: git push origin main"
echo ""
