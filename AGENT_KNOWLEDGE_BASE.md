# Agent Knowledge Base - Council AI

This document is the **Single Source of Truth** for all AI agents (Claude, Cursor, etc.) working on the council-ai repository. Refer to this before and during your tasks.

---

## 0. Prime Directives (NON-NEGOTIABLE)

1. **Security & Privacy**:
   - **NEVER** log API keys, secrets, or user credentials in code or output.
   - **NEVER** commit `.env` files or expose API keys in examples.
   - **ALWAYS** use environment variables or config files for sensitive data.

2. **Persona Integrity**:
   - **NEVER** modify the core philosophy or decision-making principles of built-in personas without explicit approval.
   - **ALWAYS** preserve the unique voice and perspective of each persona.

3. **Provider Neutrality**:
   - **NEVER** hardcode provider-specific logic in core council functionality.
   - **ALWAYS** use the provider abstraction layer for LLM interactions.

4. **Design Philosophy (The Advisory Council)**:
   - **Dieter Rams**: "Less but Better". Remove clutter. Unify styles.
   - **Daniel Kahneman**: Reduce cognitive load. "System 1 vs System 2".
   - **CONSTRAINT**: Use these lenses to audit and improve, but **DO NOT** brand features with persona names.

5. **Hippocratic Principle: "First, Do No Harm"**:

   > _"To do good or to do no harm"_ — Hippocratic tradition
   - **Avoid Deleterious Changes**: Do not introduce changes that harm functionality, security, or maintainability.
   - **Preserve Working Systems**: If code works correctly, changes must maintain or improve its behavior.
   - **Minimize Side Effects**: Consider downstream impacts before modifying shared code.
   - **Document Breaking Changes**: If unavoidable, document clearly with migration paths.
   - **Err on the Side of Caution**: When uncertain, ask for clarification rather than making assumptions.

   **Pre-commit checklist**:
   - [ ] Does this change preserve existing functionality?
   - [ ] Are there any unintended side effects?
   - [ ] Have I tested affected code paths?
   - [ ] Is backward compatibility maintained (or documented if not)?

---

## 1. Operational Guardrails

- **Configuration**: `~/.config/council-ai/config.yaml` for user config, `pyproject.toml` for project defaults.
- **API Keys**: Priority order: CLI flags > Environment variables > `.env` file > Config file.
- **Personas**: YAML files in `src/council_ai/personas/` are the source of truth for persona definitions.
- **Domains**: Registered in `src/council_ai/domains/__init__.py`.
- **Dependencies**: Do NOT upgrade major versions of core deps without testing all providers.

---

## 2. Coding Standards

### Python

- **Formatter**: `black` (line-length: 100)
- **Linter**: `ruff`
- **Style**: `snake_case` for functions/vars, `PascalCase` for classes
- **Validation**: Use **Pydantic** models for all data structures
- **Type Hints**: Required for all public functions and methods

### Commands

```bash
# Format code
black src/

# Lint code
ruff check src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=council_ai
```

### Error Handling

- Use `rich.console` for CLI output, not raw `print()`
- Return structured errors, don't raise unhandled exceptions in CLI commands
- Log errors with context using `logger.error(..., exc_info=True)`

---

## 3. Project Architecture

```text
council-ai/
├── src/council_ai/
│   ├── __init__.py        # Public API exports
│   ├── cli.py             # CLI implementation (Click)
│   ├── core/
│   │   ├── council.py     # Council class and ConsultationMode
│   │   ├── config.py      # ConfigManager and settings
│   │   ├── persona.py     # Persona and PersonaManager classes
│   │   └── diagnostics.py # API key diagnostics
│   ├── domains/           # Domain preset definitions
│   ├── personas/          # Persona YAML files
│   ├── providers/         # LLM provider implementations
│   ├── tools/             # Utilities (e.g., RepositoryReviewer)
│   └── webapp/            # Web app assets
├── tests/                 # pytest test suite
├── examples/              # Example scripts
└── pyproject.toml         # Package configuration
```

### Key Classes

- `Council`: Main class for creating and consulting advisory councils
- `Persona`: Represents an AI advisor with traits, focus areas, and decision principles
- `Domain`: Preset configurations for specific use cases
- `ConsultationMode`: Enum for consultation types (individual, synthesis, debate, vote, sequential)

