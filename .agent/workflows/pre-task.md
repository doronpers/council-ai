---
description: Pre-task instructions for all agents working on council-ai
---

# Before Starting Any Task

Before making ANY changes to the council-ai repository, read the `AGENT_KNOWLEDGE_BASE.md` file in the repository root.

```bash
cat AGENT_KNOWLEDGE_BASE.md
```

This file contains critical instructions including:

1. Prime directives (non-negotiable rules)
2. Coding standards (black, ruff, type hints)
3. Project architecture overview
4. Development workflows for personas, domains, and providers
5. Testing requirements

## Verification

After completing your task:

```bash
black src/
ruff check src/
pytest
```
