# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Council AI is an AI-powered advisory council system with customizable personas for decision-making, reviews, and strategic thinking. It provides a framework for consulting multiple AI "personas" - each with distinct expertise, perspectives, and decision-making approaches.

**Key Components:**

- 14 built-in personas across advisory, red team, and specialist councils
- 15 domain presets for different use cases (coding, business, startup, etc.)
- Multi-provider LLM support (Anthropic, OpenAI, Google Gemini, custom endpoints)
- Standalone React/TypeScript web app with Dieter Rams-inspired design
- CLI tool for consultations, history management, and configuration

## Development Commands

### Python Package Management

```bash
# Install in development mode
pip install -e ".[dev]"

# Install with specific provider support
pip install -e ".[anthropic]"    # For Claude
pip install -e ".[openai]"       # For GPT-4
pip install -e ".[gemini]"       # For Gemini
pip install -e ".[web]"          # For web app dependencies
pip install -e ".[all]"          # All providers
```

### Code Quality & Testing

```bash
# Format code (required before commits)
black src/

# Lint code
ruff check src/

# Type checking
mypy src/ --ignore-missing-imports

# Run all tests
pytest

# Run tests with coverage
pytest --cov=council_ai

# Run specific test file
pytest tests/test_core.py -v

# Run automated audit (ruff, mypy, bandit, pytest)
./scripts/audit_recent.sh
```

### Web Application

```bash
# Build frontend (React/TypeScript)
npm install
npm run build

# Run web server (backend API)
council web --reload

# Development mode - frontend with hot reload (in separate terminal)
npm run dev
# Runs Vite dev server on http://localhost:5173 with proxy to backend

# Launch complete web app (1-click launcher)
./bin/launcher.sh
```

### CLI Usage

```bash
# Basic consultation
council consult "Your question here"

# With specific domain
council consult --domain startup "Should we pivot?"

# Interactive mode
council interactive

# History management
council history sessions
council history resume SESSION_ID
council history list
council history search "keyword"

# Persona and domain management
council persona list
council persona show rams
council domain list
council domain show coding

# Configuration
council config show
council config set api.provider openai
```

## Architecture Overview

### Core Architecture

The codebase follows a modular, provider-abstraction pattern:

1. **Council Orchestration** (`core/council.py`)
   - `Council` class: Main orchestrator for persona consultations
   - Supports multiple consultation modes: individual, sequential, synthesis, debate, vote
   - Each persona can use different LLM providers simultaneously (heterogeneous councils)
   - Automatic fallback to available LLM providers
   - Web search integration (Tavily, Serper, Google) and reasoning modes

2. **Persona System** (`core/persona.py`)
   - `Persona` class: Represents an AI advisor with traits, focus areas, decision principles
   - `PersonaManager`: Auto-loads persona YAML files from `src/council_ai/personas/`
   - Personas have weights (0.0-2.0) affecting synthesis influence
   - Core attributes: id, name, emoji, category, core_question, razor, traits, focus_areas

3. **Domain Presets** (`domains/__init__.py`)
   - Domain configurations map use cases to recommended persona sets
   - Examples: coding (DR, DK, PH, NT), business (AG, NT, MD, DK)
   - Registered in `DOMAINS` dictionary with default_personas and example_queries

4. **Provider Abstraction** (`providers/__init__.py`)
   - `LLMProvider` base class with abstract `complete()` method
   - `LLMManager` handles provider initialization and credential management
   - Implementations: AnthropicProvider, OpenAIProvider, GeminiProvider, HTTPProvider
   - Provider-neutral core allows personas to use any supported LLM

5. **Session & History** (`core/session.py`, `core/history.py`)
   - `ConsultationResult`: Contains query, responses, synthesis, metadata, audio URLs
   - `MemberResponse`: Individual persona response with content, timestamp, error
   - `HistoryManager`: SQLite-based storage in `~/.council-ai/consultations.db`
   - Session tracking, tagging, search, export (markdown/JSON)

6. **Configuration** (`core/config.py`)
   - `ConfigManager`: Manages `~/.config/council-ai/config.yaml`
   - Priority: CLI flags > Environment vars > `.env` file > config.yaml
   - Stores API keys, provider settings, defaults, presets

### Web Application Architecture

**Frontend** (React 18 + TypeScript):

- Located in `src/council_ai/webapp/src/`
- Modular component architecture (25+ components in `components/`)
- Context API for state management (`context/`)
- Vite build system with code splitting and vendor chunking
- Build output: `src/council_ai/webapp/static/`
- Dieter Rams-inspired minimalist UI design

**Backend** (FastAPI):

