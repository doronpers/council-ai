"""
Tests for Multi-Model Utility Integration.
Ensures that personas can use different providers and models within the same council.
"""

from unittest.mock import patch

import pytest

from council_ai.core.council import Council
from council_ai.core.persona import Persona


@pytest.fixture
def mock_get_api_key():
    with patch("council_ai.core.council.get_api_key") as mock:
        mock.side_effect = lambda name: f"key-for-{name}"
        yield mock


@pytest.fixture
def mock_env_keys(monkeypatch):
    """Mock environment variables for API keys."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")


def test_persona_provider_field():
    """Test that Persona has the provider field."""
    persona = Persona(
        id="test",
        name="Test",
        title="Tester",
        core_question="?",
        razor="!",
        provider="anthropic",
        model="claude-3",
    )
    assert persona.provider == "anthropic"
    assert persona.model == "claude-3"


def test_council_member_provider_resolution(
    mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Test that Council correctly resolves per-persona providers."""
    # Create council with fallback disabled for cleaner test
    council = Council(provider="openai", model="gpt-4", api_key="openai-key")

    # Force the provider to be set directly (bypassing fallback logic for test clarity)
    council._provider = mock_get_provider.side_effect("openai", api_key="openai-key", model="gpt-4")

    # 1. Standard member (uses council defaults)
    p1 = Persona(id="p1", name="P1", title="T1", core_question="?", razor="!")
    council.add_member(p1)

    # 2. Member with model override only (uses council provider)
    p2 = Persona(id="p2", name="P2", title="T2", core_question="?", razor="!", model="gpt-3.5")
    council.add_member(p2)

    # 3. Member with provider and model override
    p3 = Persona(
        id="p3",
        name="P3",
        title="T3",
        core_question="?",
        razor="!",
        provider="anthropic",
        model="claude-3",
    )
    council.add_member(p3)

    default_provider = council._provider  # Use the directly set provider

    # Resolve providers
    prov1 = council._get_member_provider(p1, default_provider)
    prov2 = council._get_member_provider(p2, default_provider)
    prov3 = council._get_member_provider(p3, default_provider)

    assert prov1 == default_provider
    assert prov2.model == "gpt-3.5"
    assert prov2.provider_name == "openai"

    assert prov3.provider_name == "anthropic"
    assert prov3.model == "claude-3"
    assert prov3.api_key == "key-for-anthropic"


@pytest.mark.asyncio
async def test_heterogeneous_council_consultation(
    mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Test a consultation with a heterogeneous council."""
    council = Council(provider="openai", model="gpt-4", api_key="openai-key")
    # Clear default members to test specific personas only
    council.clear_members()

    holman = Persona(
        id="holman",
        name="Holman",
        title="Hacker",
        core_question="Break?",
        razor="Hack",
        provider="openai",
        model="gpt-4o",
    )
    treasure = Persona(
        id="treasure",
        name="Treasure",
        title="Sound",
        core_question="Listen?",
        razor="Conscious",
        provider="anthropic",
        model="claude-3-5-sonnet",
    )

    council.add_member(holman)
    council.add_member(treasure)

    # Set mode to individual to avoid synthesis which would require more mocks
    result = await council.consult_async("Test query", mode="individual")

    assert len(result.responses) == 2

    responses = {r.persona.id: r.content for r in result.responses}
    assert "Response from openai model gpt-4o" in responses["holman"]
    assert "Response from anthropic model claude-3-5-sonnet" in responses["treasure"]
