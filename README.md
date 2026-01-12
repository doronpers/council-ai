# 🏛️ Council AI

**Intelligent Advisory Council System** - Get advice from a council of AI-powered personas with diverse perspectives and expertise.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Quickstart (No API Key Required)

Want to explore Council AI before setting up an API key? Run:

```bash
python examples/quickstart.py
```

This interactive demo shows you:

- All 7 built-in personas and their characteristics
- 12 domain presets and what they're for
- How to set up and use councils
- Example usage patterns

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

- 🎭 **7 Built-in Personas** - Advisory Council (build it right) + Red Team (break & survive)
- 🌐 **12 Domain Presets** - Coding, business, startup, creative, career, and more
- 🔧 **Fully Customizable** - Create your own personas, adjust weights, modify traits
- 🤖 **Multi-Provider Support** - Anthropic, OpenAI, Google Gemini, or custom endpoints
- 💬 **Multiple Modes** - Individual, synthesis, debate, or vote
- 🧭 **Standalone Web App** - A focused web UI for user testing
- 📦 **Portable Package** - pip-installable, use in any project

---

## Installation

**From PyPI (when published):**

```bash
# Basic installation
pip install council-ai

# With Anthropic Claude support
pip install council-ai[anthropic]

# With OpenAI GPT support
pip install council-ai[openai]

# With Google Gemini support
pip install council-ai[gemini]

# Full installation (all providers)
pip install council-ai[all]
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

**Priority Order:**

1. CLI flags (`--api-key`)
2. Environment variables
3. `.env` file (auto-loaded)
4. Config file (`~/.config/council-ai/config.yaml`)

### CLI Usage

```bash
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

## Configuration

### Config File

Council AI stores configuration in `~/.config/council-ai/config.yaml`:

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

presets:
  my_team:
    name: My Review Team
    members: [rams, holman, grove]
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
    endpoint="http://localhost:8000/v1/completions"
)
```

You can also set the endpoint via `LLM_ENDPOINT` and pass an optional API key via
`HTTP_API_KEY` or `COUNCIL_API_KEY`.

You can set provider defaults via the config file (model, base URL) and override them
per council instance when needed.

---

## Web App (Standalone)

The web app is the primary user-testing surface. It provides a simple, focused UI for
consultations and is intentionally minimal.

```bash
# Install web dependencies
pip install -e ".[web]"

# Run the web app
council web --reload
```

Then open <http://127.0.0.1:8000>.

---

## Quality & Testing Policy

See [CONTRIBUTING.md](CONTRIBUTING.md) for the testing, linting, and formatting policy.

---

## Python API Reference

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
