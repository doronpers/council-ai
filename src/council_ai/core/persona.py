"""
Persona - Council Member Definition and Management

Personas define the character, expertise, and behavior of council members.
They can be loaded from YAML files, created programmatically, or customized
at runtime.
"""

from __future__ import annotations

import os
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml  # type: ignore
from pydantic import BaseModel, Field, field_validator


class PersonaCategory(str, Enum):
    """Categories for organizing personas."""

    ADVISORY = "advisory"  # Build it right
    ADVERSARIAL = "adversarial"  # Break it / survive
    CREATIVE = "creative"  # Generate ideas
    ANALYTICAL = "analytical"  # Deep analysis
    STRATEGIC = "strategic"  # Long-term thinking
    OPERATIONAL = "operational"  # Day-to-day execution
    RED_TEAM = "red_team"  # Think like an attacker/fraudster
    CUSTOM = "custom"  # User-defined


class Trait(BaseModel):
    """A single trait or characteristic of a persona."""

    name: str
    description: str
    weight: float = Field(default=1.0, ge=0.0, le=2.0)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.name}: {self.description}"


class Persona(BaseModel):
    """
    A council member persona with customizable characteristics.

    Attributes:
        id: Unique identifier (lowercase, no spaces)
        name: Display name
        title: Role or title description
        emoji: Visual identifier
        category: Organizational category
        core_question: The fundamental question this persona asks
        razor: Their decision-making principle
        traits: List of personality/expertise traits
        focus_areas: Areas of expertise or concern
        prompt_prefix: Custom prefix for LLM prompts
        prompt_suffix: Custom suffix for LLM prompts
        model: Optional model override for this persona
        model_params: Model parameter overrides (temperature, max_tokens)
        weight: Influence weight in council decisions (0.0-2.0)
        enabled: Whether this persona is active
        metadata: Additional custom data
    """

    id: str
    name: str
    title: str
    emoji: str = "👤"
    category: PersonaCategory = PersonaCategory.CUSTOM

    core_question: str = Field(..., description="The fundamental question this persona asks")
    razor: str = Field(..., description="Their decision-making principle or 'razor'")

    traits: List[Trait] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)

    prompt_prefix: Optional[str] = None
    prompt_suffix: Optional[str] = None
    system_prompt_override: Optional[str] = None

    model: Optional[str] = None
    provider: Optional[str] = None
    model_params: Dict[str, Any] = Field(default_factory=dict)

    weight: float = Field(default=1.0, ge=0.0, le=2.0)
    enabled: bool = True

    # Reasoning and web search capabilities
    reasoning_mode: Optional[str] = None  # "chain_of_thought", "tree_of_thought", etc.
    enable_web_search: bool = False  # Allow this persona to use web search

    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Normalize ID to lowercase with underscores."""
        normalized = v.lower().replace(" ", "_").replace("-", "_")
        # Ensure it starts with a letter and only contains valid characters
        if not re.match(r"^[a-z][a-z0-9_]*$", normalized):
            raise ValueError(
                "ID must start with a letter and contain "
                f"only lowercase letters, numbers, and underscores: {v}"
            )
        return normalized

    def get_system_prompt(self) -> str:
        """Generate the system prompt for this persona."""
        if self.system_prompt_override:
            return self.system_prompt_override

        traits_text = "\n".join(f"- {t}" for t in self.traits) if self.traits else ""
        focus_text = ", ".join(self.focus_areas) if self.focus_areas else ""

        prompt = f"""You are {self.name}, {self.title}.

{self.emoji} Your Core Question: "{self.core_question}"

Your Razor (Decision Principle): "{self.razor}"

{f"Your Key Traits:{chr(10)}{traits_text}" if traits_text else ""}

{f"Your Focus Areas: {focus_text}" if focus_text else ""}

When responding:
1. Stay in character as {self.name}
2. Apply your core question to the situation
3. Use your razor to guide recommendations
4. Draw on your specific expertise and perspective
5. Be direct, insightful, and actionable
6. Provide specific recommendations with clear reasoning

