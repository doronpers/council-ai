# Gemini AI Configuration for Council AI

## System Instructions

Before starting any task on this repository, read `AGENT_KNOWLEDGE_BASE.md` in the repository root. This file contains:

- Prime directives (non-negotiable rules)
- Coding standards
- Project architecture
- Development workflows

## Quick Reference

### Style

- Formatter: `black` (line-length: 100)
- Linter: `ruff`
- Style: `snake_case` for functions, `PascalCase` for classes
- Type hints: Required for public functions

### Commands

```bash
black src/        # Format
ruff check src/   # Lint
pytest            # Test
```

### Security

- Never log API keys
- Never commit .env files
- Use environment variables for secrets
