# Persona Archetype System Guide

This guide explains the archetype system introduced in Council AI v2.0 and how to use it for creating and managing personas.

## Overview

The archetype system separates **generic personality templates** (shared publicly) from **specialized personas** (customized privately). This enables:

- **Maintainability**: Core traits managed in one place
- **Scalability**: Add unlimited new personas without code changes
- **Privacy**: Keep real names and sensitive customizations private
- **Reusability**: Share archetypes across multiple personas

## The Five Core Archetypes

### 1. Quality Advocate

**File**: `src/council_ai/personas/archetypes/quality_advocate.yaml`

A design philosophy specialist focused on simplicity, function, and timelessness.

**Core Traits**:

- Simplification Focus (1.8) - PRIMARY
- Functional Clarity (1.5) - BALANCED
- Timeless Thinking (1.2) - SECONDARY

**Core Question**: "Is this as simple as possible?"

**Decision Principle**: "Less, but better. Good design is as little design as possible."

**Example Specialization**: Dieter Rams

**Use When**: You need advice on reducing complexity, improving UX, or achieving timeless design.

---

### 2. Security Specialist

**File**: `src/council_ai/personas/archetypes/security_specialist.yaml`

An adversarial security expert who thinks like an attacker.

**Core Traits**:

- Adversarial Thinking (1.8) - PRIMARY
- Creative Exploitation (1.6) - BALANCED
- Defense in Depth (1.4) - SECONDARY

**Core Question**: "How would I break this?"

**Decision Principle**: "Everything is hackable. Security through obscurity fails. Assume breach."

**Example Specialization**: Pablos Holman

**Use When**: You need red-team analysis, threat modeling, or penetration testing perspectives.

---

### 3. Strategic Leader

**File**: `src/council_ai/personas/archetypes/strategic_leader.yaml`

A long-term strategic thinker focused on competitive advantage and strategic inflection points.

**Core Traits**:

- Strategic Paranoia (1.7) - PRIMARY
- Inflection Point Detection (1.6) - BALANCED
- Operational Excellence (1.4) - SECONDARY

**Core Question**: "What 10X force could make us irrelevant?"

**Decision Principle**: "Only the paranoid survive. Strategic inflection points destroy companies that don't adapt."

**Example Specialization**: Andrew Grove

**Use When**: You need strategic planning, competitive analysis, or management advice.

---

### 4. Risk Analyst

**File**: `src/council_ai/personas/archetypes/risk_analyst.yaml`

A probabilistic risk specialist focused on tail risks and antifragility.

**Core Traits**:

- Black Swan Detection (1.8) - PRIMARY
- Antifragility Focus (1.7) - PRIMARY
- Skin in the Game (1.5) - SECONDARY

**Core Question**: "What's the hidden risk?"

**Decision Principle**: "What doesn't kill you makes you stronger. Seek antifragility, not just resilience."

**Example Specialization**: Nassim Taleb

**Use When**: You need risk assessment, tail risk analysis, or antifragility strategies.

---

### 5. Cognitive Scientist

**File**: `src/council_ai/personas/archetypes/cognitive_scientist.yaml`

A human behavior expert focused on decision-making and behavioral economics.

**Core Traits**:

- Cognitive Bias Awareness (1.8) - PRIMARY
- System 1/System 2 Thinking (1.6) - BALANCED
- Loss Aversion Focus (1.4) - SECONDARY

**Core Question**: "Does this work with human cognition?"

**Decision Principle**: "People don't think rationally. Design for how humans actually think, not how they should."

**Example Specialization**: Daniel Kahneman

**Use When**: You need behavioral analysis, UX psychology, or human decision-making insights.

---

## Repository Organization

### Public Repository (council-ai)

```
src/council_ai/personas/
├── archetypes/                     # Generic trait templates (5 base personas)
│   ├── quality_advocate.yaml
│   ├── security_specialist.yaml
│   ├── strategic_leader.yaml
│   ├── risk_analyst.yaml
│   └── cognitive_scientist.yaml
├── [domain]/                       # Domain-specific persona collections
│   └── *.yaml
└── *.yaml                          # Generic personas (non-specialized)
```

**Contents**: Framework code, archetypes, generic personas, shared utilities
**Safe to**: Fork, share, distribute, make public

### Private Repository (council-ai-personal)

```
personal/personas/
├── rams.yaml                       # Dieter Rams (quality_advocate)
├── holman.yaml                     # Pablos Holman (security_specialist)
├── grove.yaml                      # Andrew Grove (strategic_leader)
├── taleb.yaml                      # Nassim Taleb (risk_analyst)
└── kahneman.yaml                   # Daniel Kahneman (cognitive_scientist)
```

**Contents**: Real-name personas, personal customizations, private configurations
**Safe to**: Keep private, customize freely, extend without affecting main repo

---

## Creating Custom Personas

### Method 1: Extend an Existing Archetype

Create a new YAML file that references an archetype:

```yaml
archetype: quality_advocate # Reference the archetype
category: advisory
name: Your Name
title: Your Title
emoji: '🎭'
id: YN

# Optional: Override or add specific traits
traits:
  - name: Your Custom Trait
    description: What it means
    weight: 1.5

# Optional: Add focus areas specific to your persona
focus_areas:
  - Custom Focus Area 1
  - Custom Focus Area 2

# Customize model parameters if needed
provider: lmstudio
model: mixtral-8x7b-v0.1
model_params:
  temperature: 0.6
  top_p: 0.9

# Add metadata for tracking
metadata:
  real_person: 'Full Name (if applicable)'
  era: '1900–present'
  domain: 'Your Domain'
```

### Method 2: Create a New Archetype

For a personality pattern that doesn't fit existing archetypes:

