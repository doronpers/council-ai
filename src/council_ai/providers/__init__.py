"""
LLM Provider Abstractions (Council AI)

Standalone implementations for multiple LLM providers.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Type

from shared_ai_utils.llm import (
    AnthropicProvider,
    GeminiProvider,
    HTTPProvider,
    LLMManager,
    LLMProvider,
    LLMResponse,
    ModelInfo,
    ModelParameterSpec,
    OpenAIProvider,
)

logger = logging.getLogger(__name__)


_GENERATION_PARAM_SPECS = [
    ModelParameterSpec(
        name="temperature",
        type="float",
        min=0.0,
        max=2.0,
        default=0.7,
        description="Sampling temperature (higher is more creative).",
    ),
    ModelParameterSpec(
        name="max_tokens",
        type="int",
        min=1,
        max=4096,
        default=1000,
        description="Maximum tokens to generate per response.",
    ),
]


_MODEL_CAPABILITIES: Dict[str, ModelInfo] = {
    "anthropic": ModelInfo(
        provider="anthropic",
        default_model=AnthropicProvider.DEFAULT_MODEL,
        models=[AnthropicProvider.DEFAULT_MODEL],
        parameters=_GENERATION_PARAM_SPECS,
    ),
    "openai": ModelInfo(
        provider="openai",
        default_model=OpenAIProvider.DEFAULT_MODEL,
        models=[OpenAIProvider.DEFAULT_MODEL],
        parameters=_GENERATION_PARAM_SPECS,
    ),
    "gemini": ModelInfo(
        provider="gemini",
        default_model=GeminiProvider.DEFAULT_MODEL,
        models=[GeminiProvider.DEFAULT_MODEL],
        parameters=_GENERATION_PARAM_SPECS,
    ),
    "http": ModelInfo(
        provider="http",
        default_model=None,
        models=[],
        parameters=_GENERATION_PARAM_SPECS,
    ),
    "vercel": ModelInfo(
        provider="vercel",
        default_model=OpenAIProvider.DEFAULT_MODEL,
        models=[OpenAIProvider.DEFAULT_MODEL],
        parameters=_GENERATION_PARAM_SPECS,
    ),
}

_PROVIDERS: Dict[str, Type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "http": HTTPProvider,
    "vercel": OpenAIProvider,
}


def register_provider(name: str, provider_class: Type[LLMProvider]) -> None:
    """Register a custom provider."""
    _PROVIDERS[name] = provider_class


def _filter_provider_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Filter kwargs to parameters supported by providers."""
    allowed = {"api_key", "model", "base_url"}
    # Backward compat: endpoint -> base_url
    if "endpoint" in kwargs and "base_url" not in kwargs:
        kwargs["base_url"] = kwargs.pop("endpoint")
    return {k: v for k, v in kwargs.items() if k in allowed}


def get_provider(name: str, **kwargs) -> LLMProvider:
    """Get a provider instance by name."""
    if name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Provider '{name}' not found. Available: {available}")

    provider_kwargs = _filter_provider_kwargs(kwargs)
    return _PROVIDERS[name](**provider_kwargs)


def get_llm_manager(
    preferred_provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> LLMManager:
    """Create an LLMManager configured for Council defaults.

    Note: api_key, model, and base_url are not passed to LLMManager
    as it initializes providers from environment variables.
    These parameters are kept for API compatibility but unused.
    """
    return LLMManager(
        preferred_provider=preferred_provider,
    )


def list_providers() -> list[str]:
    """List available provider names."""
    return list(_PROVIDERS.keys())


def list_model_capabilities() -> list[dict]:
    """List available model capabilities."""
    return [info.model_dump() for info in _MODEL_CAPABILITIES.values()]


def normalize_model_params(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize and filter model parameters."""
    if not params:
        return {}
    normalized: Dict[str, Any] = {}
    for key, value in params.items():
        norm_key = "max_tokens" if key == "max_tokens_per_response" else key
        if norm_key in {"temperature", "max_tokens"}:
            normalized[norm_key] = value
    return normalized


def validate_model_params(params: Dict[str, Any]) -> None:
    """Validate model parameter values."""
    if "temperature" in params:
        t = params["temperature"]
        if not (0.0 <= t <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
    if "max_tokens" in params:
        m = params["max_tokens"]
        if m < 1:
            raise ValueError("max_tokens must be positive")


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "LLMManager",
    "AnthropicProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "HTTPProvider",
    "ModelInfo",
    "ModelParameterSpec",
    "register_provider",
    "get_provider",
    "get_llm_manager",
    "list_providers",
    "list_model_capabilities",
    "normalize_model_params",
    "validate_model_params",
]
