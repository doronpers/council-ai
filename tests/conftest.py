"""Test configuration for pytest."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest  # noqa: E402

from council_ai.providers import LLMProvider, LLMResponse  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


class MockProvider(LLMProvider):
    async def complete(self, system_prompt, user_prompt, max_tokens=1000, temperature=0.7):
        return LLMResponse(
            content=f"Response from {self.provider_name} model {self.model}",
            model=self.model
        )

    @property
    def provider_name(self):
        return getattr(self, "_provider_name", "mock")

    def is_available(self):
        return True


@pytest.fixture
def mock_get_provider(monkeypatch):
    from council_ai.core import council as council_module

    def side_effect(name, **kwargs):
        provider = MockProvider(api_key=kwargs.get("api_key"), model=kwargs.get("model"))
        provider._provider_name = name
        return provider

    mock = MagicMock(side_effect=side_effect)
    monkeypatch.setattr(council_module, "get_provider", mock)
    return mock


@pytest.fixture
def mock_llm_manager(monkeypatch, mock_get_provider):
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
            resolved_provider = provider or self.preferred_provider
            return LLMResponse(
                content=f"Response from {resolved_provider} model {self.model}",
                model=self.model
            )

    from council_ai.core import council as council_module
    from council_ai import providers as providers_module

    monkeypatch.setattr(council_module, "LLMManager", MockLLMManager)
    monkeypatch.setattr(providers_module, "get_llm_manager", lambda **kwargs: MockLLMManager(**kwargs))
    return MockLLMManager
