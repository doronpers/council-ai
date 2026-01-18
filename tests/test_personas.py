"""Tests for persona management."""

import pytest

from council_ai import Persona, PersonaCategory, Trait, get_persona, list_personas
from council_ai.core.persona import PersonaManager


def test_all_builtin_personas_load():
    """Test that all 9 built-in personas load correctly."""
    personas = list_personas()
    assert len(personas) == 9, f"Expected 9 personas, got {len(personas)}"

    # Check each persona has required fields
    for persona in personas:
        assert persona.id
        assert persona.name
        assert persona.title
        assert persona.emoji
        assert persona.core_question
        assert persona.razor
        assert isinstance(persona.category, PersonaCategory)


def test_specific_personas():
    """Test specific personas load with correct data."""
    # Test Dieter Rams
    rams = get_persona("rams")
    assert rams.name == "Dieter Rams"
    assert rams.emoji == "🎨"
    assert rams.category == PersonaCategory.ADVISORY
    assert "simple" in rams.core_question.lower()
    assert len(rams.traits) > 0
    assert len(rams.focus_areas) > 0

    # Test Andy Grove
    grove = get_persona("grove")
    assert grove.name == "Andy Grove"
    assert grove.emoji == "🎯"
    assert grove.category == PersonaCategory.STRATEGIC

    # Test Nassim Taleb
    taleb = get_persona("taleb")
    assert taleb.name == "Nassim Nicholas Taleb"
    assert taleb.emoji == "🦢"
    assert taleb.category == PersonaCategory.ADVERSARIAL


def test_persona_system_prompt_generation():
    """Test that system prompts are generated correctly."""
    rams = get_persona("rams")
    prompt = rams.get_system_prompt()

    # Check prompt contains key elements
    assert rams.name in prompt
    assert rams.core_question in prompt
    assert rams.razor in prompt
    assert len(prompt) > 100  # Should be substantial


def test_persona_response_prompt_formatting():
    """Test response prompt formatting."""
    rams = get_persona("rams")

    query = "Should we redesign this UI?"
    context = "Current UI has 20 screens"

    prompt = rams.format_response_prompt(query, context)
    assert query in prompt
    assert context in prompt


def test_persona_categories():
    """Test that personas are categorized correctly."""
    personas = list_personas()

    advisory = [p for p in personas if p.category == PersonaCategory.ADVISORY]
    adversarial = [p for p in personas if p.category == PersonaCategory.ADVERSARIAL]

    assert len(advisory) >= 3  # rams, kahneman, dempsey
    assert len(adversarial) >= 2  # holman, taleb


def test_persona_traits():
    """Test persona traits structure."""
    rams = get_persona("rams")

    assert len(rams.traits) > 0
    for trait in rams.traits:
        assert isinstance(trait, Trait)
        assert trait.name
        assert trait.description
        assert 0.0 <= trait.weight <= 2.0


def test_persona_yaml_export():
    """Test exporting persona to YAML."""
    rams = get_persona("rams")
    yaml_str = rams.to_yaml()

    assert "id: rams" in yaml_str
    assert rams.name in yaml_str
    assert rams.core_question in yaml_str


def test_persona_dict_export():
    """Test exporting persona to dict."""
    rams = get_persona("rams")
    data = rams.to_dict()

    assert data["id"] == "rams"
    assert data["name"] == rams.name
    assert data["emoji"] == rams.emoji
    assert "traits" in data
    assert "focus_areas" in data


def test_persona_cloning():
    """Test cloning personas with modifications."""
    original = get_persona("rams")

    clone = original.clone(new_id="rams_v2", weight=1.5)

    assert clone.id == "rams_v2"
    assert clone.name == original.name
    assert clone.weight == 1.5
    assert clone.id != original.id


