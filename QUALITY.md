# Quality & Testing Policy

Council AI is expected to be reliable, minimal, and easy to validate locally. This
policy defines the required checks before release or review.

## Required Checks

Run these commands from the repo root:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Lint (static checks)
ruff check src tests

# Formatting (must be clean)
black --check src tests

# Test suite
pytest
```

## Optional Checks

```bash
# Full provider support
pip install -e ".[all]"

# Web app dependencies
pip install -e ".[web]"
```

## Expectations

- Lint and formatting must be clean.
- Tests must pass without local modifications.
- Any new features should include test coverage.
- Documentation must reflect current defaults and workflows.
