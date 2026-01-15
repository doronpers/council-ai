"""
LLM Provider Abstractions (Council AI)

Thin wrappers around shared-ai-utils LLM providers to keep a single
implementation of provider logic across repositories.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Type

from shared_ai_utils.llm import (
    AnthropicProvider,
    GeminiProvider,
    HTTPProvider,
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
    "vercel": OpenAIProvider,  # Vercel AI Gateway is OpenAI-compatible
}


def register_provider(name: str, provider_class: Type[LLMProvider]) -> None:
    """Register a custom provider."""
    _PROVIDERS[name] = provider_class


def _filter_provider_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Filter kwargs to parameters supported by shared providers."""
    allowed = {"api_key", "model", "base_url", "endpoint"}
    return {key: value for key, value in kwargs.items() if key in allowed}


def get_provider(name: str, **kwargs) -> LLMProvider:
    """Get a provider instance by name."""
    if name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Provider '{name}' not found. Available: {available}")

    provider_kwargs = _filter_provider_kwargs(kwargs)
    return _PROVIDERS[name](**provider_kwargs)


def list_providers() -> list[str]:
    """List available provider names."""
    return list(_PROVIDERS.keys())


def list_model_capabilities() -> list[dict]:
    """List available models and supported parameters per provider."""
    return [info.model_dump() for info in _MODEL_CAPABILITIES.values()]


def normalize_model_params(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize model parameter keys and filter supported overrides."""
    if not params:
        return {}

    normalized: Dict[str, Any] = {}
    for key, value in params.items():
        normalized_key = "max_tokens" if key == "max_tokens_per_response" else key
        if normalized_key not in {"temperature", "max_tokens"}:
            raise ValueError(f"Unsupported model parameter '{key}'.")
        normalized[normalized_key] = value
    return normalized


def validate_model_params(params: Dict[str, Any]) -> None:
    """Validate model parameter values."""
    if "temperature" in params:
        temperature = params["temperature"]
        if not isinstance(temperature, (int, float)):
            raise ValueError("temperature must be a number.")
        if temperature < 0.0 or temperature > 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0.")

    if "max_tokens" in params:
        max_tokens = params["max_tokens"]
        if not isinstance(max_tokens, int):
            raise ValueError("max_tokens must be an integer.")
        if max_tokens < 1 or max_tokens > 4096:
            raise ValueError("max_tokens must be between 1 and 4096.")


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "AnthropicProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "HTTPProvider",
    "ModelInfo",
    "ModelParameterSpec",
    "register_provider",
    "get_provider",
    "list_providers",
    "list_model_capabilities",
    "normalize_model_params",
    "validate_model_params",
]
