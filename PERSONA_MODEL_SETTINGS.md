# Persona Model & Parameter Settings

This document verifies that each persona has unique model/parameter defaults where specified.

**Key Feature**: Council AI supports personas using **various LLM providers simultaneously**.
Each persona can be configured to use a different provider (Anthropic, OpenAI, Gemini, etc.),
enabling heterogeneous councils where different personas leverage different LLM providers in parallel.

## Personas with Unique Model Settings

| Persona | Provider | Model | Temperature | Notes |
|---------|---------|-------|-------------|-------|
| **rams** | anthropic (default) | `claude-3-opus-20240229` | `0.3` | Low temperature for precise design thinking |
| **kahneman** | openai (default) | `gpt-4-turbo-preview` | `0.5` | Balanced for cognitive analysis |
| **taleb** | openai (default) | `gpt-4-turbo-preview` | `0.9` | High temperature for creative risk thinking |
| **holman** | `openai` | `gpt-4o` | default (0.7) | Security-focused, uses latest GPT-4o |
| **treasure** | `anthropic` | `claude-3-5-sonnet-20240620` | default (0.7) | Communication expert, uses Claude Sonnet |

## Personas Using Council Defaults

These personas inherit the council's default provider/model/parameters:
- **compliance_auditor** - Uses council defaults
- **dempsey** - Uses council defaults
- **grove** - Uses council defaults
- **signal_analyst** - Uses council defaults

## Key Observations

1. **Unique Models**: Personas with specific expertise use different models:
   - Rams (design): Claude Opus (most capable)
   - Kahneman/Taleb (analysis): GPT-4 Turbo
   - Holman (security): GPT-4o (latest)
   - Treasure (communication): Claude Sonnet

2. **Unique Temperatures**:
   - Rams: 0.3 (precise, minimal)
   - Kahneman: 0.5 (balanced analysis)
   - Taleb: 0.9 (creative, exploratory)

3. **Heterogeneous Providers**: Personas can use various LLM providers simultaneously. For example, in a single consultation:
   - `rams` might use Claude Opus (Anthropic)
   - `kahneman` might use GPT-4 Turbo (OpenAI)
   - `grove` might use the council's default provider
   This enables optimal model selection per persona's expertise.

4. **Fallback Behavior**: If a persona's specified provider is unavailable, the system automatically falls back to the council's default provider while preserving the persona's temperature settings.

## Implementation

The `_get_member_provider()` method in `Council` class handles persona-specific LLM providers:
- Checks if persona has `provider` or `model` override
- Creates dedicated LLM provider instance for that persona
- Enables personas to use various LLM providers simultaneously
- Falls back to default provider if persona's provider unavailable
- Caches provider instances for performance

During consultation, each persona's response is generated using their preferred LLM provider,
allowing for true heterogeneous councils with multiple providers working in parallel.
- Caches provider instances for performance

Persona-specific `model_params` (like temperature) are applied via `_resolve_member_generation_params()`.
