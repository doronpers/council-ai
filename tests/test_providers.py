"""
Tests for provider abstractions.
"""

import pytest

from council_ai.providers import LLMProvider, get_provider, list_providers, register_provider


def test_list_providers():
    """Test listing available providers."""
    providers = list_providers()

    assert "anthropic" in providers
    assert "openai" in providers
    assert "gemini" in providers
    assert "http" in providers
    assert len(providers) >= 4


def test_get_nonexistent_provider():
    """Test error handling for nonexistent provider."""
    with pytest.raises(ValueError, match="not found"):
        get_provider("nonexistent_provider")


def test_anthropic_provider_without_key():
    """Test Anthropic provider without API key."""
    import os

    # Temporarily remove API key
    old_key = os.environ.pop("ANTHROPIC_API_KEY", None)

    try:
        with pytest.raises(ValueError, match="API key required"):
            get_provider("anthropic")
    finally:
        if old_key:
            os.environ["ANTHROPIC_API_KEY"] = old_key


def test_openai_provider_without_key():
    """Test OpenAI provider without API key."""
    import os

    # Temporarily remove API keys (including fallback keys)
    old_key = os.environ.pop("OPENAI_API_KEY", None)
    old_gw_key = os.environ.pop("AI_GATEWAY_API_KEY", None)

    try:
        with pytest.raises(ValueError, match="API key required"):
            get_provider("openai")
    finally:
        if old_key:
            os.environ["OPENAI_API_KEY"] = old_key
        if old_gw_key:
            os.environ["AI_GATEWAY_API_KEY"] = old_gw_key


def test_gemini_provider_without_key():
    """Test Gemini provider without API key."""
    import os

    # Temporarily remove API key
    old_key = os.environ.pop("GEMINI_API_KEY", None)

    try:
        with pytest.raises(ValueError, match="API key required"):
            get_provider("gemini")
    finally:
        if old_key:
            os.environ["GEMINI_API_KEY"] = old_key


def test_http_provider_without_endpoint():
    """Test HTTP provider without endpoint."""
    import os

    old_endpoint = os.environ.pop("LLM_ENDPOINT", None)

    try:
        with pytest.raises(ValueError, match="endpoint required"):
            get_provider("http", api_key="test-key")
    finally:
        if old_endpoint:
            os.environ["LLM_ENDPOINT"] = old_endpoint


def test_http_provider_env_api_key(monkeypatch):
    """Test HTTP provider uses env API key defaults."""
    monkeypatch.setenv("HTTP_API_KEY", "env-key")
    provider = get_provider("http", endpoint="https://example.com/v1/completions")
    assert provider.api_key == "env-key"


def test_custom_provider_registration():
    """Test registering a custom provider."""

    class CustomProvider(LLMProvider):
        async def complete(self, system_prompt, user_prompt, max_tokens=1000, temperature=0.7):
            return "Custom response"

    register_provider("custom_test", CustomProvider)

    providers = list_providers()
    assert "custom_test" in providers

    provider = get_provider("custom_test", api_key="test")
    assert isinstance(provider, CustomProvider)


def test_provider_with_api_key():
    """Test creating provider with explicit API key."""
    # These should not raise even without env vars
    try:
        provider = get_provider("anthropic", api_key="test-key")
        assert provider.api_key == "test-key"
    except ImportError:
        pytest.skip("anthropic package not installed")

    try:
        provider = get_provider("openai", api_key="test-key")
        assert provider.api_key == "test-key"
    except ImportError:
        pytest.skip("openai package not installed")

    try:
        provider = get_provider("gemini", api_key="test-key")
        assert provider.api_key == "test-key"
    except ImportError:
        pytest.skip("google-generativeai package not installed")


def test_provider_base_class():
    """Test that provider base class is abstract."""
    with pytest.raises(TypeError):
        # Cannot instantiate abstract class
        LLMProvider(api_key="test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
