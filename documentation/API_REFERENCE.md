# Council AI - Python API Reference

Complete reference for the Council AI Python API.

## Table of Contents

- [Core Classes](#core-classes)
  - [Council](#council)
  - [CouncilConfig](#councilconfig)
  - [ConsultationMode](#consultationmode)
- [Result Classes](#result-classes)
  - [ConsultationResult](#consultationresult)
  - [MemberResponse](#memberresponse)
- [Persona Management](#persona-management)
  - [Persona](#persona)
  - [PersonaCategory](#personacategory)
  - [Trait](#trait)
  - [PersonaManager](#personamanager)
- [Domain System](#domain-system)
  - [Domain](#domain)
  - [DomainCategory](#domaincategory)
- [Provider System](#provider-system)
  - [LLMProvider](#llmprovider)
- [Utility Functions](#utility-functions)

---

## Core Classes

### Council

The main class for creating and managing advisory councils.

#### Constructor

```python
Council(
    api_key: Optional[str] = None,
    provider: str = "anthropic",
    config: Optional[CouncilConfig] = None,
    persona_manager: Optional[PersonaManager] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    history: Optional[Any] = None,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `Optional[str]` | `None` | API key for the LLM provider. If not provided, will be read from environment variables or config file. |
| `provider` | `str` | `"anthropic"` | LLM provider name. Options: `"anthropic"`, `"openai"`, `"gemini"`, `"http"`. |
| `config` | `Optional[CouncilConfig]` | `None` | Council configuration. Uses default config if not provided. |
| `persona_manager` | `Optional[PersonaManager]` | `None` | Custom persona manager. Uses global persona manager if not provided. |
| `model` | `Optional[str]` | `None` | Model name override (e.g., `"gpt-4"`, `"claude-3-opus-20240229"`). |
| `base_url` | `Optional[str]` | `None` | Base URL override for custom endpoints. |
| `history` | `Optional[Any]` | `None` | ConsultationHistory instance for auto-saving consultations. |

**Example:**

```python
from council_ai import Council

# Basic usage with environment variable API key
council = Council(provider="anthropic")

# With explicit API key
council = Council(api_key="your-key", provider="openai", model="gpt-4")

# With custom configuration
from council_ai import CouncilConfig
config = CouncilConfig(temperature=0.8, max_tokens_per_response=1500)
council = Council(api_key="your-key", config=config)
```

#### Class Methods

##### `for_domain()`

Create a council pre-configured for a specific domain.

```python
@classmethod
def for_domain(
    cls,
    domain: str,
    api_key: Optional[str] = None,
    provider: str = "anthropic",
    **kwargs
) -> Council
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `domain` | `str` | Required | Domain ID (e.g., `"coding"`, `"business"`, `"startup"`). |
| `api_key` | `Optional[str]` | `None` | API key for the LLM provider. |
| `provider` | `str` | `"anthropic"` | LLM provider name. |
| `**kwargs` | | | Additional arguments passed to the Council constructor. |

**Returns:** `Council` instance with domain-specific personas pre-loaded.

**Example:**

```python
from council_ai import Council

# Create a business strategy council
council = Council.for_domain("business", api_key="your-key")

# Create a coding review council
council = Council.for_domain("coding", api_key="your-key", provider="openai")
```

#### Member Management Methods

##### `add_member()`

Add a persona to the council.

```python
def add_member(
    self,
    persona: Union[str, Persona],
    weight: Optional[float] = None
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `persona` | `Union[str, Persona]` | Required | Persona ID string (e.g., `"rams"`) or Persona instance. |
| `weight` | `Optional[float]` | `None` | Influence weight (0.0-2.0). If not provided, uses persona's default weight. |

**Example:**

```python
# Add by ID
council.add_member("rams")

# Add with custom weight
council.add_member("grove", weight=1.5)

# Add custom persona
from council_ai import Persona
custom = Persona(id="expert", name="Domain Expert", ...)
council.add_member(custom)
```

##### `remove_member()`

Remove a persona from the council.

```python
def remove_member(self, persona_id: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `persona_id` | `str` | ID of the persona to remove. |

**Example:**

```python
council.remove_member("rams")
```

##### `get_member()`

Get a council member by ID.

```python
def get_member(self, persona_id: str) -> Optional[Persona]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `persona_id` | `str` | ID of the persona to retrieve. |

**Returns:** `Persona` instance if found, `None` otherwise.

**Example:**

```python
persona = council.get_member("rams")
if persona:
    print(f"Found: {persona.name}")
```

##### `list_members()`

List all council members.

```python
def list_members(self) -> List[Persona]
```

**Returns:** List of all `Persona` instances in the council.

**Example:**

```python
members = council.list_members()
for member in members:
    print(f"{member.emoji} {member.name} - {member.title}")
```

##### `clear_members()`

Remove all members from the council.

```python
def clear_members(self) -> None
```

**Example:**

```python
council.clear_members()
```

##### `set_member_weight()`

Update a member's influence weight.

```python
def set_member_weight(self, persona_id: str, weight: float) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `persona_id` | `str` | ID of the persona to update. |
| `weight` | `float` | New weight value (0.0-2.0). Higher values increase influence. |

**Example:**

```python
# Increase Grove's influence
council.set_member_weight("grove", 1.5)

# Decrease Kahneman's influence
council.set_member_weight("kahneman", 0.7)
```

##### `enable_member()`

Enable a disabled member.

```python
def enable_member(self, persona_id: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `persona_id` | `str` | ID of the persona to enable. |

**Example:**

```python
council.enable_member("holman")
```

##### `disable_member()`

Disable a member (they won't respond to consultations).

```python
def disable_member(self, persona_id: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `persona_id` | `str` | ID of the persona to disable. |

**Example:**

```python
council.disable_member("holman")
```

#### Consultation Methods

##### `consult()`

Consult the council on a query (synchronous).

```python
def consult(
    self,
    query: str,
    context: Optional[str] = None,
    mode: Optional[ConsultationMode] = None,
    members: Optional[List[str]] = None,
) -> ConsultationResult
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | The question or topic to consult about. |
| `context` | `Optional[str]` | `None` | Additional context or background information. |
| `mode` | `Optional[ConsultationMode]` | `None` | Consultation mode. Uses config default if not provided. |
| `members` | `Optional[List[str]]` | `None` | List of persona IDs to consult. If not provided, uses all enabled members. |

**Returns:** `ConsultationResult` with individual responses and synthesis.

**Example:**

```python
# Simple consultation
result = council.consult("Should we redesign our API?")

# With context
result = council.consult(
    query="Should we redesign our API?",
    context="We have 10k users and frequent breaking changes."
)

# With specific mode
from council_ai import ConsultationMode
result = council.consult(
    query="How should we prioritize features?",
    mode=ConsultationMode.DEBATE
)

# With specific members
result = council.consult(
    query="Security review needed",
    members=["holman", "taleb"]
)
```

##### `consult_async()`

Consult the council asynchronously.

```python
async def consult_async(
    self,
    query: str,
    context: Optional[str] = None,
    mode: Optional[ConsultationMode] = None,
    members: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    auto_recall: bool = True,
) -> ConsultationResult
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | The question or topic to consult about. |
| `context` | `Optional[str]` | `None` | Additional context information. |
| `mode` | `Optional[ConsultationMode]` | `None` | Consultation mode. |
| `members` | `Optional[List[str]]` | `None` | List of persona IDs to consult. |
| `session_id` | `Optional[str]` | `None` | Session ID for conversation history. |
| `auto_recall` | `bool` | `True` | Whether to automatically include conversation history. |

**Returns:** `ConsultationResult` with individual responses and synthesis.

**Example:**

```python
import asyncio
from council_ai import Council

async def main():
    council = Council.for_domain("business", api_key="your-key")
    result = await council.consult_async("Should we pivot?")
    print(result.synthesis)

asyncio.run(main())
```

##### `consult_stream()`

Stream consultation results as they're generated.

```python
async def consult_stream(
    self,
    query: str,
    context: Optional[str] = None,
    mode: Optional[ConsultationMode] = None,
    members: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    auto_recall: bool = True,
) -> AsyncIterator[Dict[str, Any]]
```

**Parameters:** Same as `consult_async()`.

**Yields:** Dictionary events with keys:
- `event`: Event type (`"progress"`, `"response"`, `"synthesis"`, `"complete"`)
- `data`: Event-specific data

**Example:**

```python
import asyncio
from council_ai import Council

async def main():
    council = Council.for_domain("business", api_key="your-key")
    
    async for event in council.consult_stream("Market analysis needed"):
        if event["event"] == "response":
            persona = event["data"]["persona"]
            content = event["data"]["content"]
            print(f"{persona['emoji']} {persona['name']}: {content}")
        elif event["event"] == "synthesis":
            print(f"\nSynthesis: {event['data']['synthesis']}")

asyncio.run(main())
```

---

### CouncilConfig

Configuration options for a Council instance.

```python
from council_ai import CouncilConfig

config = CouncilConfig(
    name: str = "Advisory Council",
    description: str = "",
    mode: ConsultationMode = ConsultationMode.SYNTHESIS,
    max_tokens_per_response: int = 1000,
    temperature: float = 0.7,
    include_reasoning: bool = True,
    include_confidence: bool = True,
    synthesis_prompt: Optional[str] = None,
    synthesis_provider: Optional[str] = None,
    synthesis_model: Optional[str] = None,
    synthesis_max_tokens: Optional[int] = None,
    context_window: int = 10,
    use_structured_output: bool = False,
    export_enabled_state: bool = False,
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | `"Advisory Council"` | Council name for identification. |
| `description` | `str` | `""` | Council description. |
| `mode` | `ConsultationMode` | `SYNTHESIS` | Default consultation mode. |
| `max_tokens_per_response` | `int` | `1000` | Maximum tokens per member response. |
| `temperature` | `float` | `0.7` | Sampling temperature (0.0-2.0). |
| `include_reasoning` | `bool` | `True` | Whether to include reasoning in responses. |
| `include_confidence` | `bool` | `True` | Whether to include confidence levels. |
| `synthesis_prompt` | `Optional[str]` | `None` | Custom synthesis prompt template. |
| `synthesis_provider` | `Optional[str]` | `None` | Provider override for synthesis. |
| `synthesis_model` | `Optional[str]` | `None` | Model override for synthesis. |
| `synthesis_max_tokens` | `Optional[int]` | `None` | Max tokens override for synthesis. |
| `context_window` | `int` | `10` | Number of previous exchanges to include. |
| `use_structured_output` | `bool` | `False` | Enable structured synthesis output (experimental). |
| `export_enabled_state` | `bool` | `False` | Include enabled flags in exports. |

**Example:**

```python
from council_ai import Council, CouncilConfig

# Create custom config
config = CouncilConfig(
    name="Security Review Council",
    temperature=0.5,  # More focused
    max_tokens_per_response=1500,
    include_confidence=True,
)

council = Council(api_key="your-key", config=config)
```

---

### ConsultationMode

Enum defining how the council responds to queries.

```python
from council_ai import ConsultationMode
```

**Values:**

| Mode | Description | Use Case |
|------|-------------|----------|
| `INDIVIDUAL` | Each member responds separately in parallel. | Quick, independent opinions. |
| `SEQUENTIAL` | Members respond in order, seeing previous responses. | Building on each other's ideas. |
| `SYNTHESIS` | Individual responses + synthesized summary (default). | Comprehensive advice with summary. |
| `DEBATE` | Multi-round debate between members. | Exploring multiple perspectives deeply. |
| `VOTE` | Members vote on a decision. | Binary or multiple-choice decisions. |

**Example:**

```python
from council_ai import Council, ConsultationMode

council = Council.for_domain("business", api_key="your-key")

# Use debate mode for complex decisions
result = council.consult(
    "Should we pivot to B2B?",
    mode=ConsultationMode.DEBATE
)

# Use sequential for step-by-step analysis
result = council.consult(
    "Walk through this architecture design",
    mode=ConsultationMode.SEQUENTIAL
)
```

---

## Result Classes

### ConsultationResult

The result of a council consultation.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The original query. |
| `responses` | `List[MemberResponse]` | Individual member responses. |
| `synthesis` | `Optional[str]` | Synthesized summary of all responses. |
| `context` | `Optional[str]` | Context that was provided with the query. |
| `mode` | `str` | Consultation mode used. |
| `timestamp` | `datetime` | When the consultation occurred. |
| `id` | `Optional[str]` | Unique consultation ID. |
| `tags` | `List[str]` | Tags for categorization. |
| `notes` | `Optional[str]` | Additional notes. |
| `structured_synthesis` | `Optional[Any]` | Structured output (if enabled). |
| `action_items` | `List[Any]` | Extracted action items. |
| `recommendations` | `List[Any]` | Extracted recommendations. |
| `pros_cons` | `Optional[Any]` | Pros/cons analysis. |
| `synthesis_audio_url` | `Optional[str]` | Audio URL for synthesis (if TTS enabled). |
| `session_id` | `Optional[str]` | Session ID for conversation tracking. |

**Methods:**

#### `to_dict()`

Export to dictionary format.

```python
def to_dict(self) -> Dict[str, Any]
```

**Returns:** Dictionary representation of the result.

**Example:**

```python
result = council.consult("Query")
data = result.to_dict()
print(data["synthesis"])
```

#### `to_markdown()`

Export to markdown format.

```python
def to_markdown(self) -> str
```

**Returns:** Formatted markdown string.

**Example:**

```python
result = council.consult("Query")
markdown = result.to_markdown()
with open("consultation.md", "w") as f:
    f.write(markdown)
```

#### `from_dict()`

Create ConsultationResult from dictionary.

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> ConsultationResult
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `Dict[str, Any]` | Dictionary representation of a consultation result. |

**Returns:** `ConsultationResult` instance.

**Example:**

```python
from council_ai import ConsultationResult

# Load from saved data
with open("consultation.json") as f:
    data = json.load(f)
result = ConsultationResult.from_dict(data)
```

---

### MemberResponse

Response from a single council member.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `persona` | `Persona` | The persona who responded. |
| `content` | `str` | The response content. |
| `timestamp` | `datetime` | When the response was generated. |
| `error` | `Optional[str]` | Error message if response failed. |
| `audio_url` | `Optional[str]` | Audio URL if TTS is enabled. |

**Methods:**

#### `to_dict()`

Export to dictionary format.

```python
def to_dict(self) -> Dict[str, Any]
```

**Returns:** Dictionary representation.

**Example:**

```python
result = council.consult("Query")
for response in result.responses:
    data = response.to_dict()
    print(f"{data['persona_name']}: {data['content']}")
```

---

## Persona Management

### Persona

Represents an AI advisor with specific traits and expertise.

#### Constructor

```python
from council_ai import Persona, PersonaCategory

persona = Persona(
    id: str,
    name: str,
    title: str,
    emoji: str = "👤",
    category: PersonaCategory = PersonaCategory.CUSTOM,
    core_question: str,
    razor: str,
    traits: List[Trait] = [],
    focus_areas: List[str] = [],
    prompt_prefix: Optional[str] = None,
    prompt_suffix: Optional[str] = None,
    system_prompt_override: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    model_params: Dict[str, Any] = {},
    weight: float = 1.0,
    enabled: bool = True,
    metadata: Dict[str, Any] = {},
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `str` | Required | Unique identifier (lowercase, underscores allowed). |
| `name` | `str` | Required | Display name (e.g., "Dieter Rams"). |
| `title` | `str` | Required | Role/title (e.g., "Design Philosopher"). |
| `emoji` | `str` | `"👤"` | Visual identifier. |
| `category` | `PersonaCategory` | `CUSTOM` | Organizational category. |
| `core_question` | `str` | Required | Fundamental question this persona asks. |
| `razor` | `str` | Required | Decision-making principle. |
| `traits` | `List[Trait]` | `[]` | Personality/expertise traits. |
| `focus_areas` | `List[str]` | `[]` | Areas of expertise. |
| `prompt_prefix` | `Optional[str]` | `None` | Prefix added to prompts. |
| `prompt_suffix` | `Optional[str]` | `None` | Suffix added to prompts. |
| `system_prompt_override` | `Optional[str]` | `None` | Complete system prompt override. |
| `model` | `Optional[str]` | `None` | Model override for this persona. |
| `provider` | `Optional[str]` | `None` | Provider override for this persona. |
| `model_params` | `Dict[str, Any]` | `{}` | Model parameter overrides. |
| `weight` | `float` | `1.0` | Influence weight (0.0-2.0). |
| `enabled` | `bool` | `True` | Whether persona is active. |
| `metadata` | `Dict[str, Any]` | `{}` | Custom metadata. |

**Example:**

```python
from council_ai import Persona, PersonaCategory, Trait

persona = Persona(
    id="my_expert",
    name="Security Expert",
    title="Cybersecurity Specialist",
    emoji="🔒",
    category=PersonaCategory.RED_TEAM,
    core_question="How could this be exploited?",
    razor="Security first, convenience second.",
    traits=[
        Trait(name="Paranoia", description="Assumes worst case", weight=1.5),
        Trait(name="Detail-Oriented", description="Catches edge cases", weight=1.3),
    ],
    focus_areas=["Authentication", "Encryption", "Attack Vectors"],
    weight=1.2,
)
```

#### Class Methods

##### `from_dict()`

Create Persona from dictionary.

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> Persona
```

**Example:**

```python
data = {
    "id": "expert",
    "name": "Expert",
    "title": "Specialist",
    "core_question": "What matters?",
    "razor": "Focus on essentials.",
}
persona = Persona.from_dict(data)
```

##### `from_yaml()`

Create Persona from YAML string.

```python
@classmethod
def from_yaml(cls, yaml_str: str) -> Persona
```

**Example:**

```python
yaml_content = """
id: expert
name: Expert
title: Specialist
core_question: "What matters?"
razor: "Focus on essentials."
"""
persona = Persona.from_yaml(yaml_content)
```

##### `from_yaml_file()`

Load Persona from YAML file.

```python
@classmethod
def from_yaml_file(cls, path: Union[str, Path]) -> Persona
```

**Example:**

```python
from pathlib import Path

persona = Persona.from_yaml_file("personas/my_expert.yaml")
```

#### Instance Methods

##### `to_dict()`

Export to dictionary.

```python
def to_dict(self) -> Dict[str, Any]
```

**Example:**

```python
persona = get_persona("rams")
data = persona.to_dict()
```

##### `to_yaml()`

Export to YAML string.

```python
def to_yaml(self) -> str
```

**Example:**

```python
persona = get_persona("rams")
yaml_str = persona.to_yaml()
print(yaml_str)
```

##### `save_to_yaml()`

Save to YAML file.

```python
def save_to_yaml(self, path: Union[str, Path]) -> None
```

**Example:**

```python
persona = get_persona("rams")
persona.save_to_yaml("my_personas/rams_modified.yaml")
```

##### `add_trait()`

Add a new trait to the persona.

```python
def add_trait(self, name: str, description: str, weight: float = 1.0) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | Required | Trait name. |
| `description` | `str` | Required | Trait description. |
| `weight` | `float` | `1.0` | Trait weight/importance. |

**Example:**

```python
persona = get_persona("rams")
persona.add_trait(
    name="Sustainability Focus",
    description="Considers environmental impact",
    weight=1.2
)
```

##### `remove_trait()`

Remove a trait by name.

```python
def remove_trait(self, trait_name: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `trait_name` | `str` | Name of trait to remove (case-insensitive). |

**Example:**

```python
persona = get_persona("rams")
persona.remove_trait("Minimalism")
```

##### `update_trait()`

Update an existing trait.

```python
def update_trait(
    self,
    trait_name: str,
    weight: Optional[float] = None,
    description: Optional[str] = None
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `trait_name` | `str` | Required | Name of trait to update. |
| `weight` | `Optional[float]` | `None` | New weight value. |
| `description` | `Optional[str]` | `None` | New description. |

**Example:**

```python
persona = get_persona("rams")
persona.update_trait("Simplification Obsession", weight=1.8)
```

##### `clone()`

Create a modified copy of the persona.

```python
def clone(self, new_id: Optional[str] = None, **overrides) -> Persona
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `new_id` | `Optional[str]` | `None` | ID for the cloned persona. |
| `**overrides` | | | Field values to override in the clone. |

**Returns:** New `Persona` instance.

**Example:**

```python
rams = get_persona("rams")

# Create variant with higher weight
rams_heavy = rams.clone(new_id="rams_heavy", weight=1.5)

# Create variant for specific domain
rams_mobile = rams.clone(
    new_id="rams_mobile",
    focus_areas=["Mobile UX", "Touch Interfaces", "Responsive Design"]
)
```

##### `get_system_prompt()`

Generate the system prompt for this persona.

```python
def get_system_prompt(self) -> str
```

**Returns:** System prompt string with traits and focus areas.

**Example:**

```python
persona = get_persona("rams")
prompt = persona.get_system_prompt()
```

##### `format_response_prompt()`

Format the user query with context.

```python
def format_response_prompt(
    self,
    query: str,
    context: Optional[str] = None
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | User query. |
| `context` | `Optional[str]` | `None` | Additional context. |

**Returns:** Formatted prompt string.

---

### PersonaCategory

Enum for categorizing personas.

```python
from council_ai import PersonaCategory
```

**Values:**

| Category | Description |
|----------|-------------|
| `ADVISORY` | Advisory council members (build it right). |
| `RED_TEAM` | Red team members (break & survive). |
| `SPECIALIST` | Domain specialists. |
| `CUSTOM` | User-created personas. |

**Example:**

```python
from council_ai import Persona, PersonaCategory

persona = Persona(
    id="security_expert",
    name="Security Expert",
    category=PersonaCategory.RED_TEAM,
    # ... other fields
)
```

---

### Trait

Represents a personality or expertise trait.

```python
from council_ai import Trait

trait = Trait(
    name: str,
    description: str,
    weight: float = 1.0,
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | Required | Trait name. |
| `description` | `str` | Required | Trait description. |
| `weight` | `float` | `1.0` | Trait weight/importance (0.0-2.0). |

**Example:**

```python
from council_ai import Trait

traits = [
    Trait(
        name="Analytical Thinking",
        description="Breaks down complex problems",
        weight=1.5
    ),
    Trait(
        name="Risk Awareness",
        description="Identifies potential dangers",
        weight=1.3
    ),
]
```

---

### PersonaManager

Manages the collection of available personas.

**Note:** Most users don't need to interact with PersonaManager directly. Use the utility functions `get_persona()` and `list_personas()` instead.

#### Methods

##### `get()`

Get a persona by ID.

```python
def get(self, persona_id: str) -> Optional[Persona]
```

##### `get_or_raise()`

Get a persona by ID or raise exception.

```python
def get_or_raise(self, persona_id: str) -> Persona
```

##### `list()`

List all personas, optionally filtered by category.

```python
def list(self, category: Optional[PersonaCategory] = None) -> List[Persona]
```

##### `add()`

Add a custom persona.

```python
def add(self, persona: Persona, overwrite: bool = False) -> None
```

##### `remove()`

Remove a persona.

```python
def remove(self, persona_id: str) -> None
```

##### `save_persona()`

Save a persona to YAML file.

```python
def save_persona(
    self,
    persona_id: str,
    path: Optional[Union[str, Path]] = None
) -> Path
```

##### `reload()`

Reload all personas from disk.

```python
def reload(self) -> None
```

---

## Domain System

### Domain

A domain configuration with recommended personas and settings.

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Unique domain identifier. |
| `name` | `str` | Display name. |
| `description` | `str` | Domain description. |
| `category` | `DomainCategory` | Organizational category. |
| `default_personas` | `List[str]` | Personas to include by default. |
| `optional_personas` | `List[str]` | Optional personas that can be added. |
| `recommended_mode` | `str` | Recommended consultation mode. |
| `example_queries` | `List[str]` | Example queries for this domain. |

**Example:**

```python
from council_ai import get_domain

domain = get_domain("coding")
print(f"Domain: {domain.name}")
print(f"Description: {domain.description}")
print(f"Default personas: {', '.join(domain.default_personas)}")
print(f"\nExample queries:")
for query in domain.example_queries:
    print(f"  - {query}")
```

---

### DomainCategory

Enum for categorizing domains.

```python
from council_ai import DomainCategory
```

**Values:**

| Category | Description |
|----------|-------------|
| `TECHNICAL` | Technical/engineering domains. |
| `BUSINESS` | Business strategy domains. |
| `CREATIVE` | Creative/artistic domains. |
| `PERSONAL` | Personal development domains. |
| `GENERAL` | General-purpose domains. |

---

## Provider System

### LLMProvider

Abstract base class for LLM providers.

**Note:** Most users don't need to interact with LLMProvider directly. Providers are automatically instantiated based on the `provider` parameter in Council.

#### Supported Providers

| Provider | Value | Models |
|----------|-------|--------|
| Anthropic Claude | `"anthropic"` | `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307` |
| OpenAI GPT | `"openai"` | `gpt-4-turbo-preview`, `gpt-4`, `gpt-3.5-turbo` |
| Google Gemini | `"gemini"` | `gemini-pro`, `gemini-pro-vision` |
| Custom HTTP | `"http"` | Custom endpoint |

#### Methods

##### `complete()`

Generate a completion (async).

```python
async def complete(
    self,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> str
```

##### `stream_complete()`

Stream a completion (async).

```python
async def stream_complete(
    self,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> AsyncIterator[str]
```

##### `close()`

Close and cleanup provider resources.

```python
def close(self) -> None
```

---

## Utility Functions

### Persona Utilities

#### `get_persona()`

Get a built-in persona by ID.

```python
from council_ai import get_persona

persona = get_persona(persona_id: str) -> Persona
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `persona_id` | `str` | ID of the persona to retrieve. |

**Returns:** `Persona` instance.

**Raises:** `ValueError` if persona not found.

**Example:**

```python
from council_ai import get_persona

# Get a persona (raises ValueError if not found)
rams = get_persona("rams")
print(f"{rams.emoji} {rams.name}: {rams.title}")
```

#### `list_personas()`

List all available personas.

```python
from council_ai import list_personas

personas = list_personas(category: Optional[PersonaCategory] = None) -> List[Persona]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | `Optional[PersonaCategory]` | `None` | Filter by category. |

**Returns:** List of `Persona` instances.

**Example:**

```python
from council_ai import list_personas, PersonaCategory

# List all personas
all_personas = list_personas()
for p in all_personas:
    print(f"{p.emoji} {p.name} - {p.category.value}")

# List only red team members
red_team = list_personas(category=PersonaCategory.RED_TEAM)
```

### Domain Utilities

#### `get_domain()`

Get a domain configuration by ID.

```python
from council_ai import get_domain

domain = get_domain(domain_id: str) -> Domain
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `domain_id` | `str` | ID of the domain to retrieve. |

**Returns:** `Domain` instance.

**Raises:** `ValueError` if domain not found.

**Example:**

```python
from council_ai import get_domain

coding = get_domain("coding")
print(f"Domain: {coding.name}")
print(f"Default personas: {coding.default_personas}")
```

#### `list_domains()`

List all available domains.

```python
from council_ai import list_domains

domains = list_domains(category: Optional[DomainCategory] = None) -> List[Domain]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | `Optional[DomainCategory]` | `None` | Filter by category. |

**Returns:** List of `Domain` instances.

**Example:**

```python
from council_ai import list_domains, DomainCategory

# List all domains
all_domains = list_domains()
for d in all_domains:
    print(f"{d.id}: {d.name}")

# List only business domains
business_domains = list_domains(category=DomainCategory.BUSINESS)
```

### Provider Utilities

#### `get_provider()`

Get a provider instance by name.

```python
from council_ai import get_provider

provider = get_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> LLMProvider
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider_name` | `str` | Required | Provider name (`"anthropic"`, `"openai"`, etc.). |
| `api_key` | `Optional[str]` | `None` | API key for the provider. |
| `model` | `Optional[str]` | `None` | Model name override. |
| `base_url` | `Optional[str]` | `None` | Base URL override. |

**Returns:** Provider instance.

**Example:**

```python
from council_ai import get_provider

# Get Anthropic provider
provider = get_provider("anthropic", api_key="your-key")

# Get OpenAI provider with custom model
provider = get_provider("openai", api_key="your-key", model="gpt-4")
```

#### `list_providers()`

List all available provider names.

```python
from council_ai import list_providers

providers = list_providers() -> List[str]
```

**Returns:** List of provider names.

**Example:**

```python
from council_ai import list_providers

providers = list_providers()
print(f"Available providers: {', '.join(providers)}")
```

---

## Complete Examples

### Basic Consultation

```python
from council_ai import Council

# Create a council for business strategy
council = Council.for_domain("business", api_key="your-key")

# Consult the council
result = council.consult("Should we enter the European market?")

# Print synthesis
print("Synthesis:")
print(result.synthesis)
print()

# Print individual responses
print("Individual Responses:")
for response in result.responses:
    print(f"\n{response.persona.emoji} {response.persona.name}:")
    print(response.content)
```

### Custom Council

```python
from council_ai import Council, Persona, Trait, PersonaCategory

# Create a custom persona
security_expert = Persona(
    id="security_guru",
    name="Security Guru",
    title="Cybersecurity Expert",
    emoji="🔐",
    category=PersonaCategory.RED_TEAM,
    core_question="Where are the vulnerabilities?",
    razor="Paranoia keeps systems safe.",
    traits=[
        Trait("Threat Modeling", "Identifies attack vectors", 1.5),
        Trait("Defense in Depth", "Multiple security layers", 1.3),
    ],
    focus_areas=["Authentication", "Encryption", "Access Control"],
)

# Create council with custom persona
council = Council(api_key="your-key")
council.add_member("rams")  # Design perspective
council.add_member("holman")  # Hacker perspective
council.add_member(security_expert)  # Custom security expert

# Consult
result = council.consult("Review our authentication system")
```

### Async Consultation with Streaming

```python
import asyncio
from council_ai import Council, ConsultationMode

async def main():
    council = Council.for_domain("coding", api_key="your-key")
    
    print("Starting consultation...")
    
    async for event in council.consult_stream(
        query="Review this API design: POST /users with {email, password}",
        mode=ConsultationMode.SEQUENTIAL
    ):
        if event["event"] == "progress":
            print(f"Progress: {event['data']['message']}")
        
        elif event["event"] == "response":
            persona = event["data"]["persona"]
            content = event["data"]["content"]
            print(f"\n{persona['emoji']} {persona['name']}:")
            print(content)
        
        elif event["event"] == "synthesis":
            print("\n--- Synthesis ---")
            print(event["data"]["synthesis"])
        
        elif event["event"] == "complete":
            print("\nConsultation complete!")

asyncio.run(main())
```

### Domain Exploration

```python
from council_ai import list_domains, get_domain, Council

# List all available domains
print("Available Domains:")
for domain in list_domains():
    print(f"\n{domain.id}: {domain.name}")
    print(f"  {domain.description}")
    print(f"  Default personas: {', '.join(domain.default_personas)}")

# Get specific domain details
coding = get_domain("coding")
print(f"\n\nDomain: {coding.name}")
print(f"Example queries:")
for query in coding.example_queries:
    print(f"  - {query}")

# Use the domain
council = Council.for_domain("coding", api_key="your-key")
result = council.consult(coding.example_queries[0])
```

### Persona Management

```python
from council_ai import get_persona, list_personas, PersonaCategory

# List all personas
print("All Available Personas:")
for persona in list_personas():
    print(f"{persona.emoji} {persona.name} - {persona.title}")

# Get specific persona
rams = get_persona("rams")
print(f"\n\nPersona: {rams.name}")
print(f"Core Question: {rams.core_question}")
print(f"Decision Razor: {rams.razor}")

# Clone and modify
rams_focused = rams.clone(
    new_id="rams_focused",
    weight=1.5,
    focus_areas=["Mobile Design", "Accessibility"]
)

# Use modified persona
from council_ai import Council
council = Council(api_key="your-key")
council.add_member(rams_focused)
```

### Configuration Management

```python
from council_ai import Council, CouncilConfig, ConsultationMode

# Create custom configuration
config = CouncilConfig(
    name="Code Review Council",
    description="Focused on code quality and security",
    mode=ConsultationMode.SEQUENTIAL,
    temperature=0.5,  # More focused, less creative
    max_tokens_per_response=1500,
    include_confidence=True,
    context_window=20,  # Remember more history
)

# Create council with config
council = Council.for_domain("coding", api_key="your-key", config=config)

# Adjust member weights
council.set_member_weight("holman", 1.5)  # Emphasize security
council.set_member_weight("kahneman", 1.2)  # Emphasize UX

# Consult
result = council.consult("Should we use microservices or monolith?")
```

---

## Best Practices

### API Key Management

```python
# ❌ Don't hardcode API keys
council = Council(api_key="sk-ant-...")

# ✅ Use environment variables
import os
council = Council(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ✅ Or use .env file (auto-loaded)
council = Council()  # Reads from .env automatically
```

### Error Handling

```python
from council_ai import Council

council = Council.for_domain("business", api_key="your-key")

try:
    result = council.consult("Should we pivot?")
    
    # Check for member failures
    for response in result.responses:
        if response.error:
            print(f"Error from {response.persona.name}: {response.error}")
    
    # Use synthesis if available
    if result.synthesis:
        print(result.synthesis)
    else:
        print("No synthesis available")
        
except Exception as e:
    print(f"Consultation failed: {e}")
```

### Resource Cleanup

```python
import asyncio
from council_ai import Council

async def main():
    council = Council.for_domain("business", api_key="your-key")
    
    try:
        result = await council.consult_async("Query")
        print(result.synthesis)
    finally:
        # Clean up provider resources
        if hasattr(council, '_provider') and council._provider:
            council._provider.close()

asyncio.run(main())
```

### Performance Tips

```python
from council_ai import Council, ConsultationMode

council = Council.for_domain("coding", api_key="your-key")

# For quick consultations, use INDIVIDUAL mode (parallel)
result = council.consult("Quick question", mode=ConsultationMode.INDIVIDUAL)

# For specific members only
result = council.consult("Security review", members=["holman", "taleb"])

# Disable members you don't need
council.disable_member("treasure")  # Not needed for this domain
```

---

## Additional Resources

- [Main Documentation](../README.md)
- [Examples Directory](../examples/)
- [Contributing Guide](../CONTRIBUTING.md)
- [Agent Knowledge Base](../AGENT_KNOWLEDGE_BASE.md)

---

## Version

API Reference for Council AI v1.0.0
