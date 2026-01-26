#!/bin/bash

# Phase 3 Execution: Reorganize Website-Sonotheia-v251120 Documentation
# Run this after committing active development changes
# Date: January 25, 2026

set -e  # Exit on error

REPO_DIR="/Volumes/Treehorn/Gits/Website-Sonotheia-v251120"
cd "$REPO_DIR"

echo "=========================================="
echo "Phase 3: Website-Sonotheia-v251120"
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
mkdir -p documentation/internal Archive

echo "📁 Creating directories..."
echo "   ✓ documentation/internal/"
echo "   ✓ Archive/"

# Archive QUICKSTART (overlaps with README)
echo ""
echo "📦 Archiving redundant setup guide..."
if [[ -f "QUICKSTART.md" ]]; then
    git mv QUICKSTART.md Archive/QUICKSTART.md.archived
    echo "   ✓ Archived QUICKSTART.md"
else
    echo "   ℹ️  QUICKSTART.md not found"
fi

# Move internal documentation
echo ""
echo "🔧 Moving internal documentation..."
if [[ -f "BRANCH_PROTECTION_QUICK_REFERENCE.md" ]]; then
    git mv BRANCH_PROTECTION_QUICK_REFERENCE.md documentation/internal/
    echo "   ✓ Moved BRANCH_PROTECTION_QUICK_REFERENCE.md"
fi

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

# Note about AGENTS.md
echo ""
echo "ℹ️  AGENTS.md remains at root (substantial, referenced in copilot-instructions)"

# Show summary
echo ""
echo "=========================================="
echo "✅ Phase 3: Website-Sonotheia Complete"
echo "=========================================="
git status --short
echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git diff --cached"
echo "   2. Commit: git commit -m 'docs: reorganize documentation structure'"
echo "   3. Push: git push origin main"
echo ""
