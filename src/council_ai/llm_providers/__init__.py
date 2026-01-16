"""
Local LLM Provider Implementations

This module provides a local implementation of LLM provider abstractions
that were originally planned to come from shared-ai-utils package.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelParameterSpec(BaseModel):
    """Specification for a model parameter."""

    name: str
    type: str
    min: Optional[float] = None
    max: Optional[float] = None
    default: Any = None
    description: str = ""


class ModelInfo(BaseModel):
    """Information about available models for a provider."""

    provider: str
    default_model: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    parameters: List[ModelParameterSpec] = Field(default_factory=list)


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    content: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    DEFAULT_MODEL: str = ""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.base_url = base_url

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion for the given prompt."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key, model, base_url)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion using Anthropic API."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

        client = anthropic.Anthropic(api_key=self.api_key)

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                finish_reason=response.stop_reason,
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key, model, base_url)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion using OpenAI API."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                finish_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    DEFAULT_MODEL = "gemini-1.5-pro-latest"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key, model, base_url)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion using Google Gemini API."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

        if not self.api_key:
            raise ValueError("Gemini API key not provided")

        genai.configure(api_key=self.api_key)

        try:
            model = genai.GenerativeModel(self.model)
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            response = model.generate_content(prompt, generation_config=generation_config)
            return LLMResponse(
                content=response.text,
                model=self.model,
                finish_reason="stop" if response.candidates else None,
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


class HTTPProvider(LLMProvider):
    """Generic HTTP/OpenAI-compatible provider."""

    DEFAULT_MODEL = "gpt-4o"

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion using HTTP API."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        if not self.api_key:
            raise ValueError("API key not provided for HTTP provider")

        if not self.base_url:
            raise ValueError("base_url required for HTTP provider")

        client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(response.usage, "completion_tokens", None),
                    "total_tokens": getattr(response.usage, "total_tokens", None),
                },
                finish_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logger.error(f"HTTP provider API error: {e}")
            raise


class LLMManager:
    """Manager for LLM providers with fallback support."""

    def __init__(self, preferred_provider: str = "openai"):
        self.preferred_provider = preferred_provider
        self._providers: Dict[str, LLMProvider] = {}

    def set_provider(self, name: str, provider: LLMProvider) -> None:
        """Register a provider instance."""
        self._providers[name] = provider

    async def complete(
        self,
        prompt: str,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a completion with fallback support."""
        target_provider = provider or self.preferred_provider

        if target_provider in self._providers:
            try:
                return await self._providers[target_provider].complete(
                    prompt, temperature, max_tokens, **kwargs
                )
            except Exception as e:
                logger.warning(f"Provider {target_provider} failed: {e}, trying fallback...")

        # Try other providers as fallback
        for name, prov in self._providers.items():
            if name != target_provider:
                try:
                    return await prov.complete(prompt, temperature, max_tokens, **kwargs)
                except Exception as e:
                    logger.warning(f"Fallback provider {name} failed: {e}")
                    continue

        raise RuntimeError("All LLM providers failed")


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
]
