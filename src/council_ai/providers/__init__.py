"""
LLM Provider Abstractions (Council AI)

Standalone implementations for multiple LLM providers.
"""

from __future__ import annotations

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Type

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ModelParameterSpec(BaseModel):
    """Supported generation parameter specification."""

    name: str
    type: str = Field(..., description="Parameter type (int, float, string)")
    min: Optional[float] = None
    max: Optional[float] = None
    default: Optional[float] = None
    description: Optional[str] = None


class ModelInfo(BaseModel):
    """Model capability information for a provider."""

    provider: str
    default_model: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    parameters: List[ModelParameterSpec] = Field(default_factory=list)


class LLMResponse(BaseModel):
    """Result of an LLM completion."""

    text: str
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None


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
    ) -> LLMResponse:
        """Generate a completion."""
        pass

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion token by token."""
        response = await self.complete(system_prompt, user_prompt, max_tokens, temperature)
        # Simple chunking if streaming is not natively implemented
        chunk_size = 20
        for i in range(0, len(response.text), chunk_size):
            yield response.text[i : i + chunk_size]
            await asyncio.sleep(0.01)

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """Generate a structured completion following a JSON schema."""
        import json

        schema_instruction = (
            f"\n\nRespond with valid JSON matching this schema: {json.dumps(json_schema, indent=2)}"
        )
        enhanced_prompt = user_prompt + schema_instruction

        response = await self.complete(system_prompt, enhanced_prompt, max_tokens, temperature)
        result = response.text

        try:
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                result = result[json_start:json_end].strip()
            elif "```" in result:
                json_start = result.find("```") + 3
                json_end = result.find("```", json_start)
                result = result[json_start:json_end].strip()

            return json.loads(result)
        except json.JSONDecodeError:
            import re

            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse structured JSON from response: {result[:200]}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    DEFAULT_MODEL = "claude-3-5-sonnet-20240620"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("ANTHROPIC_API_KEY"),
            model=model or self.DEFAULT_MODEL,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("Anthropic API key required.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed.")

        def _call() -> str:
            client = anthropic.Anthropic(api_key=self.api_key, base_url=self.base_url)
            message = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text

        text = await asyncio.to_thread(_call)
        return LLMResponse(text=text, model=self.model)

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed.")

        client = anthropic.AsyncAnthropic(api_key=self.api_key, base_url=self.base_url)
        async with client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for text_block in stream.text_stream:
                yield text_block


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("OPENAI_API_KEY"),
            model=model or self.DEFAULT_MODEL,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("OpenAI API key required.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed.")

        def _call() -> str:
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content

        text = await asyncio.to_thread(_call)
        return LLMResponse(text=text, model=self.model)

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed.")

        client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        stream = await client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    DEFAULT_MODEL = "gemini-1.5-pro"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("GEMINI_API_KEY"),
            model=model or self.DEFAULT_MODEL,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("Gemini API key required.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed.")

        def _call() -> str:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return response.text

        text = await asyncio.to_thread(_call)
        return LLMResponse(text=text, model=self.model)

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed.")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        def _stream():
            return model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                stream=True,
            )

        response = await asyncio.to_thread(_stream)
        for chunk in response:
            if chunk.text:
                yield chunk.text


class HTTPProvider(LLMProvider):
    """Custom HTTP endpoint provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(
            api_key or os.environ.get("COUNCIL_API_KEY"), model=model, base_url=base_url
        )
        if not self.base_url:
            raise ValueError("HTTP base_url required.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        import httpx

        async with httpx.AsyncClient() as client:
            payload = {
                "system": system_prompt,
                "prompt": user_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "model": self.model,
            }
            response = await client.post(
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=60.0,
            )
            response.raise_for_status()
            text = response.json().get("completion", response.text)
            return LLMResponse(text=text, model=self.model)


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
