# 🏛️ Council AI

**Intelligent Advisory Council System** - Get advice from a council of AI-powered personas with diverse perspectives and expertise.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/doronpers/council-ai)

---

## ☁️ Open in Codespaces

Get up and running immediately with a fully configured development environment in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/doronpers/council-ai)

## 🚀 Quickstart (No API Key Required)

Want to explore Council AI before setting up an API key? Run:

```bash
# Run the interactive launcher (handles setup automatically)
./launcher.sh
```

Or manually:

This interactive demo shows you:

- All 9 built-in personas and their characteristics
- 14 domain presets and what they're for
- How to set up and use councils
- Example usage patterns

### First-Time Setup

For first-time users, we provide a guided setup wizard:

```bash
# Run the interactive setup wizard
council init
```

This will guide you through:

- Choosing your LLM provider
- Configuring your API key
- Setting your default domain
- Understanding next steps

To actually consult the council (requires API key):

```bash
# Install with a provider (choose one)
pip install -e ".[anthropic]"   # For Anthropic Claude
pip install -e ".[openai]"      # For OpenAI GPT
pip install -e ".[gemini]"      # For Google Gemini

# Set your API key (choose one)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# Try a simple consultation
python examples/simple_example.py
```

---

## Overview

Council AI provides a framework for consulting multiple AI "personas" - each with distinct expertise, perspectives, and decision-making approaches. Whether you're making business decisions, reviewing code, planning strategy, or working on creative projects, the council provides comprehensive, multi-perspective advice.

**Key Features:**

- 🎭 **9 Built-in Personas** - Advisory Council (build it right) + Red Team (break & survive) + Experts
- 🌐 **14 Domain Presets** - Coding, business, startup, creative, career, and more
- 🔧 **Fully Customizable** - Create your own personas, adjust weights, modify traits
- 🤖 **Multi-Provider Support** - Anthropic, OpenAI, Google Gemini, or custom endpoints
- 💬 **Multiple Modes** - Individual, synthesis, debate, or vote
- 🧭 **Standalone Web App** - A focused, Dieter Rams-inspired web UI
- 🔊 **Text-to-Speech** - Voice responses via ElevenLabs and OpenAI TTS
- 📦 **Portable Package** - pip-installable, use in any project
- 📖 **[Full API Documentation](documentation/API_REFERENCE.md)** - Complete Python API reference

---

## Installation

**From PyPI (when published):**

```bash
# Basic installation
pip install council-ai

# With Anthropic Claude support
pip install "council-ai[anthropic]"

# With OpenAI GPT support
pip install "council-ai[openai]"

# With Google Gemini support
pip install "council-ai[gemini]"

# Full installation (all providers)
pip install "council-ai[all]"
```

**Development Installation (from this repo):**

```bash
# Clone the repository
git clone https://github.com/doronpers/council-ai.git
cd council-ai

# Install with specific provider
pip install -e ".[anthropic]"
pip install -e ".[openai]"
pip install -e ".[gemini]"

# Or with all providers
pip install -e ".[all]"

# Or for development (includes testing tools)
pip install -e ".[dev]"
```

> [!NOTE]
> **Windows Users:** If you encounter "command not found" errors, ensure your Python `Scripts` directory is in your PATH. Alternatively, you can run commands using the `python -m` syntax (e.g., `python -m pytest`, `python -m black src/`).

### Set Your API Key

**Option 1: Using a `.env` file (Recommended)**

Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
```

The `.env` file is automatically loaded when you import `council_ai`. It's already in `.gitignore`, so it won't be committed.

### Option 2: Environment Variables

```bash
# Choose your provider
export ANTHROPIC_API_KEY="your-key"    # For Claude
export OPENAI_API_KEY="your-key"       # For GPT-4
export GEMINI_API_KEY="your-key"       # For Gemini
```

### Option 3: Config File

```bash
council config set api.api_key your-key
```

### Option 4: Setup Wizard (Recommended for First-Time Users)

```bash
council init
```

**Priority Order:**

1. CLI flags (`--api-key`)
2. Environment variables
3. `.env` file (auto-loaded)
4. Config file (`~/.config/council-ai/config.yaml`)

### CLI Usage

```bash
# First time? Run the setup wizard
council init

# Explore features without an API key
council quickstart

# Simple consultation
council consult "Should I take this job offer?"

# With a specific domain
council consult --domain startup "Should we pivot?"

# With specific personas
council consult --members grove --members taleb "What's our biggest risk?"

# With a specific mode
council consult --mode sequential "Walk through this step-by-step"

# Interactive mode
council interactive

