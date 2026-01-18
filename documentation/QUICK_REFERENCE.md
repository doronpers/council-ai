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
from council_ai import Council, get_persona

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

## Web UI Configuration

### Local LLM Setup

```bash
# 1. Select provider (local/ollama)
# 2. Go to Advanced Settings
# 3. Set Base URL:
# Ollama: http://localhost:11434/v1
# LM Studio: http://localhost:1234/v1
# Custom: http://your-server:8000/v1
# 4. API Key (usually empty for local)
```

### Custom Endpoints

```bash
# For any OpenAI-compatible endpoint:
# 1. Choose provider that matches your model type
# 2. In Advanced Settings, set Base URL to your endpoint
# 3. Add API key if required
# 4. Settings are saved to browser automatically
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

## Related Guides

- `documentation/CONTEXT_INJECTION_GUIDE.md`
- `documentation/WEB_SEARCH_AND_REASONING.md`
