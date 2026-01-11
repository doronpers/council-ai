"""
Tests for Council AI core functionality.
"""

import pytest
from council_ai import Council, Persona, PersonaCategory, Trait
from council_ai.core.session import MemberResponse
from datetime import datetime


def test_persona_creation():
    """Test creating a custom persona."""
    persona = Persona(
        id="test_persona",
        name="Test Advisor",
        title="Test Expert",
        emoji="🧪",
        category=PersonaCategory.CUSTOM,
        core_question="Is this tested?",
        razor="Test everything twice.",
        traits=[
            Trait(name="Testing", description="Tests thoroughly", weight=1.5)
        ],
        focus_areas=["Testing", "Quality"]
    )
    
    assert persona.id == "test_persona"
    assert persona.name == "Test Advisor"
    assert persona.emoji == "🧪"
    assert len(persona.traits) == 1
    assert persona.traits[0].name == "Testing"


def test_persona_system_prompt():
    """Test persona system prompt generation."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="Is this right?",
        razor="Do it right.",
    )
    
    prompt = persona.get_system_prompt()
    assert "Test" in prompt
    assert "Is this right?" in prompt
    assert "Do it right." in prompt


def test_council_creation():
    """Test creating a council."""
    council = Council(api_key="test-key", provider="anthropic")
    assert len(council.list_members()) == 0
    
    # Add a persona
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )
    council.add_member(persona)
    assert len(council.list_members()) == 1


def test_council_for_domain():
    """Test creating a council from a domain."""
    council = Council.for_domain("business", api_key="test-key")
    
    # Should have business-related personas
    members = council.list_members()
    assert len(members) > 0
    
    member_ids = [m.id for m in members]
    # Business domain includes grove, taleb, etc
    assert any(mid in ["grove", "taleb", "kahneman", "dempsey"] for mid in member_ids)


def test_member_response():
    """Test member response creation."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )
    
    response = MemberResponse(
        persona=persona,
        content="This is my advice",
        timestamp=datetime.now()
    )
    
    assert response.persona.id == "test"
    assert response.content == "This is my advice"
    assert response.error is None


def test_persona_weight():
    """Test persona weight modification."""
    council = Council(api_key="test-key")
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
        weight=1.0
    )
    
    council.add_member(persona)
    council.set_member_weight("test", 1.5)
    
    member = council.get_member("test")
    assert member.weight == 1.5


def test_member_enable_disable():
    """Test enabling/disabling members."""
    council = Council(api_key="test-key")
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )
    
    council.add_member(persona)
    assert council.get_member("test").enabled
    
    council.disable_member("test")
    assert not council.get_member("test").enabled
    
    council.enable_member("test")
    assert council.get_member("test").enabled


def test_trait_operations():
    """Test adding, updating, and removing traits."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )
    
    # Add trait
    persona.add_trait("Quality", "Focus on quality", weight=1.2)
    assert len(persona.traits) == 1
    assert persona.traits[0].name == "Quality"
    
    # Update trait
    persona.update_trait("Quality", weight=1.5)
    assert persona.traits[0].weight == 1.5
    
    # Remove trait
    persona.remove_trait("Quality")
    assert len(persona.traits) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