# Web app (for user testing)
council web --reload

# Repository review (code/design/security)
council review . --focus all --output review.md
```

### Python API

```python
from council_ai import Council

# Create a council for a domain
council = Council.for_domain("business", api_key="your-key")

# Consult the council
result = council.consult("Should we enter the European market?")

# Print the synthesis
print(result.synthesis)

# Print individual responses
for response in result.responses:
    print(f"{response.persona.emoji} {response.persona.name}:")
    print(response.content)
    print()
```

---

## Built-in Personas

### Advisory Council (Build It Right)

| Persona | Focus | Core Question |
| ------- | ----- | ------------- |
| 🎨 **Dieter Rams** | Simplification, Design | "Is this as simple as possible?" |
| 🎖️ **Martin Dempsey** | Mission Clarity, Autonomy | "Can this operate without asking permission?" |
| 🧠 **Daniel Kahneman** | Cognitive Load, UX | "Does this work with human cognition?" |
| 🔊 **Julian Treasure** | Communication, Listening | "Are we listening with integrity?" |

### Red Team Council (Break & Survive)

| Persona | Focus | Core Question |
| ------- | ----- | ------------- |
| 🔓 **Pablos Holman** | Security, Exploits | "How would I break this?" |
| 🦢 **Nassim Taleb** | Risk, Antifragility | "What's the hidden risk?" |
| 🎯 **Andy Grove** | Strategy, Competition | "What 10X force could make us irrelevant?" |

### Specialist Council (Deep Domain Expertise)

| Persona | Focus | Core Question |
| ------- | ----- | ------------- |
| 🛡️ **Signal Analyst** | Deepfake Defense, Audio | "Is this signal authentic or synthetic?" |
| ⚖️ **Compliance Auditor** | Regulations, Fintech | "Does this comply with relevant regulations?" |

---

## Domain Presets

```bash
# List all domains
council domain list
```

| Domain | Description | Default Personas |
| ------ | ----------- | ---------------- |
| `coding` | Software development | Rams, Kahneman, Holman, Taleb |
| `business` | Business strategy | Grove, Taleb, Dempsey, Kahneman |
| `startup` | Early-stage decisions | Grove, Taleb, Kahneman, Rams |
| `product` | Product management | Kahneman, Rams, Treasure, Grove |
| `leadership` | Team & org leadership | Dempsey, Kahneman, Grove |
| `creative` | Creative projects | Treasure, Rams, Kahneman |
| `writing` | Written content | Treasure, Kahneman, Rams |
| `career` | Career decisions | Grove, Kahneman, Dempsey, Taleb |
| `decisions` | Major life decisions | Kahneman, Taleb, Dempsey |
| `devops` | Infrastructure & ops | Dempsey, Holman, Taleb, Grove |
| `data` | Data science | Kahneman, Taleb, Rams |
| `general` | General purpose | Kahneman, Taleb, Grove, Rams |
| `llm_review` | High-quality LLM review | Dempsey, Kahneman, Rams, Treasure |
| `sonotheia` | Audio defense & fintech | signal_analyst, compliance_auditor, Holman, Taleb |

---

## Customization

### Create Custom Personas

**Via CLI:**

```bash
council persona create --interactive
```

**Via Python:**

```python
from council_ai import Council
from council_ai.core.persona import Persona, PersonaCategory

# Create a custom persona
custom = Persona(
    id="my_advisor",
    name="My Custom Advisor",
    title="Domain Expert",
    emoji="🔮",
    category=PersonaCategory.CUSTOM,
    core_question="What would a domain expert ask?",
    razor="The key principle for decisions.",
    focus_areas=["Area 1", "Area 2", "Area 3"],
)

# Add to council
council = Council(api_key="your-key")
council.add_member(custom)
```

**Via YAML:**

```yaml
# ~/.config/council-ai/personas/my_advisor.yaml
id: my_advisor
name: My Custom Advisor
title: Domain Expert
emoji: "🔮"
category: custom

core_question: "What would a domain expert ask?"
razor: "The key principle for decisions."

traits:
  - name: Expertise
    description: Deep knowledge in the domain
    weight: 1.5
  - name: Practicality
    description: Focuses on actionable advice
    weight: 1.2

focus_areas:
  - Area 1
  - Area 2
  - Area 3
```

### Modify Persona Weights

```python
council = Council.for_domain("business", api_key="your-key")

# Increase Grove's influence (strategy focus)
council.set_member_weight("grove", 1.5)

# Decrease Kahneman's influence
council.set_member_weight("kahneman", 0.8)
```

### Add/Remove Traits

```python
from council_ai import get_persona