- Located in `src/council_ai/webapp/app.py`
- REST API for consultations, history, personas, domains
- WebSocket support for streaming responses
- TTS integration (ElevenLabs primary, OpenAI fallback)
- Serves static frontend assets

**Development Workflow:**

1. Backend runs on http://localhost:8000
2. Frontend dev server runs on http://localhost:5173 (proxies /api to backend)
3. Production: Frontend builds to static assets served by backend

### Directory Structure

```
council-ai/
├── src/council_ai/
│   ├── cli.py              # Click-based CLI implementation
│   ├── core/
│   │   ├── council.py      # Council orchestration & consultation modes
│   │   ├── persona.py      # Persona definitions & management
│   │   ├── config.py       # Configuration management
│   │   ├── session.py      # Session data structures
│   │   ├── history.py      # History storage (SQLite)
│   │   ├── analysis.py     # Consensus analysis
│   │   ├── reasoning.py    # Reasoning mode prompts
│   │   └── diagnostics.py  # API key validation
│   ├── domains/            # Domain preset definitions (YAML-based)
│   ├── personas/           # Persona YAML files (14 built-in)
│   ├── providers/          # LLM provider implementations
│   │   ├── __init__.py     # Provider abstraction & registry
│   │   ├── resilience.py   # Retry logic & error handling
│   │   └── tts.py          # Text-to-speech integration
│   ├── tools/              # Utilities (RepositoryReviewer, etc.)
│   └── webapp/
│       ├── app.py          # FastAPI backend
│       ├── index.html      # Main HTML entry
│       ├── src/            # React/TypeScript source
│       └── static/         # Built frontend assets
├── tests/                  # pytest test suite
├── examples/               # Example usage scripts
├── bin/                    # Launcher scripts and utilities
├── scripts/                # Maintenance scripts (audit_recent.sh, deploy.sh)
├── documentation/          # Extended docs (API_REFERENCE.md, guides)
├── pyproject.toml          # Package config, dependencies, tool settings
├── vite.config.js          # Frontend build configuration
└── package.json            # Frontend dependencies & npm scripts
```

## Development Guidelines

### Code Standards

- **Formatter:** `black` with line-length: 100 (enforced in pyproject.toml)
- **Linter:** `ruff` (checks: E, F, I, N, W; ignores E501)
- **Type Hints:** Required for all public functions and methods
- **Validation:** Use Pydantic models for data structures
- **Naming:** `snake_case` for functions/variables, `PascalCase` for classes
- **Testing:** All new features require pytest tests in `tests/`

### Security & Privacy (NON-NEGOTIABLE)

- NEVER log API keys, secrets, or credentials in code or output
- NEVER commit `.env` files
- ALWAYS use environment variables or config files for sensitive data
- Use `rich.console` for CLI output, not raw `print()`

### Provider Neutrality

- NEVER hardcode provider-specific logic in core council functionality
- ALWAYS use the provider abstraction layer (`LLMProvider` interface)
- Personas can specify preferred providers, but council must support any provider

### Persona Integrity

- NEVER modify core philosophy or decision principles of built-in personas without approval
- ALWAYS preserve unique voice and perspective of each persona
- Persona YAML files in `src/council_ai/personas/` are source of truth

### Adding New Features

**Add a Persona:**

1. Create YAML in `src/council_ai/personas/`
2. Schema: id, name, title, emoji, category, core_question, razor, traits, focus_areas
3. Auto-loaded by `PersonaManager`
4. Add tests in `tests/`

**Add a Domain:**

1. Edit `src/council_ai/domains/__init__.py`
2. Add entry to `DOMAINS` dictionary with default_personas, optional_personas, example_queries
3. Test with `council domain show your_domain`

**Add an LLM Provider:**

1. Create class in `src/council_ai/providers/__init__.py` inheriting from `LLMProvider`
2. Implement async `complete()` method
3. Register in `_PROVIDERS` dictionary
4. Add optional dependency to `pyproject.toml` if needed

### Testing

- Test files: `tests/test_<feature>.py`
- Test functions: `test_<what_is_being_tested>()`
- Run specific test: `pytest tests/test_core.py::test_council_creation -v`
- Use `conftest.py` for shared fixtures

## Configuration & API Keys

**Priority Order:**

1. CLI flags (`--api-key`, `--provider`)
2. Environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`)
3. `.env` file (auto-loaded, git-ignored)
4. Config file (`~/.config/council-ai/config.yaml`)

**Config File Location:**

- Default: `~/.config/council-ai/config.yaml`
- Override: `COUNCIL_CONFIG_PATH` environment variable

**Web Search Providers:**

- Tavily: `TAVILY_API_KEY`
- Serper: `SERPER_API_KEY`
- Google: `GOOGLE_API_KEY` + `GOOGLE_CSE_ID`

**TTS Providers:**

- ElevenLabs: `ELEVENLABS_API_KEY` (primary)
- OpenAI TTS: `OPENAI_API_KEY` (fallback)

## Common Patterns

### Creating and Using a Council

```python
from council_ai import Council, ConsultationMode

