#!/bin/bash
# scripts/audit_recent.sh
# Automate static analysis and security scans for Council AI

set -e

# Configuration
SRC_DIR="src"
TESTS_DIR="tests"
LINT_CMD="ruff check"
TYPE_CHECK_CMD="mypy"
SECURITY_SCAN_CMD="bandit"
TEST_CMD="pytest"

echo "=== Starting Recent Code Audit ==="

# 1. Linting (Ruff)
echo "Checking code style (ruff)..."
$LINT_CMD $SRC_DIR $TESTS_DIR

# 2. Type Checking (Mypy)
echo "Checking type safety (mypy)..."
$TYPE_CHECK_CMD $SRC_DIR --ignore-missing-imports

# 3. Security Scan (Bandit)
echo "Scanning for vulnerabilities (bandit)..."
$SECURITY_SCAN_CMD -r $SRC_DIR --severity-level medium --quiet

# 4. Tests (Pytest)
echo "Running test suite (pytest)..."
$TEST_CMD

echo "=== Audit Completed Successfully! ==="
