"""
LLM Provider Abstractions

Supports multiple LLM providers (Anthropic, OpenAI, custom endpoints).
"""

from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional, Type


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a completion."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("ANTHROPIC_API_KEY"),
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY or pass api_key.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a completion using Anthropic."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        def _call() -> str:
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text

        return await asyncio.to_thread(_call)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    DEFAULT_MODEL = "gpt-4-turbo-preview"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("OPENAI_API_KEY"),
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or pass api_key.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a completion using OpenAI."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        def _call() -> str:
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            client = openai.OpenAI(**client_kwargs)
            response = client.chat.completions.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content

        return await asyncio.to_thread(_call)


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    DEFAULT_MODEL = "gemini-pro"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("GEMINI_API_KEY"),
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY or pass api_key.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a completion using Google Gemini."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            )

        def _call() -> str:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model or self.DEFAULT_MODEL)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return response.text

        return await asyncio.to_thread(_call)


class HTTPProvider(LLMProvider):
    """Custom HTTP endpoint provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        resolved_api_key = (
            api_key or os.environ.get("HTTP_API_KEY") or os.environ.get("COUNCIL_API_KEY")
        )
        super().__init__(resolved_api_key, model=model, base_url=base_url)
        self.endpoint = endpoint or base_url or os.environ.get("LLM_ENDPOINT")
        if not self.endpoint:
            raise ValueError("HTTP endpoint required. Set LLM_ENDPOINT or pass endpoint.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a completion using custom HTTP endpoint."""
        import httpx

        async with httpx.AsyncClient() as client:
            payload = {
                "system": system_prompt,
                "prompt": user_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if self.model:
                payload["model"] = self.model
            response = await client.post(
                self.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()["completion"]


# Provider registry
_PROVIDERS: Dict[str, Type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "http": HTTPProvider,
}


def register_provider(name: str, provider_class: Type[LLMProvider]) -> None:
    """Register a custom provider."""
    _PROVIDERS[name] = provider_class


def get_provider(name: str, **kwargs) -> LLMProvider:
    """Get a provider instance by name."""
    if name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Provider '{name}' not found. Available: {available}")

    return _PROVIDERS[name](**kwargs)


def list_providers() -> list[str]:
    """List available provider names."""
    return list(_PROVIDERS.keys())
