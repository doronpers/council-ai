# Repository Structure Guide

This guide explains the Council AI repository structure and helps you choose which repository to use.

## Which Repository Should I Use?

### council-ai (Main Framework)

**Location**: `https://github.com/doronpers/council-ai`

**Use this if:**

- You want the **main open-source framework**
- You're **contributing features** back to Council AI
- You need the **latest official features and updates**
- You're **embedding Council AI** in another application
- You want **clean architecture patterns** to follow

**What's included:**

- Core framework (prompt, agent, chain execution)
- Built-in personas (14+) and domains (15+)
- Web UI and CLI
- Python API
- Examples and integrations

**Best for:** Framework users, contributors, integrators

### council-ai-personal (Individual Agent Templates)

**Location**: Private repository (personal use)

**Use this if:**

- You want **quick templates** for personal AI agents
- You need **pre-configured personalities** for yourself
- You're building **individual workflows** (not shared frameworks)
- You want to **experiment without affecting** the main codebase

**What's included:**

- Personal agent templates
- Customized personas for individual use
- Quick-start configurations
- Personal experiments

**Best for:** Individual researchers, personal workflows

---

## Directory Structure

### council-ai Repository Layout

```
council-ai/
├── README.md                     # Project overview
├── GETTING_STARTED.md            # Setup guide (5 min)
├── REPOSITORY_STRUCTURE.md       # This file
├── CONTRIBUTING.md               # For contributors
├── SECURITY.md                   # Security guidelines
├── LICENSE                       # MIT
│
├── src/council_ai/
│   ├── __init__.py
│   ├── main.py                   # Core exports
│   │
│   ├── llm/                      # LLM Providers
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── gemini.py
│   │   ├── ollama.py
│   │   └── lm_studio.py
│   │
│   ├── context/                  # Context Management
│   │   ├── context.py
│   │   ├── interpreter.py
│   │   └── loader.py
│   │
│   ├── web_search/               # Web Search Integration
│   │   ├── tavily_search.py
│   │   ├── serper_search.py
│   │   └── google_search.py
│   │
│   ├── cli/                      # Command-Line Interface
│   │   ├── main.py
│   │   ├── commands/
│   │   │   ├── init.py           # Setup wizard
│   │   │   ├── run.py            # Run CLI
│   │   │   └── config.py
│   │   └── utils.py
│   │
│   ├── webapp/                   # Web UI (React + TypeScript)
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── components/
│   │   │   │   ├── Configuration/
│   │   │   │   ├── Consultation/
│   │   │   │   ├── Onboarding/
│   │   │   │   └── MemberSelection/
│   │   │   ├── context/
│   │   │   ├── api/
│   │   │   └── utils/
│   │   └── package.json
│   │
│   ├── agents/                   # Agent Implementation
│   │   ├── base.py
│   │   ├── prompt.py
│   │   └── executor.py
│   │
│   ├── personas/                 # Built-in Personas
│   │   ├── __init__.py
│   │   ├── researcher.py
│   │   ├── analyst.py
│   │   ├── writer.py
│   │   └── [12+ more personas]
│   │
│   ├── domains/                  # Built-in Domains
│   │   ├── __init__.py
│   │   ├── research.py
│   │   ├── engineering.py
│   │   ├── business.py
│   │   └── [12+ more domains]
│   │
│   ├── config/                   # Configuration System
│   │   ├── default_config.py
│   │   ├── config_loader.py
│   │   └── validation.py
│   │
│   └── utils/                    # Utilities
│       ├── logging.py
│       ├── validators.py
│       └── formatters.py
│
├── tests/                        # Test Suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── examples/                     # Example Usage
│   ├── basic_usage.py
│   ├── web_search_example.py
│   ├── custom_personas.py
│   └── multi_llm_example.py
│
├── documentation/                # User Documentation
│   ├── README.md                 # Docs index
│   ├── QUICK_REFERENCE.md        # Copy/paste examples
│   ├── CONFIGURATION.md          # Config guide
│   ├── PERSONAS_AND_DOMAINS.md   # Persona reference
│   ├── WEB_APP.md                # Web UI guide
│   ├── WEB_SEARCH_AND_REASONING.md
│   ├── CONTEXT_INJECTION_GUIDE.md
│   ├── REVIEWER_SETUP.md
│   ├── ERROR_HANDLING.md
│   ├── API_REFERENCE.md
│   ├── TROUBLESHOOTING.md
│   ├── COMMON_TASKS.md
│   ├── DOCS_MAINTENANCE.md
│   ├── decisions/                # Design decisions
│   └── internal/                 # Internal docs (not for users)
│
├── pyproject.toml                # Python package config
├── pytest.ini                    # Test configuration
├── package.json                  # Node dependencies
├── launch-council.py             # Launcher script
├── config.yaml.example           # Example config
├── .env.example                  # Example environment vars
│
├── Archive/                      # Deprecated files
│   └── [old setup guides]
│
└── docker/                       # Docker files (if any)
    └── [docker configs]
```