persona = get_persona("rams")

# Add a trait
persona.add_trait(
    name="Sustainability Focus",
    description="Considers environmental impact",
    weight=1.2
)

# Remove a trait
persona.remove_trait("Minimalism")

# Update a trait's weight
persona.update_trait("Simplification Obsession", weight=1.8)
```

---

## Consultation Modes

```python
from council_ai import Council
from council_ai.core.council import ConsultationMode

council = Council.for_domain("business", api_key="your-key")

# Individual: Each member responds separately
result = council.consult(query, mode=ConsultationMode.INDIVIDUAL)

# Synthesis: Individual responses + synthesized summary (default)
result = council.consult(query, mode=ConsultationMode.SYNTHESIS)

# Sequential: Members respond in order, seeing previous responses
result = council.consult(query, mode=ConsultationMode.SEQUENTIAL)

# Debate: Multiple rounds of discussion
result = council.consult(query, mode=ConsultationMode.DEBATE)

# Vote: Members vote on a decision
result = council.consult(query, mode=ConsultationMode.VOTE)
```

---

## Structured Synthesis, Weighting, and Failure Behavior

Council AI can optionally request a structured, JSON-schema-backed synthesis. When enabled,
the council first attempts structured synthesis; if that step raises an exception, it falls
back to the normal free-form synthesis. If the structured call returns no data (or returns
`None`), the formatted synthesis text will be empty. Streaming mode always uses free-form
synthesis, even when structured output is enabled, and will still emit synthesis events even
if the synthesis content is empty. Individual member failures are surfaced in their response
content, and only successful responses are included in the synthesis prompt, so if every
member fails you will see only error responses and an empty/low-signal synthesis.

Persona weights are stored on each persona (0.0–2.0) and can be adjusted per council member.
The synthesis prompt explicitly asks the model to weight advisor input by expertise relevance,
so weights act as guidance metadata you can use directly (or via custom hooks) rather than
changing generation parameters by default.

```python
from council_ai import Council, CouncilConfig

config = CouncilConfig()
config.use_structured_output = True  # Enable structured synthesis output

council = Council.for_domain("business", api_key="your-key", config=config)

# Adjust persona influence weights (0.0–2.0)
council.set_member_weight("grove", 1.5)
council.set_member_weight("kahneman", 0.8)

result = council.consult("Should we expand into Europe?")
print(result.structured_synthesis)  # Structured schema (if available)
print(result.synthesis)             # Markdown-formatted synthesis text
```

---

## Configuration

### Config File

Council AI stores configuration in `~/.config/council-ai/config.yaml`.
Override the location with `COUNCIL_AI_CONFIG_DIR`.

```yaml
api:
  provider: openai
  api_key: null  # Use environment variable instead
  model: gpt-4-turbo-preview  # or your preferred model
  base_url: null  # Optional for OpenAI-compatible endpoints

default_mode: synthesis
default_domain: general
temperature: 0.7
max_tokens_per_response: 1000
synthesis_provider: null
synthesis_model: null
synthesis_max_tokens: null

presets:
  my_team:
    domain: coding
    members: [rams, holman, grove]
    mode: synthesis
```

### CLI Configuration

```bash
# Set provider
council config set api.provider openai

# Set default domain
council config set default_domain startup

# Set temperature
council config set temperature 0.8

# View config
council config show
```

### Configuration Presets

Save commonly-used configurations as presets for quick access:

```bash
# Save a preset
council config preset-save my-review-team --domain coding --members rams,holman,kahneman --mode synthesis

# List all presets
council config preset-list

# Use a preset in consultation
council consult --preset my-review-team "Review this code"

# Delete a preset
council config preset-delete my-review-team
```

**Presets are perfect for:**

- Different project types (frontend, backend, devops)
- Different consultation styles (quick reviews vs deep analysis)
- Team-specific member combinations

### Set temperature

```bash
council config set temperature 0.8
```

### View config

```bash
council config show
```

---

## Provider Support

### Anthropic (Claude)

```python
council = Council(
    api_key="your-anthropic-key",
    provider="anthropic"
)
```

### OpenAI (GPT-4)

```python
council = Council(
    api_key="your-openai-key",
    provider="openai",
    model="gpt-4-turbo-preview",  # or "gpt-4", "gpt-3.5-turbo", etc.
    base_url="https://api.openai.com/v1"
)
```

### Google Gemini

```python
council = Council(
    api_key="your-gemini-key",
    provider="gemini"
)
```

### Custom HTTP Endpoint

```python
from council_ai.providers import HTTPProvider, register_provider

