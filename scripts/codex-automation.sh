#!/usr/bin/env bash
# Codex Autonomous Automation Script for council-ai
# This script runs comprehensive validation, testing, and quality checks
# Designed to be executed automatically by Codex agents

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Task selection (can be overridden via environment variable)
TASK="${CODEX_TASK:-all}"

# Results tracking
FAILED_TASKS=()
PASSED_TASKS=()

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
    PASSED_TASKS+=("$1")
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    FAILED_TASKS+=("$1")
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

run_task() {
    local task_name="$1"
    shift
    log_info "Running: $task_name"
    if "$@"; then
        log_success "$task_name"
        return 0
    else
        log_error "$task_name"
        return 1
    fi
}

# Task: Code Formatting (Black)
task_format() {
    log_info "Formatting code with black..."
    black --check --diff src/ tests/ || {
        log_warning "Code formatting issues found. Run 'black src/ tests/' to fix."
        return 1
    }
}

# Task: Linting (Ruff)
task_lint() {
    log_info "Linting code with ruff..."
    ruff check src/ tests/ || return 1
}

# Task: Import Sorting (isort)
task_imports() {
    log_info "Checking import sorting with isort..."
    isort --check-only --profile=black src/ tests/ || {
        log_warning "Import sorting issues found. Run 'isort src/ tests/' to fix."
        return 1
    }
}

# Task: Type Checking (mypy)
task_types() {
    log_info "Type checking with mypy..."
    mypy src/council_ai --ignore-missing-imports --no-strict-optional --disable-error-code=no-any-return || return 1
}

# Task: Fast Tests (excludes slow and integration)
task_test_fast() {
    log_info "Running fast tests (excluding slow and integration)..."
    pytest -m "not slow and not integration" --tb=short -v || return 1
}

# Task: All Tests
task_test_all() {
    log_info "Running all tests..."
    pytest --tb=short -v || return 1
}

# Task: Test Coverage
task_coverage() {
    log_info "Running tests with coverage..."
    pytest --cov=src/council_ai --cov-report=term-missing --cov-report=html -m "not slow and not integration" || return 1
    log_info "Coverage report generated in htmlcov/"
}

# Task: Pre-commit Hooks
task_precommit() {
    log_info "Running pre-commit hooks..."
    pre-commit run --all-files || return 1
}

# Task: Package Validation
task_validate_package() {
    log_info "Validating package installation..."
    python3 scripts/validate_package.py || return 1
}

# Task: Security Scan (detect-secrets)
task_security() {
    log_info "Scanning for secrets..."
    detect-secrets scan --baseline .secrets.baseline . || return 1
}

# Task: CLI Validation
task_cli() {
    log_info "Validating CLI commands..."
    council --version > /dev/null || return 1
    council --help > /dev/null || return 1
}

# Task: Import Validation
task_imports_check() {
    log_info "Validating all imports..."
    python3 -c "
import sys
modules = [
    'council_ai',
    'council_ai.core.council',
    'council_ai.core.persona',
    'council_ai.core.session',
    'council_ai.core.strategies.individual',
    'council_ai.core.strategies.synthesis',
    'council_ai.cli',
]
for module in modules:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError as e:
        print(f'✗ {module}: {e}')
        sys.exit(1)
" || return 1
}

# Task: Documentation Check
task_docs() {
    log_info "Checking documentation..."
    # Check that README exists and is readable
    test -f README.md || return 1
    # Check that key documentation files exist
    test -f CODEX_ENV_SETUP.md || log_warning "CODEX_ENV_SETUP.md not found"
    return 0
}

# Main task runner
main() {
    echo ""
    echo "=========================================="
    echo "  Council AI - Codex Automation"
    echo "=========================================="
    echo ""
    echo "Task: $TASK"
    echo "Project: $PROJECT_ROOT"
    echo ""

    case "$TASK" in
        format)
            run_task "Code Formatting" task_format
            ;;
        lint)
            run_task "Linting" task_lint
            ;;
        imports)
            run_task "Import Sorting" task_imports
            ;;
        types)
            run_task "Type Checking" task_types
            ;;
        test-fast)
            run_task "Fast Tests" task_test_fast
            ;;
        test-all)
            run_task "All Tests" task_test_all
            ;;
        coverage)
            run_task "Test Coverage" task_coverage
            ;;
        precommit)
            run_task "Pre-commit Hooks" task_precommit
            ;;
        validate)
            run_task "Package Validation" task_validate_package
            ;;
        security)
            run_task "Security Scan" task_security
            ;;
        cli)
            run_task "CLI Validation" task_cli
            ;;
        quick)
            # Quick validation: format, lint, types, fast tests
            run_task "Code Formatting" task_format || true
            run_task "Linting" task_lint
            run_task "Type Checking" task_types
            run_task "Fast Tests" task_test_fast
            ;;
        ci)
            # Full CI pipeline
            run_task "Code Formatting" task_format || true
            run_task "Linting" task_lint
            run_task "Import Sorting" task_imports || true
            run_task "Type Checking" task_types
            run_task "Fast Tests" task_test_fast
            run_task "Package Validation" task_validate_package
            run_task "CLI Validation" task_cli
            ;;
        all|*)
            # Complete validation suite
            run_task "Code Formatting" task_format || true
            run_task "Linting" task_lint
            run_task "Import Sorting" task_imports || true
            run_task "Type Checking" task_types
            run_task "Import Validation" task_imports_check
            run_task "Fast Tests" task_test_fast
            run_task "Package Validation" task_validate_package
            run_task "CLI Validation" task_cli
            run_task "Documentation Check" task_docs
            ;;
    esac

    # Summary
    echo ""
    echo "=========================================="
    echo "  Summary"
    echo "=========================================="
    echo ""
    echo -e "${GREEN}Passed: ${#PASSED_TASKS[@]}${NC}"
    for task in "${PASSED_TASKS[@]}"; do
        echo -e "  ${GREEN}✓${NC} $task"
    done
    echo ""
    if [ ${#FAILED_TASKS[@]} -gt 0 ]; then
        echo -e "${RED}Failed: ${#FAILED_TASKS[@]}${NC}"
        for task in "${FAILED_TASKS[@]}"; do
            echo -e "  ${RED}✗${NC} $task"
        done
        echo ""
        exit 1
    else
        echo -e "${GREEN}All tasks passed!${NC}"
        echo ""
        exit 0
    fi
}

main "$@"