---

## 4. Development Workflows

### Adding a New Persona

1. Create a YAML file in `src/council_ai/personas/`
2. Follow the schema: id, name, title, emoji, category, core_question, razor, traits, focus_areas
3. Personas are auto-loaded by `PersonaManager`
4. Add tests in `tests/`

### Adding a New Domain

1. Edit `src/council_ai/domains/__init__.py`
2. Add entry to `DOMAINS` dictionary
3. Define default_personas, optional_personas, example_queries

### Adding a New Provider

1. Create class in `src/council_ai/providers/__init__.py`
2. Inherit from `LLMProvider`
3. Implement `complete()` method (async)
4. Register in `_PROVIDERS` dictionary

---

## 5. Testing

- **Framework**: pytest
- **Location**: `tests/` directory
- **Requirement**: All new features must have corresponding tests
- **Run**: `pytest` or `pytest -v` for verbose output

### Test Naming

- `test_<feature>_<scenario>.py` for test files
- `test_<what_is_being_tested>()` for test functions

---

## 6. Quick Reference

| Task          | Command                           |
| :------------ | :-------------------------------- |
| Install (dev) | `pip install -e ".[dev]"`         |
| Format        | `black src/`                      |
| Lint          | `ruff check src/`                 |
| Test          | `pytest`                          |
| Run CLI       | `council --help`                  |
| Run web       | `council web --reload`            |
| Consult       | `council consult "Your question"` |

### Key Files

- Entry point: `src/council_ai/cli.py`
- Public API: `src/council_ai/__init__.py`
- Config: `pyproject.toml`
- Examples: `examples/`
- **API Reference: `documentation/API_REFERENCE.md`** (Complete Python API documentation)

---

## 7. Common Patterns

### Creating a Council

```python
from council_ai import Council

# For a domain
council = Council.for_domain("business", api_key="key")

# Custom members
council = Council(api_key="key")
council.add_member("DR")
council.add_member("NT")

# Consult
result = council.consult("Your question")
print(result.synthesis)
```

### CLI Command Pattern

```python
@main.command()
@click.argument("arg")
@click.option("--flag", "-f", help="Description")
@click.pass_context
def command_name(ctx, arg, flag):
    """Command description."""
    config_manager = ctx.obj["config_manager"]
    # Implementation
```

---

## Documentation Standards

### Documentation Structure

- **Root-level documentation**: User-facing documentation lives in the repository root
  - `README.md` - Main project documentation and getting started guide
  - `CONTRIBUTING.md` - Development workflow and contribution guidelines
  - `AGENT_KNOWLEDGE_BASE.md` - AI agent reference (this file)
  - `CHANGELOG.md` - Version history and changes
  - `SECURITY.md` - Security policy and best practices
  - `GEMINI.md` - Quick reference for Gemini AI agents
  - `.env.example` - API key configuration template

- **Extended documentation**: All other documentation lives in `documentation/` folder
  - `documentation/API_REFERENCE.md` - **Complete Python API documentation**
  - `documentation/REVIEWER_SETUP.md` - LLM Response Reviewer setup guide
  - `documentation/INTEGRATION_ASSESSMENT.md` - Integration assessments
  - `documentation/development/` - Development-specific documentation

### Documentation Guidelines

- Update `README.md` for user-facing changes
- Update `CONTRIBUTING.md` for development workflow changes
- Add detailed guides to `documentation/` folder
- Use docstrings for all public functions and classes
- Keep examples in `examples/` directory current
- **Never create new top-level documentation folders** - use `documentation/` for all non-root docs

---

## 8. Reasoning Logs

After completing significant tasks, document your reasoning in the feedback-loop repository.

**Location**: `feedback-loop/agent_reasoning_logs/logs/`

**When to Log**:

- Complex problem-solving tasks
- Architectural decisions
- Bug fixes with non-obvious solutions
- Refactoring work
- Any task with valuable lessons learned

**Template**: Use `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`

**File Naming**: `YYYY-MM-DD_council-ai_<brief-task>.md`

**Example**: `2026-01-16_council-ai_documentation-consolidation.md`

This creates institutional knowledge that helps future agents and developers understand past decisions, and feeds into the feedback-loop pattern library.
