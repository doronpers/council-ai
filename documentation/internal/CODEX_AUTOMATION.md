# Codex Autonomous Automation Guide

This guide explains how to use Codex for autonomous validation, testing, and quality assurance tasks in the `council-ai` project.

## Overview

Codex can automatically handle:

- ✅ Code formatting and linting
- ✅ Type checking
- ✅ Test execution (fast, full, coverage)
- ✅ Package validation
- ✅ Security scanning
- ✅ Pre-commit hook validation
- ✅ CLI validation
- ✅ Import validation

## Quick Start

### Manual Execution

Run the automation script directly:

```bash
# Full validation suite
bash scripts/codex-automation.sh

# Quick check (lint, types, fast tests)
CODEX_TASK=quick bash scripts/codex-automation.sh

# Specific task
CODEX_TASK=lint bash scripts/codex-automation.sh
CODEX_TASK=test-fast bash scripts/codex-automation.sh
CODEX_TASK=types bash scripts/codex-automation.sh
```

### Available Tasks

| Task        | Description                               | Command                                                 |
| ----------- | ----------------------------------------- | ------------------------------------------------------- |
| `all`       | Complete validation suite                 | `CODEX_TASK=all bash scripts/codex-automation.sh`       |
| `quick`     | Fast validation (lint, types, fast tests) | `CODEX_TASK=quick bash scripts/codex-automation.sh`     |
| `ci`        | Full CI pipeline                          | `CODEX_TASK=ci bash scripts/codex-automation.sh`        |
| `format`    | Code formatting check                     | `CODEX_TASK=format bash scripts/codex-automation.sh`    |
| `lint`      | Linting with ruff                         | `CODEX_TASK=lint bash scripts/codex-automation.sh`      |
| `types`     | Type checking with mypy                   | `CODEX_TASK=types bash scripts/codex-automation.sh`     |
| `test-fast` | Fast tests only                           | `CODEX_TASK=test-fast bash scripts/codex-automation.sh` |
| `test-all`  | All tests                                 | `CODEX_TASK=test-all bash scripts/codex-automation.sh`  |
| `coverage`  | Test coverage report                      | `CODEX_TASK=coverage bash scripts/codex-automation.sh`  |
| `precommit` | Pre-commit hooks                          | `CODEX_TASK=precommit bash scripts/codex-automation.sh` |
| `validate`  | Package validation                        | `CODEX_TASK=validate bash scripts/codex-automation.sh`  |
| `security`  | Security scan                             | `CODEX_TASK=security bash scripts/codex-automation.sh`  |
| `cli`       | CLI validation                            | `CODEX_TASK=cli bash scripts/codex-automation.sh`       |

## Autonomous Execution

### Task Configuration

Tasks are defined in `.codex/tasks.json`. Each task can be configured to run:

- **On file change**: Automatically when files are modified
- **On commit**: Before commits are finalized
- **On push**: When pushing to remote
- **Manual**: On-demand execution

### Setting Up Autonomous Tasks

1. **Configure Codex Environment**:
   - Use the setup script: `scripts/codex-setup.sh`
   - Ensure environment variables are set (see `CODEX_ENV_SETUP.md`)

2. **Enable Auto-run**:
   - Codex can be configured to automatically run tasks based on triggers
   - Default behavior: runs `quick-check` on file changes

3. **Custom Triggers**:
   - Modify `.codex/tasks.json` to customize trigger behavior
   - Add new tasks as needed

## Workflow Integration

### GitHub Actions

The automation script is integrated with GitHub Actions via `.github/workflows/codex-validation.yml`:

- **Runs on**: Push to main/develop, Pull Requests
- **Executes**: Full CI pipeline
- **Reports**: Test coverage to Codecov

### Pre-commit Hooks

The automation respects and uses pre-commit hooks:

- Formatting (black)
- Linting (ruff, flake8)
- Type checking (mypy)
- Import sorting (isort)
- Security scanning (detect-secrets)

