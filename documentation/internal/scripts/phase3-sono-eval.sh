#!/bin/bash

# Phase 3 Execution: Reorganize sono-eval Documentation
# Run this AFTER feature/dual-lens-journey is merged to main
# This is the HIGHEST PRIORITY cleanup (11+ files to organize)
# Date: January 25, 2026

set -e  # Exit on error

REPO_DIR="/Volumes/Treehorn/Gits/sono-eval"
cd "$REPO_DIR"

echo "=========================================="
echo "Phase 3: sono-eval Documentation"
echo "=========================================="
echo "⚠️  HIGHEST PRIORITY - Most cleanup needed"
echo "=========================================="

# Verify on main branch
if [[ $(git rev-parse --abbrev-ref HEAD) != "main" ]]; then
    echo "❌ ERROR: Not on main branch"
    echo "   feature/dual-lens-journey must be merged to main first"
    exit 1
fi

# Verify clean state
if [[ $(git status --short) ]]; then
    echo "❌ ERROR: Repository has uncommitted changes"
    echo "Run 'git commit' first to save any work"
    exit 1
fi

# Create directories if needed
mkdir -p documentation/internal documentation/reviews Archive

echo "📁 Creating directories..."
echo "   ✓ documentation/internal/"
echo "   ✓ documentation/reviews/"
echo "   ✓ Archive/"

# Archive beta-phase files
echo ""
echo "📦 Archiving beta-phase files..."
if [[ -f "BETA_REQUIREMENTS.md" ]]; then
    git mv BETA_REQUIREMENTS.md Archive/
    echo "   ✓ Archived BETA_REQUIREMENTS.md"
fi

if [[ -f "BETA_WELCOME.md" ]]; then
    git mv BETA_WELCOME.md Archive/
    echo "   ✓ Archived BETA_WELCOME.md"
fi

# Move to reviews (code review / audit documents)
echo ""
echo "📋 Moving review & audit documents..."
if [[ -f "CODE_REVIEW_2026-01-16.md" ]]; then
    git mv CODE_REVIEW_2026-01-16.md documentation/reviews/
    echo "   ✓ Moved CODE_REVIEW_2026-01-16.md"
fi

if [[ -f "IMPROVEMENTS_REPORT_2026-01-19.md" ]]; then
    git mv IMPROVEMENTS_REPORT_2026-01-19.md documentation/reviews/
    echo "   ✓ Moved IMPROVEMENTS_REPORT_2026-01-19.md"
fi

# Move to internal (planning / operational)
echo ""
echo "🔧 Moving internal documentation..."
if [[ -f "DOCUMENTATION_REVISION_2026-01-21.md" ]]; then
    git mv DOCUMENTATION_REVISION_2026-01-21.md documentation/internal/
    echo "   ✓ Moved DOCUMENTATION_REVISION_2026-01-21.md"
fi

if [[ -f "DARK_HORSE_MITIGATION.md" ]]; then
    git mv DARK_HORSE_MITIGATION.md documentation/internal/
    echo "   ✓ Moved DARK_HORSE_MITIGATION.md"
fi

if [[ -f "PRODUCTION_HARDENING_SUMMARY.md" ]]; then
    git mv PRODUCTION_HARDENING_SUMMARY.md documentation/internal/
    echo "   ✓ Moved PRODUCTION_HARDENING_SUMMARY.md"
fi

if [[ -f "PUBLIC_RELEASE_CHECKLIST.md" ]]; then
    git mv PUBLIC_RELEASE_CHECKLIST.md documentation/internal/
    echo "   ✓ Moved PUBLIC_RELEASE_CHECKLIST.md"
fi

if [[ -f "SESSION_SUMMARY_2026-01-22.md" ]]; then
    git mv SESSION_SUMMARY_2026-01-22.md documentation/internal/
    echo "   ✓ Moved SESSION_SUMMARY_2026-01-22.md"
fi

if [[ -f "TEST_COVERAGE_IMPROVEMENTS.md" ]]; then
    git mv TEST_COVERAGE_IMPROVEMENTS.md documentation/internal/
    echo "   ✓ Moved TEST_COVERAGE_IMPROVEMENTS.md"
fi

if [[ -f "CODEX_ENV_SETUP.md" ]]; then
    git mv CODEX_ENV_SETUP.md documentation/internal/
    echo "   ✓ Moved CODEX_ENV_SETUP.md"
fi

if [[ -f "GEMINI.md" ]]; then
    git mv GEMINI.md documentation/internal/GEMINI_NOTES.md
    echo "   ✓ Moved GEMINI.md → GEMINI_NOTES.md"
fi

if [[ -f "AGENTS.md" ]]; then
    git mv AGENTS.md documentation/internal/AGENTS_NOTES.md
    echo "   ✓ Moved AGENTS.md → AGENTS_NOTES.md"
fi

# Handle README_LAUNCHERS if present
echo ""
echo "📖 Handling launcher documentation..."
if [[ -f "README_LAUNCHERS.md" ]]; then
    echo "   ℹ️  README_LAUNCHERS.md - review content and decide:"
    echo "      - Archive if merged into README.md"
    echo "      - Move to documentation/ if user-facing"
    echo "      - Leave if still needed"
    # For now, leaving it - user should decide
fi

# Update documentation index if exists
if [[ -f "documentation/README.md" ]]; then
    echo ""
    echo "📝 Note: Update documentation/README.md to reference new structure"
    echo "   See council-ai/documentation/README.md for pattern"
fi

# Show summary
echo ""
echo "=========================================="
echo "✅ Phase 3: sono-eval Complete"
echo "=========================================="
echo ""
echo "📊 Changes:"
git status --short | wc -l
git status --short
echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git diff --cached"
echo "   2. Update documentation/README.md if needed"
echo "   3. Commit: git commit -m 'docs: reorganize documentation structure'"
echo "   4. Push: git push origin main"
echo ""
echo "⚠️  This is the highest-priority cleanup (11+ files organized)"
echo ""