def test_persona_trait_operations():
    """Test adding, updating, and removing traits."""
    persona = Persona(
        id="test",
        name="Test",
        title="Test",
        core_question="?",
        razor=".",
    )

    # Add trait
    persona.add_trait("Quality", "High quality", weight=1.3)
    assert len(persona.traits) == 1
    assert persona.traits[0].name == "Quality"
    assert persona.traits[0].weight == 1.3

    # Update trait
    persona.update_trait("Quality", weight=1.7)
    assert persona.traits[0].weight == 1.7

    # Update description
    persona.update_trait("Quality", description="Very high quality")
    assert persona.traits[0].description == "Very high quality"

    # Remove trait
    persona.remove_trait("Quality")
    assert len(persona.traits) == 0


def test_persona_manager():
    """Test PersonaManager functionality."""
    manager = PersonaManager()

    # Should have loaded built-in personas
    assert len(manager.list()) >= 7
    assert len(manager.list_ids()) >= 7

    # Test getting personas
    rams = manager.get("rams")
    assert rams is not None
    assert rams.id == "rams"

    # Test get_or_raise
    rams2 = manager.get_or_raise("rams")
    assert rams2.id == "rams"

    with pytest.raises(ValueError):
        manager.get_or_raise("nonexistent")


def test_persona_loading_user_overrides_personal(monkeypatch, tmp_path):
    """Test that user personas override personal personas when IDs collide."""
    personal_personas_dir = tmp_path / "personal_personas"
    personal_personas_dir.mkdir(parents=True)

    config_dir = tmp_path / ".config" / "council-ai"
    user_personas_dir = config_dir / "personas"
    user_personas_dir.mkdir(parents=True)

    # Same persona ID exists in both places.
    (personal_personas_dir / "override.yaml").write_text(
        "\n".join(
            [
                "id: override",
                "name: Personal Version",
                "title: Personal",
                "core_question: Personal?",
                "razor: Personal razor.",
            ]
        ),
        encoding="utf-8",
    )
    (user_personas_dir / "override.yaml").write_text(
        "\n".join(
            [
                "id: override",
                "name: User Version",
                "title: User",
                "core_question: User?",
                "razor: User razor.",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("COUNCIL_CONFIG_DIR", str(config_dir))
    monkeypatch.setattr(PersonaManager, "_get_personal_path", lambda self: personal_personas_dir)

    manager = PersonaManager()
    persona = manager.get("override")
    assert persona is not None
    assert persona.name == "User Version"


def test_persona_manager_add_custom():
    """Test adding custom personas to manager."""
    manager = PersonaManager()

    custom = Persona(
        id="custom_test",
        name="Custom",
        title="Custom Expert",
        core_question="Is it custom?",
        razor="Custom is best.",
    )

    manager.add(custom)
    retrieved = manager.get("custom_test")
    assert retrieved.id == "custom_test"

    # Test overwrite protection
    with pytest.raises(ValueError):
        manager.add(custom, overwrite=False)

    # Test overwrite allowed
    manager.add(custom, overwrite=True)  # Should not raise


def test_persona_validation():
    """Test persona field validation."""
    # Valid persona
    persona = Persona(
        id="valid_id",
        name="Valid Name",
        title="Valid Title",
        core_question="Valid question?",
        razor="Valid razor.",
    )
    assert persona.id == "valid_id"

    # ID normalization
    persona2 = Persona(
        id="Valid ID With-Spaces",
        name="Test",
        title="Test",
        core_question="?",
        razor=".",
    )
    assert persona2.id == "valid_id_with_spaces"


def test_list_personas_by_category():
    """Test filtering personas by category."""
    advisory = list_personas(PersonaCategory.ADVISORY)
    adversarial = list_personas(PersonaCategory.ADVERSARIAL)

    assert len(advisory) > 0
    assert len(adversarial) > 0

    for p in advisory:
        assert p.category == PersonaCategory.ADVISORY

    for p in adversarial:
        assert p.category == PersonaCategory.ADVERSARIAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
