# 🏛️ Council AI

**Intelligent Advisory Council System** - Get advice from a council of AI-powered personas with diverse perspectives and expertise.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## Overview

Council AI provides a framework for consulting multiple AI "personas" - each with distinct expertise, perspectives, and decision-making approaches. Whether you're making business decisions, reviewing code, planning strategy, or working on creative projects, the council provides comprehensive, multi-perspective advice.

**Key Features:**
- 🎭 **7 Built-in Personas** - Advisory Council (build it right) + Red Team (break & survive)
- 🌐 **12 Domain Presets** - Coding, business, startup, creative, career, and more
- 🔧 **Fully Customizable** - Create your own personas, adjust weights, modify traits
- 🤖 **Multi-Provider Support** - Anthropic, OpenAI, or custom endpoints
- 💬 **Multiple Modes** - Individual, synthesis, debate, or vote
- 📦 **Portable Package** - pip-installable, use in any project

---

## Quick Start

### Installation

```bash
# Basic installation
pip install council-ai

# With Anthropic support
pip install council-ai[anthropic]

# With OpenAI support
pip install council-ai[openai]

# Full installation (all providers)
pip install council-ai[all]
```

### Set Your API Key

```bash
# Anthropic
export ANTHROPIC_API_KEY="your-key"

# Or OpenAI
export OPENAI_API_KEY="your-key"
```

### CLI Usage

```bash
# Simple consultation
council consult "Should I take this job offer?"

# With a specific domain
council consult --domain startup "Should we pivot?"

# With specific personas
council consult --members grove --members taleb "What's our biggest risk?"

# Interactive mode
council interactive
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
|---------|-------|---------------|
| 🎨 **Dieter Rams** | Simplification, Design | "Is this as simple as possible?" |
| 🎖️ **Martin Dempsey** | Mission Clarity, Autonomy | "Can this operate without asking permission?" |
| 🧠 **Daniel Kahneman** | Cognitive Load, UX | "Does this work with human cognition?" |
| 🔊 **Julian Treasure** | Communication, Listening | "Are we listening with integrity?" |

### Red Team Council (Break & Survive)

| Persona | Focus | Core Question |
|---------|-------|---------------|
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
|--------|-------------|------------------|
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
  provider: anthropic
  api_key: null  # Use environment variable instead
  model: claude-sonnet-4-20250514

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
    provider="openai"
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

---

## Contributing

Contributions welcome! Please read the contributing guidelines first.

```bash
# Development setup
git clone https://github.com/doronpers/council-ai
cd council-ai
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

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
