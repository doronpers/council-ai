# 🏛️ Council AI

**Intelligent Advisory Council System** — Get advice from a council of AI-powered personas with diverse perspectives and expertise.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/doronpers/council-ai)

## 🚀 Getting Started (5 Minutes)

### Option 1: Local LLM (Free, No API Key)

Use a local LLM with [LM Studio](https://lmstudio.ai/) for cost-free, private consulting:

```bash
# 1. Download & start LM Studio, load any model

# 2. Install and run Council AI
pip install -e ".[dev]"
council init          # Detects LM Studio automatically
council run "Should we redesign our API?"
```

### Option 2: Cloud LLM (OpenAI, Anthropic, Gemini)

```bash
# Install with your provider
pip install -e ".[anthropic]"    # or [openai], [gemini]

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run
council init
council run "Your question here"
```

### Need More Guidance?

→ **[GETTING_STARTED.md](GETTING_STARTED.md)** — Detailed 5-10 minute setup guide for all platforms

→ **[REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)** — Understand council-ai vs council-ai-personal

---

## ✨ Features

- 🎭 **14 Built-in Personas** — Advisors, red team, specialists with diverse perspectives
- 🌐 **15 Domain Presets** — Business, research, engineering, creative, career, legal, medical, and more
- 🔧 **Fully Customizable** — Create personas, adjust traits, modify behavior
- 🤖 **Multi-Provider** — OpenAI, Anthropic, Google Gemini, Ollama, LM Studio, or custom endpoints
- 💬 **Multiple Modes** — Individual, synthesis, debate, vote, sequential, or pattern-based
- 🔍 **Web Search** — Live data via Tavily, Serper, or Google Custom Search
- 🧠 **Extended Thinking** — Reasoning mode for complex analysis
- 📝 **Session Management** — Track and resume consultations
- 🧭 **Web UI** — Modern React/TypeScript interface with Dieter Rams design
- 🎯 **Onboarding Wizard** — Guided 6-step setup for first-time users
- 🔊 **Text-to-Speech** — Voice responses via ElevenLabs or OpenAI
- 📖 **[Full API](documentation/API_REFERENCE.md)** — Use Council AI in your code

---

## 📚 Documentation

| Need                   | Link                                                                     |
| ---------------------- | ------------------------------------------------------------------------ |
| **Setup Guide**        | [GETTING_STARTED.md](GETTING_STARTED.md)                                 |
| **Troubleshooting**    | [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md)                   |
| **Common Tasks**       | [COMMON_TASKS.md](documentation/COMMON_TASKS.md)                         |
| **Using Web UI**       | [WEB_APP.md](documentation/WEB_APP.md)                                   |
| **Configuration**      | [CONFIGURATION.md](documentation/CONFIGURATION.md)                       |
| **Web Search**         | [WEB_SEARCH_AND_REASONING.md](documentation/WEB_SEARCH_AND_REASONING.md) |
| **Personas & Domains** | [PERSONAS_AND_DOMAINS.md](documentation/PERSONAS_AND_DOMAINS.md)         |
| **Python API**         | [API_REFERENCE.md](documentation/API_REFERENCE.md)                       |
| **Contributing**       | [CONTRIBUTING.md](CONTRIBUTING.md)                                       |
| **All Docs**           | [documentation/README.md](documentation/README.md)                       |

---

## 📦 Installation & Configuration

Full step-by-step setup → **[GETTING_STARTED.md](GETTING_STARTED.md)**

### Quick Version

```bash
# Clone repository
git clone https://github.com/doronpers/council-ai.git
cd council-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux: source venv/bin/activate; Windows: .\venv\Scripts\activate.bat

# Install package
pip install -e ".[dev]"

# Run setup wizard (guides you through API key configuration)
council init

# Launch web UI
python launch-council.py --web
# OR launch CLI
council run
```

**Supported API Providers**: OpenAI, Anthropic, Google Gemini, Ollama, LM Studio, or custom endpoints.

See **[REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)** to understand which repository to use (council-ai vs council-ai-personal).

---

## 🎯 Usage Examples

**Web UI:**

```bash
python launch-council.py --web
# Open http://localhost:8000 → Complete onboarding wizard
```

**CLI:**

```bash
# Interactive session
council run

# One-shot consultation
council run --query "Should we pivot our business model?"

# With specific domain & personas
council run --domain startup --model gpt-4
```

**Python API:**

```python
from council_ai import Council

council = Council.for_domain("business", api_key="your-key")
result = council.consult("Should we expand to Europe?")
print(result.synthesis)
```

**For comprehensive examples**, see [COMMON_TASKS.md](documentation/COMMON_TASKS.md) and [examples/](examples/).

---

## 🏗️ Persona Architecture (v2.0+)

Council AI uses **archetypes** — reusable personality templates — combined with **specialization** for flexible persona management.

### Archetypes (Public)

Generic trait-based templates in `src/council_ai/personas/archetypes/`:

- `quality_advocate` — Design philosophy & best practices
- `security_specialist` — Adversarial thinking & risk
- `strategic_leader` — Long-term strategy
- `risk_analyst` — Probabilistic reasoning
- `cognitive_scientist` — Human behavior & UX

### Specialized Personas (Personal)

In `council-ai-personal` (private repo, sibling directory):

- Real-name personas inheriting from archetypes
- Private configurations
- Personal customizations

**14 Built-in Personas** across 3 councils:

- Advisory Council: Dieter Rams, Daniel Kahneman, Martin Dempsey, Julian Treasure
- Red Team: Pablo Holman, Nassim Taleb, Andy Grove, and others
- Specialists: Audio, compliance, fraud, and domain experts

**15 Domain Presets**: Business, startup, coding, creative, career, audio, medical, legal, and more.

Create custom personas or modify weights to fit your needs.

**Reference**: [PERSONAS_AND_DOMAINS.md](documentation/PERSONAS_AND_DOMAINS.md)

---

## Advanced Features

| Feature                 | Documentation                                                            |
| ----------------------- | ------------------------------------------------------------------------ |
| **Web Search**          | [WEB_SEARCH_AND_REASONING.md](documentation/WEB_SEARCH_AND_REASONING.md) |
| **Context Injection**   | [CONTEXT_INJECTION_GUIDE.md](documentation/CONTEXT_INJECTION_GUIDE.md)   |
| **LLM Response Review** | [REVIEWER_SETUP.md](documentation/REVIEWER_SETUP.md)                     |
| **Configuration**       | [CONFIGURATION.md](documentation/CONFIGURATION.md)                       |
| **Error Handling**      | [ERROR_HANDLING.md](documentation/ERROR_HANDLING.md)                     |
| **Python API**          | [API_REFERENCE.md](documentation/API_REFERENCE.md)                       |

---

## Support

- 📖 **Documentation**: [documentation/README.md](documentation/README.md)
- 🐛 **Issues**: [github.com/doronpers/council-ai/issues](https://github.com/doronpers/council-ai/issues)
- 💬 **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- ❓ **Troubleshooting**: [TROUBLESHOOTING.md](documentation/TROUBLESHOOTING.md)

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=council_ai

# Run specific test
pytest tests/unit/test_core.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for code quality and testing standards.

---

## License

MIT License — see [LICENSE](LICENSE) file.

---

Built with ❤️ for better decisions.
