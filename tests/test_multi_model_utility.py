"""
Tests for Multi-Model Utility Integration.
Ensures that personas can use different providers and models within the same council.
"""

import pytest
from unittest.mock import MagicMock, patch
from council_ai.core.persona import Persona, Trait
from council_ai.core.council import Council, CouncilConfig
from council_ai.providers import LLMProvider

class MockProvider(LLMProvider):
    async def complete(self, system_prompt, user_prompt, max_tokens=1000, temperature=0.7):
        response = MagicMock()
        response.text = f"Response from {self.provider_name} model {self.model}"
        return response

    @property
    def provider_name(self):
        return getattr(self, "_provider_name", "mock")

    def is_available(self):
        return True

@pytest.fixture
def mock_get_provider():
    with patch("council_ai.core.council.get_provider") as mock:
        def side_effect(name, **kwargs):
            provider = MockProvider(api_key=kwargs.get("api_key"), model=kwargs.get("model"))
            provider._provider_name = name
            return provider
        mock.side_effect = side_effect
        yield mock

@pytest.fixture
def mock_llm_manager(mock_get_provider):
    class MockLLMManager:
        def __init__(self, preferred_provider, api_key=None, model=None, base_url=None):
            self.preferred_provider = preferred_provider
            self.api_key = api_key
            self.model = model
            self.base_url = base_url

        def get_provider(self, name):
            return mock_get_provider.side_effect(
                name, api_key=self.api_key, model=self.model, base_url=self.base_url
            )

        async def generate(
            self,
            system_prompt,
            user_prompt,
            provider=None,
            fallback=True,
            max_tokens=1000,
            temperature=0.7,
        ):
            response = MagicMock()
            resolved_provider = provider or self.preferred_provider
            response.text = f"Response from {resolved_provider} model {self.model}"
            return response

    with patch("council_ai.core.council.LLMManager", MockLLMManager):
        yield MockLLMManager

@pytest.fixture
def mock_get_api_key():
    with patch("council_ai.core.council.get_api_key") as mock:
        mock.side_effect = lambda name: f"key-for-{name}"
        yield mock

def test_persona_provider_field():
    """Test that Persona has the provider field."""
    persona = Persona(
        id="test",
        name="Test",
        title="Tester",
        core_question="?",
        razor="!",
        provider="anthropic",
        model="claude-3"
    )
    assert persona.provider == "anthropic"
    assert persona.model == "claude-3"

def test_council_member_provider_resolution(mock_get_provider, mock_llm_manager, mock_get_api_key):
    """Test that Council correctly resolves per-persona providers."""
    council = Council(provider="openai", model="gpt-4", api_key="openai-key")
    
    # 1. Standard member (uses council defaults)
    p1 = Persona(id="p1", name="P1", title="T1", core_question="?", razor="!")
    council.add_member(p1)
    
    # 2. Member with model override only (uses council provider)
    p2 = Persona(id="p2", name="P2", title="T2", core_question="?", razor="!", model="gpt-3.5")
    council.add_member(p2)
    
    # 3. Member with provider and model override
    p3 = Persona(id="p3", name="P3", title="T3", core_question="?", razor="!", provider="anthropic", model="claude-3")
    council.add_member(p3)
    
    default_provider = council._get_provider()
    
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
    mock_get_provider, mock_llm_manager, mock_get_api_key
):
    """Test a consultation with a heterogeneous council."""
    council = Council(provider="openai", model="gpt-4", api_key="openai-key")
    
    holman = Persona(id="holman", name="Holman", title="Hacker", core_question="Break?", razor="Hack", provider="openai", model="gpt-4o")
    treasure = Persona(id="treasure", name="Treasure", title="Sound", core_question="Listen?", razor="Conscious", provider="anthropic", model="claude-3-5-sonnet")
    
    council.add_member(holman)
    council.add_member(treasure)
    
    # Set mode to individual to avoid synthesis which would require more mocks
    result = await council.consult_async("Test query", mode="individual")
    
    assert len(result.responses) == 2
    
    responses = {r.persona.id: r.content for r in result.responses}
    assert "Response from openai model gpt-4o" in responses["holman"]
    assert "Response from anthropic model claude-3-5-sonnet" in responses["treasure"]