1. Create a new file: `src/council_ai/personas/archetypes/your_archetype.yaml`
2. Define core traits (aim for 3-5 key traits)
3. Set appropriate trait weights
4. Document with core_question and razor
5. Create specialized personas that reference it

**Archetype Template**:

```yaml
id: your_archetype
name: Archetype Name
title: Brief Description
emoji: '🎯'
category: advisory # or: adversarial, strategic, analytical

core_question: 'Key question this archetype asks?'
razor: 'Core decision principle or philosophy'

traits:
  - name: Key Trait 1
    description: What it means and why it matters
    weight: 1.8
  - name: Key Trait 2
    description: What it means and why it matters
    weight: 1.5
  - name: Key Trait 3
    description: What it means and why it matters
    weight: 1.2

focus_areas:
  - Focus Area 1
  - Focus Area 2
  - Focus Area 3

provider: lmstudio
model: mixtral-8x7b-v0.1
model_params:
  temperature: 0.5
  top_p: 0.9
  top_k: 50
  repetition_penalty: 1.1

weight: 1.0
enabled: true
```

---

## Metadata Best Practices

Always include metadata for proper tracking and attribution:

```yaml
metadata:
  # For real-name personas (should be in private repo)
  real_person: 'Full Name'
  era: '1930–2020'

  # For custom personas
  domain: 'Specific domain or field'
  version: '1.0'
  created: '2024-01-25'

  # For tracking and sourcing
  source: 'Internal | External | Custom'
  confidence: 'High | Medium | Low'
  notes: 'Any additional context'
```

---

## Trait Weight System

Trait weights (1.0 - 2.0) control influence on decision-making:

| Range     | Influence           | Example                 |
| --------- | ------------------- | ----------------------- |
| 1.0 - 1.2 | Secondary (low)     | Tertiary consideration  |
| 1.3 - 1.6 | Balanced (moderate) | Balanced importance     |
| 1.7 - 2.0 | Primary (high)      | Core to decision-making |

**Example: Quality Advocate**

- Simplification Focus (1.8) - PRIMARY: Most important trait
- Functional Clarity (1.5) - BALANCED: Important but not primary
- Timeless Thinking (1.2) - SECONDARY: Supporting trait

---

## Privacy & Customization Model

```
┌─────────────────────────────────────┬──────────────────────┐
│ council-ai (Public)                 │ council-ai-personal  │
├─────────────────────────────────────┼──────────────────────┤
│ ✓ Archetypes (generic)              │ ✓ Real-name personas │
│ ✓ Domain collections                │ ✓ Personal configs   │
│ ✓ Framework & core code             │ ✓ Custom settings    │
│ ✓ Safe to fork/share                │ ✓ Private, not shared│
└─────────────────────────────────────┴──────────────────────┘
         ↓ Auto-detected & loaded together ↓
    Seamless multi-persona consultation
```

**Key Benefits**:

- **Legal Protection**: Real names kept private
- **Clean Separation**: Framework vs. customization
- **Easy to Fork**: Share only what's appropriate
- **Scalable**: Add unlimited custom personas
- **Transparent**: Know what's shared vs. private

---

## Using Archetypes in Code

When Council AI loads personas, it automatically resolves archetype references:

```python
from council_ai import PersonaRegistry

registry = PersonaRegistry()

# Load from YAML (handles archetype resolution)
rams_persona = registry.load('rams')

# The persona inherits archetype traits and characteristics
print(rams_persona.name)        # → "Dieter Rams"
print(rams_persona.traits)      # → Includes all quality_advocate traits
print(rams_persona.archetype)   # → "quality_advocate"
```

---

## Best Practices

1. **Minimize Duplication**: Use archetypes instead of repeating traits
2. **Keep Archetypes Generic**: Avoid real names or specific details
3. **Document Everything**: Add comments explaining trait purposes
4. **Version Your Personas**: Track changes with metadata
5. **Test Your Personas**: Verify they respond as expected
6. **Group by Domain**: Organize personas by use case or industry
7. **Separate Public/Private**: Keep sensitive customizations in council-ai-personal
8. **Use Descriptive Titles**: Help users understand persona purpose at a glance
9. **Provide Focus Areas**: Help users know when to consult this persona
10. **Keep Weights Realistic**: Aim for 5-8 points total across traits

---

## Troubleshooting

### Persona not loading

- Check YAML syntax: `yamllint personal/personas/your_persona.yaml`
- Verify archetype reference exists: `ls src/council_ai/personas/archetypes/`
- Check persona ID is unique and properly formatted
- Look for typos in archetype name

### Trait not appearing

- Verify trait is defined in archetype or persona YAML
- Check trait name spelling (YAML is case-sensitive)
- Ensure trait weight is valid (1.0 - 2.0)
- Check for conflicting trait definitions

### Persona behaving unexpectedly

- Check model parameters (temperature, top_p, etc.)
- Verify traits are appropriate for the use case
- Test with a simple prompt first
- Check for conflicting trait definitions between archetype and persona
- Review focus_areas to ensure relevance

### Archetype not resolving

- Verify archetype file exists in correct directory
- Check archetype ID matches reference in persona
- Ensure archetype YAML is valid (use yamllint)
- Check for typos in archetype ID

---

## Contributing

To propose new archetypes or improvements:

1. Create an issue describing the archetype and use cases
2. Provide sample traits and decision principles
3. Submit a PR with the archetype YAML file
4. Include documentation and real-world examples
5. Gather feedback from the community

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Related Documentation

- [API Reference](documentation/API_REFERENCE.md) - Complete Python API
- [Custom Personas Guide](https://github.com/doronpers/council-ai-personal) - Private repo setup
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [README.md](README.md) - Main documentation

---

**Last Updated**: January 25, 2026
**Version**: 2.0