# Register a custom provider
register_provider("my_llm", HTTPProvider)

# Use it
council = Council(
    api_key="your-key",
    provider="http",
    base_url="http://localhost:8000/v1/completions"
)
```

You can also set the endpoint via `LLM_ENDPOINT` and pass an optional API key via
`HTTP_API_KEY` or `COUNCIL_API_KEY`.

You can set provider defaults via the config file (model, base URL) and override them
per council instance when needed.

---

## Web App (Standalone)

The web app is the primary user-testing surface. It features a modern, Dieter Rams-inspired UI built with **React** and **TypeScript**.

### Quick Launch

The easiest way to run the web app is using the launcher script, which automatically handles dependencies and building the frontend:

```bash
# Run the interactive launcher (handles npm install & build automatically)
./launcher.sh
```

### Manual Launch

If you prefer to run manually or differet parts separately:

```bash
# 1. Install Python dependencies
pip install -e ".[web]"

# 2. Build the React frontend (requires Node.js & npm)
npm install
npm run build

# 3. Run the web server
council web --reload
```

Then open <http://127.0.0.1:8000>.

### Development Mode

For frontend development with hot-reloading:

1. Start the backend API:
   ```bash
   council web --reload
   ```

2. In a separate terminal, start the React dev server:
   ```bash
   npm run dev
   ```
   Access the app at <http://localhost:5173>.

### Text-to-Speech (TTS) Integration 🔊

The web UI supports voice/audio responses powered by ElevenLabs (primary) and OpenAI TTS (fallback).

**Setup:**

1. **Add API Keys** - Add to your `.env` file:

```bash
ELEVENLABS_API_KEY=your-elevenlabs-key-here
OPENAI_API_KEY=your-openai-key-here  # Fallback
```

1. **Enable TTS** - In the web UI, go to Advanced Settings and toggle "Enable voice responses"

2. **Select Voice** (Optional) - Choose from available voices in the dropdown

**Configuration:**

Create or edit `~/.config/council-ai/config.yaml`:

```yaml
tts:
  enabled: false  # Set to true to enable by default
  provider: "elevenlabs"  # Primary provider
  voice: "EXAVITQu4vr4xnSDxMaL"  # Optional: specific voice ID
  fallback_provider: "openai"  # Fallback provider
  fallback_voice: "alloy"  # Optional: fallback voice
```

See `config.yaml.example` for full configuration options.

**Features:**

- 🎙️ **High-Quality Voices** - ElevenLabs provides natural, human-like voices
- 🔄 **Automatic Fallback** - Falls back to OpenAI TTS if ElevenLabs fails
- 🎚️ **Voice Selection** - Choose from multiple voices per provider
- 🔇 **Optional** - TTS is disabled by default, enable per-session or globally
- 📱 **Browser-Native** - Uses HTML5 audio player for compatibility

**Supported Providers:**

| Provider | Quality | Speed | Voices | Cost |
| :--- | :--- | :--- | :--- | :--- |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | Fast | 50+ | $$ |
| **OpenAI TTS** | ⭐⭐⭐⭐ | Very Fast | 6 | $ |

### Web App Features

- **Auto-Save Settings**: Provider, domain, mode, model, and base URL are automatically saved to browser localStorage
- **Clear Persistence Indicators**: Each field shows whether it's saved to browser or session-only
- **Manual Save/Reset**: Use the "💾 Save Settings" and "🔄 Reset to Defaults" buttons in Advanced Settings
- **Security**: API keys are never stored - only used for the current session
- **History**: Recent consultations are automatically saved and displayed

**Settings Persistence:**

- ✅ Saved to browser: Provider, Model, Base URL, Domain, Mode
- ❌ Session only: Custom Members, API Key

---

## Quality & Testing Policy

See [CONTRIBUTING.md](CONTRIBUTING.md) for the testing, linting, and formatting policy.

---

## Python API Reference

**📖 [Complete API Documentation](documentation/API_REFERENCE.md)**

For comprehensive API documentation including all classes, methods, parameters, and examples, see the [API Reference Guide](documentation/API_REFERENCE.md).

### Quick Reference

Below is a quick reference for common API usage. For detailed documentation, see the [full API reference](documentation/API_REFERENCE.md).

### Council

```python
from council_ai import Council

# Create
council = Council(api_key="key", provider="anthropic")
council = Council.for_domain("business", api_key="key")

# Members
council.add_member("rams")
council.add_member(custom_persona)
council.remove_member("rams")
council.set_member_weight("grove", 1.5)
council.enable_member("holman")
council.disable_member("holman")
council.list_members()
council.clear_members()