# For a specific domain
council = Council.for_domain("business", api_key="key")

# Custom configuration
council = Council(api_key="key", provider="anthropic")
council.add_member("DR")
council.add_member("NT")
council.set_member_weight("AG", 1.5)

# Consult with context
result = council.consult(
    "Should we migrate to Kubernetes?",
    context="Company: 15 people, $2M ARR",
    mode=ConsultationMode.SYNTHESIS
)

# Access results
print(result.synthesis)
for response in result.responses:
    print(f"{response.persona.emoji} {response.persona.name}: {response.content}")
```

### Structured Output & Analysis

```python
from council_ai import CouncilConfig

config = CouncilConfig(
    use_structured_output=True,  # Enable structured synthesis
    enable_analysis=True,         # Enable consensus analysis
    enable_web_search=True,       # Enable web search
    reasoning_mode="analytical"   # Use extended reasoning
)
council = Council(api_key="key", config=config)
result = council.consult("Analyze our scaling strategy")

# Access structured outputs
print(result.structured_synthesis)
print(result.analysis)
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
    # Implementation with rich.console for output
```

## Important Files

- **Entry Points:** `src/council_ai/cli.py` (CLI), `src/council_ai/webapp/app.py` (Web API)
- **Public API:** `src/council_ai/__init__.py` (exports for `from council_ai import ...`)
- **Configuration:** `pyproject.toml` (package), `~/.config/council-ai/config.yaml` (user)
- **Personas:** `src/council_ai/personas/*.yaml` (14 built-in persona definitions)
- **Documentation:** `README.md` (main), `documentation/API_REFERENCE.md` (complete API docs)
- **Agent Reference:** `AGENT_KNOWLEDGE_BASE.md` (detailed development guide)

## Frontend Development

### Tech Stack

- React 18 with TypeScript
- Vite for build tooling and dev server
- Context API for state management
- No external UI libraries (custom minimalist components)

### Key Frontend Directories

- `src/council_ai/webapp/src/components/` - React components
- `src/council_ai/webapp/src/context/` - State management contexts
- `src/council_ai/webapp/src/utils/` - Utility functions
- `src/council_ai/webapp/src/styles/` - CSS modules

### Build Process

1. `npm install` - Install frontend dependencies
2. `npm run build` - TypeScript compile + Vite build
3. Output: `src/council_ai/webapp/static/` (served by FastAPI in production)

### Development Cycle

- Backend: `council web --reload` (port 8000)
- Frontend: `npm run dev` (port 5173, proxies /api to backend)
- Make frontend changes → hot reload in browser
- Build for production: `npm run build`

## Troubleshooting

### Windows Users

If tools aren't in PATH, use Python module syntax:

```bash
python -m black src/
python -m ruff check src/
python -m pytest
```

### API Key Issues

Run diagnostics: `council config show` or check `AGENT_KNOWLEDGE_BASE.md` section 0 (Prime Directives)

### Web App Not Loading

1. Ensure frontend is built: `npm run build`
2. Check backend is running: `council web --reload`
3. For dev mode: Run both backend and `npm run dev` in separate terminals

## Recent UX Improvements (January 2026)

The web application has undergone a comprehensive design audit and UX polish guided by Dieter Rams' 10 Principles of Good Design. See `DESIGN_AUDIT_REPORT.md` and `IMPLEMENTATION_SUMMARY.md` for full details.

**Key Improvements:**

- ✅ **Accessibility**: Full keyboard navigation, ARIA labels, screen reader support
- ✅ **User Feedback**: Empty states, character counters, loading indicators
- ✅ **Visual Polish**: Professional favicon, consistent styling, no inline styles
- ✅ **Type Safety**: Removed all `any` types, added proper TypeScript interfaces
- ✅ **Performance**: Optimized memoization, cleaner component architecture
- ✅ **Code Quality**: 171/171 tests passing, clean build, production-ready

## Additional Resources

- **Design Audit Report:** `DESIGN_AUDIT_REPORT.md` - Comprehensive UX audit through Rams' 10 Principles
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md` - Detailed changes and improvements
- **Complete API Documentation:** `documentation/API_REFERENCE.md`
- **Agent Development Guide:** `AGENT_KNOWLEDGE_BASE.md`
- **Contributing Guidelines:** `CONTRIBUTING.md`
- **Reviewer Setup:** `documentation/REVIEWER_SETUP.md`
- **Examples:** `examples/` directory (simple_example.py, review_repository.py, etc.)
