# Council AI Quick Reference

Quick reference for common Council AI tasks.

## Context Injection

```python
from council_ai import Council
from council_ai.utils.context import load_markdown_files, load_code_files

council = Council(api_key="key", provider="anthropic")
council.add_member("rams")

# Load files
context = load_markdown_files(["README.md"])
# OR
context = load_code_files(["src/main.py"])

result = council.consult("Review this", context=context)
```

## Web Search

```python
from council_ai import Council, CouncilConfig

# Enable web search
config = CouncilConfig(enable_web_search=True)
council = Council(api_key="key", provider="anthropic", config=config)
council.add_member("rams")

result = council.consult("What are latest API trends?")
```

## Reasoning Modes

```python
from council_ai import Council, CouncilConfig

# Enable reasoning mode
config = CouncilConfig(reasoning_mode="chain_of_thought")
council = Council(api_key="key", provider="anthropic", config=config)
council.add_member("rams")

result = council.consult("Should we use REST or GraphQL?")
```

## Persona Customization

```python
from council_ai import Council
from council_ai.core.persona import get_persona

council = Council(api_key="key", provider="anthropic")

# Custom persona with web search and reasoning
persona = get_persona("rams").clone(
    enable_web_search=True,
    reasoning_mode="analytical"
)
council.add_member(persona)

result = council.consult("Your question")
```

## Combined Features

```python
from council_ai import Council, CouncilConfig
from council_ai.utils.context import load_context_from_files

# Full-featured consultation
config = CouncilConfig(
    enable_web_search=True,
    reasoning_mode="chain_of_thought"
)

council = Council(api_key="key", provider="anthropic", config=config)
council.add_member("rams")
council.add_member("kahneman")

# Load context + web search + reasoning
context = load_context_from_files(["README.md", "src/main.py"])

result = council.consult(
    "Comprehensive review",
    context=context
)
```

## Environment Variables

```bash
# LLM Provider
export ANTHROPIC_API_KEY="your-key"

# Web Search (choose one)
export TAVILY_API_KEY="your-key"
# OR
export SERPER_API_KEY="your-key"
```

## Reasoning Modes

- `standard` - Default
- `chain_of_thought` - Step-by-step
- `tree_of_thought` - Multiple paths
- `reflective` - Think, reflect, refine
- `analytical` - Deep analysis
- `creative` - Divergent thinking

See full documentation:
- `documentation/CONTEXT_INJECTION_GUIDE.md`
- `documentation/WEB_SEARCH_AND_REASONING.md`