{self.prompt_prefix or ""}"""

        return prompt.strip()

    def format_response_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Format a user query for this persona."""
        parts = []

        if context:
            parts.append(f"Context:\n{context}\n")

        parts.append(f"Query:\n{query}")

        if self.prompt_suffix:
            parts.append(f"\n{self.prompt_suffix}")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Export persona to dictionary."""
        return self.model_dump()

    def to_yaml(self) -> str:
        """Export persona to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Persona":
        """Create persona from dictionary."""
        # Convert traits if they're simple dicts
        if "traits" in data and data["traits"]:
            data["traits"] = [Trait(**t) if isinstance(t, dict) else t for t in data["traits"]]
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Persona":
        """Create persona from YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_yaml_file(cls, path: Union[str, Path]) -> "Persona":
        """Load persona from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_yaml(f.read())

    def save_to_yaml(self, path: Union[str, Path]) -> None:
        """Save persona to YAML file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

    def update_trait(
        self, trait_name: str, weight: Optional[float] = None, description: Optional[str] = None
    ) -> None:
        """Update an existing trait."""
        for trait in self.traits:
            if trait.name.lower() == trait_name.lower():
                if weight is not None:
                    trait.weight = weight
                if description is not None:
                    trait.description = description
                return
        raise ValueError(f"Trait '{trait_name}' not found")

    def add_trait(self, name: str, description: str, weight: float = 1.0) -> None:
        """Add a new trait."""
        self.traits.append(Trait(name=name, description=description, weight=weight))

    def remove_trait(self, trait_name: str) -> None:
        """Remove a trait by name."""
        self.traits = [t for t in self.traits if t.name.lower() != trait_name.lower()]

    def clone(self, new_id: Optional[str] = None, **overrides) -> "Persona":
        """Create a copy of this persona with optional modifications."""
        data = self.to_dict()
        data.update(overrides)
        if new_id:
            data["id"] = new_id
        return Persona.from_dict(data)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.emoji} {self.name} ({self.title})"

    def __repr__(self) -> str:
        """Return debug representation."""
        return f"Persona(id='{self.id}', name='{self.name}')"


class PersonaManager:
    """
    Manages persona loading, storage, and retrieval.

    Personas can be loaded from:
    - Built-in package personas
    - Custom YAML files
    - User's config directory
    - Programmatically created
    """

    def __init__(self, custom_paths: Optional[List[Union[str, Path]]] = None):
        self._personas: Dict[str, Persona] = {}
        self._custom_paths = [Path(p) for p in (custom_paths or [])]
        self._load_builtin_personas()
        self._load_custom_personas()

    def _get_builtin_path(self) -> Path:
        """Get path to built-in personas."""
        return Path(__file__).parent.parent / "personas"

    def _get_user_path(self) -> Path:
        """Get path to user's custom personas."""
        config_dir = Path(
            os.environ.get("COUNCIL_CONFIG_DIR", Path.home() / ".config" / "council-ai")
        )
        return config_dir / "personas"

    def _get_personal_path(self) -> Optional[Path]:
        """Get path to personal personas from council-ai-personal if available."""
        try:
            from .personal_integration import detect_personal_repo

            repo_path = detect_personal_repo()
            if repo_path:
                personal_personas = repo_path / "personal" / "personas"
                if personal_personas.exists():
                    return personal_personas
        except Exception:
            pass
        return None

    def _load_builtin_personas(self) -> None:
        """Load all built-in personas."""
        builtin_path = self._get_builtin_path()
        if builtin_path.exists():
            for yaml_file in builtin_path.glob("*.yaml"):
                try:
                    persona = Persona.from_yaml_file(yaml_file)
                    self._personas[persona.id] = persona
                except Exception as e:
                    import sys

                    print(f"Warning: Failed to load {yaml_file}: {e}", file=sys.stderr)

    def _load_custom_personas(self) -> None:
        """Load personas from custom paths, personal repo, and user directory."""
        paths = list(self._custom_paths)

        # Add personal personas path (loaded before user path for priority)
        personal_path = self._get_personal_path()
        if personal_path:
            paths.append(personal_path)

        # Add user path (highest priority, loaded last)
        paths.append(self._get_user_path())

        for path in paths:
            if path and path.exists():
                for yaml_file in path.glob("*.yaml"):
                    try:
                        persona = Persona.from_yaml_file(yaml_file)
                        # Only overwrite if not already loaded (user configs take priority)
                        if persona.id not in self._personas:
                            self._personas[persona.id] = persona
                    except Exception as e:
                        import sys

                        print(f"Warning: Failed to load {yaml_file}: {e}", file=sys.stderr)

    def get(self, persona_id: str) -> Optional[Persona]:
        """Get a persona by ID."""
        return self._personas.get(persona_id.lower())

    def get_or_raise(self, persona_id: str) -> Persona:
        """Get a persona by ID, raising if not found."""
        persona = self.get(persona_id)
        if persona is None:
            available = ", ".join(self._personas.keys())
            raise ValueError(f"Persona '{persona_id}' not found. Available: {available}")
        return persona

    def list(self, category: Optional[PersonaCategory] = None) -> List[Persona]:
        """List all personas, optionally filtered by category."""
        personas = list(self._personas.values())
        if category:
            personas = [p for p in personas if p.category == category]
        return sorted(personas, key=lambda p: (p.category.value, p.name))

    def list_ids(self) -> List[str]:
        """List all persona IDs."""
        return sorted(self._personas.keys())

    def add(self, persona: Persona, overwrite: bool = False) -> None:
        """Add a persona to the manager."""
        if persona.id in self._personas and not overwrite:
            raise ValueError(
                f"Persona '{persona.id}' already exists. Use overwrite=True to replace."
            )
        self._personas[persona.id] = persona

    def remove(self, persona_id: str) -> None:
        """Remove a persona."""
        if persona_id in self._personas:
            del self._personas[persona_id]

    def save_persona(self, persona_id: str, path: Optional[Union[str, Path]] = None) -> Path:
        """Save a persona to file."""
        persona = self.get_or_raise(persona_id)

        if path is None:
            user_path = self._get_user_path()
            user_path.mkdir(parents=True, exist_ok=True)
            path = user_path / f"{persona_id}.yaml"

        path = Path(path)
        persona.save_to_yaml(path)
        return path

    def reload(self) -> None:
        """Reload all personas from disk."""
        self._personas.clear()
        self._load_builtin_personas()
        self._load_custom_personas()

    def create_persona(
        self,
        id: str,
        name: str,
        title: str,
        core_question: str,
        razor: str,
        emoji: str = "👤",
        category: PersonaCategory = PersonaCategory.CUSTOM,
        traits: Optional[List[Dict[str, Any]]] = None,
        focus_areas: Optional[List[str]] = None,
        save: bool = False,
        **kwargs,
    ) -> Persona:
        """Create a new persona and optionally save it."""
        trait_objects = [Trait(**t) for t in (traits or [])]

        persona = Persona(
            id=id,
            name=name,
            title=title,
            core_question=core_question,
            razor=razor,
            emoji=emoji,
            category=category,
            traits=trait_objects,
            focus_areas=focus_areas or [],
            **kwargs,
        )

        self.add(persona)

        if save:
            self.save_persona(id)

        return persona


# Global persona manager instance
_default_manager: Optional[PersonaManager] = None


def get_persona_manager() -> PersonaManager:
    """Get the global persona manager instance."""
    global _default_manager
    if _default_manager is None:
        from .config import load_config

        config = load_config()
        custom_personas_path = config.custom_personas_path
        custom_paths: Optional[List[Union[str, Path]]] = (
            [custom_personas_path] if custom_personas_path else None
        )
        _default_manager = PersonaManager(custom_paths=custom_paths)
    return _default_manager


def get_persona(persona_id: str) -> Persona:
    """Get a persona by ID from the global manager."""
    return get_persona_manager().get_or_raise(persona_id)


def list_personas(category: Optional[PersonaCategory] = None) -> List[Persona]:
    """List all available personas."""
    return get_persona_manager().list(category)
