# Council AI Examples

This directory contains examples demonstrating various ways to use Council AI.

## Quick Start

### 1. Simple Example

The fastest way to get started:

```bash
# Install with a provider
pip install -e .[anthropic]

# Set your API key
export ANTHROPIC_API_KEY="your-key"

# Run the example
python examples/simple_example.py
```

### 2. Usage Examples

Comprehensive examples covering all features:

```bash
python examples/usage_examples.py
```

### 3. Repository Review

Use the council to review a repository's code, design, and functionality:

```bash
python examples/review_repository.py
```

This example demonstrates using the embedded council personas to provide a comprehensive review of the repository itself, analyzing:

- Code quality and architecture
- Design and user experience
- Functionality and robustness

## Examples Overview

| File                   | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `simple_example.py`    | Basic consultation example - perfect for getting started    |
| `usage_examples.py`    | Comprehensive examples of all features                      |
| `review_repository.py` | Use council personas to review repository code, design & UX |

## Web App

For user testing, run the standalone web app:

```bash
pip install -e ".[web]"
council web --reload
```

## Key Concepts Demonstrated

### Creating a Council

```python
from council_ai import Council

# Use a domain preset
council = Council.for_domain("business", api_key="key")

# Or build custom
council = Council(api_key="key")
council.add_member("DR")
council.add_member("AG")
```

### Consulting the Council

```python
result = council.consult("Should we expand to Europe?")
print(result.synthesis)

for response in result.responses:
    print(f"{response.persona.emoji} {response.persona.name}:")
    print(response.content)
```

### Custom Personas

```python
from council_ai import Persona, PersonaCategory

my_expert = Persona(
    id="expert",
    name="My Expert",
    title="Domain Specialist",
    emoji="🔮",
    category=PersonaCategory.CUSTOM,
    core_question="What should we consider?",
    razor="Think deeply, act wisely.",
    focus_areas=["Strategy", "Execution"]
)

council.add_member(my_expert)
```

### Different Consultation Modes

```python
from council_ai import ConsultationMode

# Individual responses only
result = council.consult(query, mode=ConsultationMode.INDIVIDUAL)

# With synthesis (default)
result = council.consult(query, mode=ConsultationMode.SYNTHESIS)

# Sequential responses
result = council.consult(query, mode=ConsultationMode.SEQUENTIAL)

# Debate mode
result = council.consult(query, mode=ConsultationMode.DEBATE)

# Vote mode
result = council.consult(query, mode=ConsultationMode.VOTE)
```

## Available Domains

Run `council domain list` to see all domains, or use these common ones:

- **coding** - Software development and code review
- **business** - Strategic business decisions
- **startup** - Early-stage startup decisions
- **product** - Product management
- **career** - Career and job decisions
- **creative** - Creative projects
- **writing** - Written content
- **leadership** - Team and organizational leadership

## Need Help?

- Check the main README.md for full documentation
- Run `council --help` for CLI usage
- Run `council persona list` to see all available personas
- Run `council domain list` to see all available domains