---

## Key Directories Explained

### `src/council_ai/` — Core Framework

Main application code. This is what gets installed when you `pip install -e .`

- **llm/**: LLM provider integrations (OpenAI, Anthropic, Gemini, Ollama, LM Studio)
- **cli/**: Command-line interface and setup wizard
- **webapp/**: React + TypeScript web UI
- **agents/**: Core agent framework (prompts, execution)
- **personas/**: Pre-built agent personalities (researcher, analyst, etc.)
- **domains/**: Pre-built domains (research, engineering, business, etc.)
- **config/**: Configuration system (env vars, config files, precedence)
- **context/**: Context loading and interpretation
- **web_search/**: Search provider integrations (Tavily, Serper, Google)

### `documentation/` — User Docs

All user-facing documentation:

- **README.md**: Table of contents for all docs
- **GETTING_STARTED.md**: 5-minute setup (in root, but referenced)
- **QUICK_REFERENCE.md**: Copy/paste code examples
- **WEB_APP.md**: Web UI walkthrough
- **CONFIGURATION.md**: All config options
- **TROUBLESHOOTING.md**: Common issues and solutions
- **internal/**: Developer notes (not for end users)
- **decisions/**: Architecture decisions

### `tests/` — Test Suite

- **unit/**: Test individual components
- **integration/**: Test component interactions

### `examples/` — Code Examples

Ready-to-run examples showing how to use Council AI programmatically.

---

## Common Navigation

### "I want to set up Council AI"

→ Go to [GETTING_STARTED.md](GETTING_STARTED.md)

### "I want to use the web interface"

→ Go to [WEB_APP.md](documentation/WEB_APP.md)

### "I want to configure LLM providers"

→ Go to [CONFIGURATION.md](documentation/CONFIGURATION.md)

### "I want to use web search and reasoning"

→ Go to [WEB_SEARCH_AND_REASONING.md](documentation/WEB_SEARCH_AND_REASONING.md)

### "I want to write custom code using Council AI"

→ Go to [API_REFERENCE.md](documentation/API_REFERENCE.md) and [examples/](examples/)

### "I'm hitting an error"

→ Go to [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md)

### "I want to contribute"

→ Go to [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Architecture Overview

Council AI follows this flow:

```
User Input
    ↓
[CLI or Web UI]
    ↓
[Configuration] (load provider, model, domain, personas)
    ↓
[Domain] (e.g., "research") provides context and guidance
    ↓
[Personas] (e.g., "Researcher", "Analyst") propose ideas
    ↓
[LLM Provider] (e.g., OpenAI, local Ollama) generates responses
    ↓
[Web Search] (optional) fetches real-time information
    ↓
[Output] to user with explanation of reasoning
```

---

## Design Philosophy

Council AI is built on these principles:

1. **Framework-first**: Extensible, not monolithic
2. **Provider-agnostic**: Supports any LLM (OpenAI, Anthropic, Gemini, local, custom)
3. **Configuration-driven**: Behavior via config, not code
4. **Web + CLI**: Both interfaces supported equally
5. **Explainability**: Every response includes reasoning

---

## File Organization Philosophy

- **Root-level**: Only project essentials (README, setup, CONTRIBUTING, LICENSE)
- **src/**: All framework code (installed via pip)
- **documentation/**: All user-facing docs
- **examples/**: Runnable code examples
- **tests/**: Test suite
- **Archive/**: Old/deprecated files (preserved in git)

---

## Getting Help

- **Setup issues?** → [GETTING_STARTED.md](GETTING_STARTED.md)
- **Using Council?** → [README.md](README.md)
- **Specific docs?** → [documentation/README.md](documentation/README.md)
- **Code examples?** → [examples/](examples/)
- **Contributing?** → [CONTRIBUTING.md](CONTRIBUTING.md)
