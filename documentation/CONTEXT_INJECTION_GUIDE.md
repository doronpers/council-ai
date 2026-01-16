# Context Injection Guide for Council AI

This guide explains how to inject context, background details, code, images, and markdown files into Council AI consultations.

## Table of Contents

1. [Basic Context Injection](#basic-context-injection)
2. [Injecting Markdown Files](#injecting-markdown-files)
3. [Injecting Code Files](#injecting-code-files)
4. [Injecting Images](#injecting-images)
5. [Injecting Multiple Files](#injecting-multiple-files)
6. [Persona-Level Context](#persona-level-context)
7. [Helper Utilities](#helper-utilities)

---

## Basic Context Injection

The simplest way to inject context is using the `context` parameter in `council.consult()`:

```python
from council_ai import Council

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Simple string context
context = """
Project Background:
- Building a new API for user management
- Target launch: Q2 2024
- Team size: 5 engineers
"""

result = council.consult(
    "Should we use REST or GraphQL?",
    context=context
)
```

---

## Injecting Markdown Files

### Method 1: Read and Pass Directly

```python
from pathlib import Path
from council_ai import Council

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Read markdown file
readme_path = Path("README.md")
context = readme_path.read_text(encoding="utf-8")

result = council.consult(
    "Review our project documentation",
    context=f"Project Documentation:\n\n{context}"
)
```

### Method 2: Using Helper Utility

```python
from council_ai import Council
from council_ai.utils.context import load_markdown_files

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Load one or more markdown files
context = load_markdown_files([
    "README.md",
    "documentation/ARCHITECTURE.md",
    "CHANGELOG.md"
])

result = council.consult(
    "What are the key architectural decisions?",
    context=context
)
```

---

## Injecting Code Files

### Method 1: Read and Format Manually

```python
from pathlib import Path
from council_ai import Council

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Read code file
code_path = Path("src/main.py")
code_content = code_path.read_text(encoding="utf-8")

# Format with code block
context = f"""
Relevant Code File: {code_path}

```python
{code_content}
```
"""

result = council.consult(
    "Review this code for security issues",
    context=context
)
```

### Method 2: Using Helper Utility

```python
from council_ai import Council
from council_ai.utils.context import load_code_files

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Load code files with automatic language detection
context = load_code_files([
    "src/main.py",
    "src/utils.py",
    "tests/test_main.py"
])

result = council.consult(
    "Review code quality and suggest improvements",
    context=context
)
```

---

## Injecting Images

Images need to be base64-encoded and included in the context. Most modern LLM providers (Claude 3, GPT-4 Vision) support images.

### Method 1: Manual Base64 Encoding

```python
import base64
from pathlib import Path
from council_ai import Council

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Encode image to base64
image_path = Path("diagrams/architecture.png")
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# Note: For Claude, you'd typically pass images via the provider's image API
# This is a simplified example - actual implementation depends on provider
context = f"""
Architecture Diagram: {image_path.name}
[Image data would be passed separately via provider's image API]
"""

result = council.consult(
    "Review this architecture diagram",
    context=context
)
```

### Method 2: Using Helper Utility

```python
from council_ai import Council
from council_ai.utils.context import load_images

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Load and encode images
image_context = load_images([
    "diagrams/architecture.png",
    "screenshots/ui-mockup.jpg"
])

result = council.consult(
    "Review the UI design in these screenshots",
    context=image_context
)
```

**Note:** Image support varies by provider. Check your provider's documentation for image API details.

---

## Injecting Multiple Files

### Using Helper Utility

```python
from council_ai import Council
from council_ai.utils.context import load_context_from_files

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")

# Load multiple files of different types
context = load_context_from_files([
    "README.md",                    # Markdown
    "src/main.py",                  # Code
    "documentation/ARCHITECTURE.md", # Markdown
    "config/settings.yaml",         # Code (YAML)
])

result = council.consult(
    "Provide a comprehensive project review",
    context=context
)
```

---

## Persona-Level Context

You can inject context at the persona level using `prompt_prefix`, `prompt_suffix`, or `system_prompt_override` in persona YAML files.

### Option 1: Modify Persona YAML

```yaml
# custom_persona.yaml
id: custom_expert
name: Domain Expert
title: Specialized Advisor
emoji: "🎯"
category: custom

core_question: "Does this align with best practices?"
razor: "Expertise-driven decision making"

# Inject context via prompt prefix
prompt_prefix: |
  Background Context:
  - Project uses Python 3.11+
  - Follows PEP 8 style guide
  - Uses async/await patterns
  - Database: PostgreSQL 15

traits:
  - name: Domain Knowledge
    description: Deep expertise in the domain
    weight: 1.5

focus_areas:
  - Python development
  - Database design
  - API architecture
```

### Option 2: Programmatically Modify Persona

```python
from council_ai import Council
from council_ai.core.persona import get_persona

council = Council(api_key="your-key", provider="anthropic")

# Get a persona and clone it with custom context
base_persona = get_persona("rams")
custom_persona = base_persona.clone(
    new_id="rams_with_context",
    prompt_prefix="""
    Project Context:
    - Building a REST API
    - Using FastAPI framework
    - Target: High performance, low latency
    """
)

council.add_member(custom_persona)

result = council.consult("Should we use async endpoints?")
```

### Option 3: System Prompt Override

```python
from council_ai import Council
from council_ai.core.persona import get_persona

council = Council(api_key="your-key", provider="anthropic")

# Override entire system prompt with context
base_persona = get_persona("rams")
custom_persona = base_persona.clone(
    new_id="rams_custom",
    system_prompt_override=f"""
    You are Dieter Rams, Design Philosopher.

    Project Background:
    - Building a design system for a SaaS platform
    - Team of 10 designers
    - Target users: Enterprise customers

    Your Core Question: "Is this as simple as possible?"
    Your Razor: "Less, but better. Good design is as little design as possible."

    When responding, consider the project context above.
    """
)

council.add_member(custom_persona)
result = council.consult("Review our design system approach")
```

---

## Helper Utilities

Council AI provides helper utilities in `council_ai.utils.context` for common context loading tasks:

### Available Functions

```python
from council_ai.utils.context import (
    load_markdown_files,      # Load .md files
    load_code_files,          # Load code files with syntax highlighting
    load_text_files,          # Load any text files
    load_images,              # Load and encode images
    load_context_from_files,  # Auto-detect and load multiple files
    format_code_context,      # Format code with language tags
    format_file_context,      # Format file with metadata
)
```

### Example: Comprehensive Context Loading

```python
from council_ai import Council
from council_ai.utils.context import load_context_from_files

council = Council(api_key="your-key", provider="anthropic")
council.add_member("rams")
council.add_member("kahneman")

# Load comprehensive context
context = load_context_from_files([
    # Documentation
    "README.md",
    "CONTRIBUTING.md",
    "documentation/ARCHITECTURE.md",

    # Code
    "src/main.py",
    "src/core/council.py",

    # Configuration
    "pyproject.toml",
    "config/settings.yaml",

    # Images (if supported by provider)
    # "diagrams/flow.png",
])

result = council.consult(
    "Provide a comprehensive code review focusing on design simplicity and cognitive load",
    context=context
)
```

---

## Best Practices

1. **Keep Context Relevant**: Only include files/content relevant to the query
2. **Size Limits**: Be aware of token limits. Large files may need truncation
3. **Format Clearly**: Use clear section headers and code blocks
4. **Provider Support**: Check if your provider supports images before using them
5. **Incremental Context**: For large codebases, consider multiple focused consultations

### Example: Truncating Large Files

```python
from pathlib import Path
from council_ai.utils.context import load_code_files, truncate_content

# Load with automatic truncation
context = load_code_files(
    ["src/large_file.py"],
    max_length=5000,  # Truncate to 5000 chars
    truncate_message="... (truncated for brevity)"
)
```

---

## Advanced: Pre-Consult Hooks

You can use pre-consult hooks to automatically inject context:

```python
from council_ai import Council
from pathlib import Path

council = Council(api_key="your-key", provider="anthropic")

# Define a hook that automatically loads context
def auto_load_context(query: str, context: Optional[str]) -> Tuple[str, Optional[str]]:
    """Automatically load context from files if not provided."""
    if context:
        return query, context

    # Auto-load from common files
    context_files = []
    for path in ["README.md", "ARCHITECTURE.md"]:
        if Path(path).exists():
            context_files.append(path)

    if context_files:
        from council_ai.utils.context import load_context_from_files
        auto_context = load_context_from_files(context_files)
        return query, auto_context

    return query, context

# Register the hook
council.add_pre_consult_hook(auto_load_context)

# Now consultations automatically include context
result = council.consult("Review the project")
```

---

## Summary

- **Simple context**: Use `context` parameter in `consult()`
- **Markdown files**: Read with `Path.read_text()` or use `load_markdown_files()`
- **Code files**: Format with code blocks or use `load_code_files()`
- **Images**: Base64 encode or use provider's image API
- **Persona-level**: Use `prompt_prefix`, `prompt_suffix`, or `system_prompt_override`
- **Multiple files**: Use `load_context_from_files()` helper
- **Auto-injection**: Use pre-consult hooks

For more examples, see `examples/` directory in the repository.
