# Tests for Council AI

This directory contains tests for the Council AI package.

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

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
