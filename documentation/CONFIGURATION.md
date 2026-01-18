# Configuration Guide

This guide describes how Council AI loads configuration (API keys, default provider/domain, model settings), and how to set it via **CLI**, **environment**, or **config file**.

## Configuration sources and precedence

Council AI resolves credentials and defaults in this order:

1. **Explicit values you pass at runtime**
   - Python: `Council(api_key=..., provider=..., model=..., base_url=...)`
   - CLI: flags like `--api-key`, `--provider`, etc. (per-command)
2. **Provider-specific environment variables**
   - `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.
3. **OpenAI-compatible gateway key (OpenAI/Vercel)**
   - `AI_GATEWAY_API_KEY`
4. **Generic key (any provider)**
   - `COUNCIL_API_KEY`
5. **Config file**
   - `~/.config/council-ai/config.yaml` (default)

### `.env` files

If `python-dotenv` is installed (it is in core deps), Council AI will try to auto-load a `.env` file so that values behave like environment variables.

It checks (in order):

- `.env` in your **current working directory**
- `.env` in the **repository root** (when running from the repo)
- `~/.council-ai/.env`

## Config file location

- **Default**: `~/.config/council-ai/config.yaml`
- **Override**: set `COUNCIL_CONFIG_PATH` to point to a specific file

See `config.yaml.example` for a complete example config.

## Common CLI workflows

### First-time setup wizard

```bash
council init
```

### Inspect config

```bash
council config show
```

### Set default provider/domain

```bash
council config set api.provider openai
council config set default_domain coding
```

### Set default model/base URL (OpenAI-compatible endpoints)

```bash
council config set api.model gpt-4o
council config set api.base_url https://api.openai.com/v1
```

### Presets

```bash
# Save a reusable preset
council config preset-save my-review-team --domain coding --members rams,holman,kahneman --mode synthesis

# Use it
council consult --preset my-review-team "Review this code"
```

## Programmatic configuration

```python
from council_ai import Council, CouncilConfig

config = CouncilConfig(
    enable_web_search=True,
    web_search_provider="tavily",  # or "serper", "google", or "auto"
    reasoning_mode="analytical",
)

council = Council(provider="anthropic", config=config)
```
