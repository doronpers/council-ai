# Tests for Council AI

This directory contains tests for the Council AI package.

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Lint and format checks (see QUALITY.md for policy)
ruff check src tests
black --check src tests

# Run all tests
pytest

# Run with coverage
pytest --cov=council_ai

# Run specific test file
pytest tests/test_core.py -v
```

## Test Structure

- `test_core.py` - Core functionality tests (Council, Persona, etc.)
- `conftest.py` - Pytest configuration