# Consult
result = council.consult("query")
result = council.consult("query", context="additional context")
result = council.consult("query", mode=ConsultationMode.DEBATE)
result = council.consult("query", members=["rams", "grove"])

# Async
result = await council.consult_async("query")
```

### ConsultationResult

```python
result = council.consult("query")

# Access
result.query          # Original query
result.synthesis      # Synthesized response
result.responses      # List of MemberResponse
result.mode           # Consultation mode used
result.timestamp      # When consulted

# Export
result.to_markdown()  # Markdown format
result.to_dict()      # Dictionary format

# Individual responses
for response in result.responses:
    response.persona      # Persona object
    response.content      # Response text
    response.error        # Error if any
```

### Persona

```python
from council_ai import get_persona, list_personas
from council_ai.core.persona import Persona, PersonaManager

# Get built-in
persona = get_persona("rams")
all_personas = list_personas()

# Create
persona = Persona(
    id="custom",
    name="Custom",
    title="Title",
    core_question="Question?",
    razor="Principle.",
)

# Modify
persona.add_trait("name", "description", weight=1.2)
persona.remove_trait("name")
persona.update_trait("name", weight=1.5)

# Export
persona.to_yaml()
persona.save_to_yaml("path.yaml")

# Clone with modifications
new_persona = persona.clone(new_id="custom_v2", weight=1.5)
```

---

## Examples

### Code Review

```python
council = Council.for_domain("coding", api_key=key)
result = council.consult("""
Review this API design:

POST /users
- Creates a new user
- Accepts: {email, password, name}
- Returns: {id, email, name, created_at}

What issues do you see?
""")
```

### Business Strategy

```python
council = Council.for_domain("business", api_key=key)
result = council.consult("""
We're a B2B SaaS company with $2M ARR.
A competitor just raised $50M.
Should we:
A) Raise funding to compete
B) Focus on profitability and niche down
C) Seek acquisition

What do you advise?
""")
```

### Career Decision

```python
council = Council.for_domain("career", api_key=key)
result = council.consult("""
I'm a senior engineer at a stable company.
I've been offered a CTO role at an early-stage startup.

Pros:
- 3x equity, 20% salary cut
- Full technical ownership
- High growth potential

Cons:
- Startup has 18 months runway
- Would leave a team I built
- More stress, less stability

How should I think about this?
""")
```

### Creative Project

```python
council = Council.for_domain("creative", api_key=key)
council.add_member("treasure")  # Add sonic lens

result = council.consult("""
I'm designing a podcast intro.
It needs to:
- Grab attention in 5 seconds
- Convey "thoughtful tech commentary"
- Be memorable but not annoying

What elements should I include?
""")
```

### Repository Review

```python
# Review your repository's code, design, and functionality
# See examples/review_repository.py for full implementation
council = Council(api_key=key)

# Code quality review
council.add_member("rams")      # Design & Simplicity
council.add_member("holman")    # Security
council.add_member("kahneman")  # Cognitive Load

result = council.consult("Review code quality and architecture...")

# Also review design/UX and functionality/robustness
# with different persona combinations
```

### LLM Response Reviewer

Council AI includes a specialized "Supreme Court-style" reviewer for evaluating multiple LLM responses. See the [LLM Response Reviewer Setup Guide](documentation/REVIEWER_SETUP.md) for details.

---

## Contributing

Contributions welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

```bash
# Development setup
git clone https://github.com/doronpers/council-ai
cd council-ai
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=council_ai

# Format code
black src/
ruff check src/

# Try the quickstart demo (no API key needed)
python examples/quickstart.py
```

### Adding New Personas

Create a YAML file in `src/council_ai/personas/`:

```yaml
id: your_persona
name: Full Name
title: Brief Title
emoji: "🎭"
category: advisory

core_question: "The key question?"
razor: "The decision principle."

traits:
  - name: Trait Name
    description: What it means
    weight: 1.5

focus_areas:
  - Area 1
  - Area 2
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on adding domains, providers, and more.

---

## License

MIT License - see LICENSE file.

---

## Credits

Inspired by the decision-making frameworks of:

- **Dieter Rams** - Industrial design principles
- **Martin Dempsey** - Mission command leadership
- **Daniel Kahneman** - Behavioral economics
- **Julian Treasure** - Sound and communication
- **Pablos Holman** - Hacker mindset
- **Nassim Nicholas Taleb** - Antifragility and risk
- **Andy Grove** - Strategic management

---

Built with ❤️ for better decisions.