## Best Practices

### For Development

1. **Before Committing**:

   ```bash
   CODEX_TASK=quick bash scripts/codex-automation.sh
   ```

2. **Before Pushing**:

   ```bash
   CODEX_TASK=ci bash scripts/codex-automation.sh
   ```

3. **Before Release**:
   ```bash
   CODEX_TASK=all bash scripts/codex-automation.sh
   CODEX_TASK=coverage bash scripts/codex-automation.sh
   ```

### For Codex Agents

When working in Codex, agents should:

1. **Run quick checks frequently**:
   - After making code changes
   - Before committing
   - When unsure about code quality

2. **Run full validation**:
   - Before completing a task
   - When preparing for review
   - After significant refactoring

3. **Monitor results**:
   - Check task summaries
   - Fix failures immediately
   - Review coverage reports

## Task Details

### Format Check

- **Tool**: Black
- **Action**: Checks code formatting
- **Auto-fix**: Run `black src/ tests/` to fix

### Linting

- **Tool**: Ruff
- **Action**: Static analysis and linting
- **Auto-fix**: Run `ruff check --fix src/ tests/`

### Type Checking

- **Tool**: Mypy
- **Action**: Static type analysis
- **Configuration**: See `pyproject.toml` for mypy settings

### Testing

- **Framework**: Pytest
- **Markers**: `slow`, `integration`, `performance`
- **Fast tests**: Excludes slow and integration tests
- **Coverage**: Minimum 50% (configurable in `pyproject.toml`)

### Package Validation

- **Script**: `scripts/validate_package.py`
- **Checks**: Imports, personas, domains, council creation, CLI

### Security

- **Tool**: detect-secrets
- **Action**: Scans for exposed secrets
- **Baseline**: `.secrets.baseline`

## Troubleshooting

### Task Failures

If a task fails:

1. **Check the error message**: Each task provides specific error details
2. **Run the task individually**: Isolate the failing component
3. **Check dependencies**: Ensure all dev dependencies are installed
4. **Review logs**: Check Codex logs for detailed error information

### Common Issues

**Formatting failures**:

```bash
black src/ tests/  # Auto-fix formatting
```

**Linting failures**:

```bash
ruff check --fix src/ tests/  # Auto-fix linting issues
```

**Type errors**:

- Review mypy output
- Add type hints where needed
- Check `pyproject.toml` for mypy configuration

**Test failures**:

- Run tests individually: `pytest tests/path/to/test.py`
- Check test markers: `pytest -m "not slow"`
- Review test output for specific failures

## Integration with CI/CD

The automation script is designed to work seamlessly with:

- **GitHub Actions**: `.github/workflows/codex-validation.yml`
- **Pre-commit hooks**: `.pre-commit-config.yaml`
- **Local development**: Direct script execution

## Extending Automation

### Adding New Tasks

1. Add task function to `scripts/codex-automation.sh`:

   ```bash
   task_new_task() {
       log_info "Running new task..."
       # Your task logic here
   }
   ```

2. Add case to main() function:

   ```bash
   new-task)
       run_task "New Task" task_new_task
       ;;
   ```

3. Update `.codex/tasks.json`:
   ```json
   "new-task": {
     "name": "New Task",
     "description": "Description of new task",
     "command": "bash scripts/codex-automation.sh",
     "env": { "CODEX_TASK": "new-task" }
   }
   ```

### Custom Triggers

Modify `.codex/tasks.json` to add custom trigger conditions or integrate with external systems.

## Summary

Codex automation provides:

- ✅ **Efficiency**: Automated validation saves time
- ✅ **Accuracy**: Consistent quality checks
- ✅ **Reliability**: Catches issues before they reach production
- ✅ **Integration**: Works with existing CI/CD pipelines
- ✅ **Flexibility**: Customizable tasks and triggers

Use these automation tools to maintain high code quality and catch issues early in the development process.
