"""
LLM Provider Abstractions (Council AI)

Standalone implementations for multiple LLM providers.

Provider instances are expected to be long-lived and reused per Council instance.
Each provider lazily initializes and caches SDK/HTTP clients; if you create a new
provider instance per request, you will forfeit connection pooling benefits.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Optional, Type

from shared_ai_utils.llm import (
    AnthropicProvider as _BaseAnthropicProvider,
)
from shared_ai_utils.llm import (
    GeminiProvider as _BaseGeminiProvider,
)
from shared_ai_utils.llm import (
    HTTPProvider as _BaseHTTPProvider,
)
from shared_ai_utils.llm import (
    LLMManager,
    LLMProvider,
    LLMResponse,
    ModelInfo,
    ModelParameterSpec,
)
from shared_ai_utils.llm import (
    OpenAIProvider as _BaseOpenAIProvider,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(_BaseAnthropicProvider):
    """Anthropic provider with cached SDK clients."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key=api_key, model=model, base_url=base_url)
        self._client = None
        self._async_client = None

    def _get_client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def _get_async_client(self):
        if self._async_client is None:
            import anthropic

            self._async_client = anthropic.AsyncAnthropic(api_key=self.api_key)
        return self._async_client

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using Anthropic."""

        def _call() -> tuple[str, int, int]:
            client = self._get_client()
            message = client.messages.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            text = message.content[0].text
            return text, input_tokens, output_tokens

        text, input_tokens, output_tokens = await asyncio.to_thread(_call)

        return LLMResponse(
            text=text,
            model=self.model or self.DEFAULT_MODEL,
            provider="anthropic",
            tokens_used=input_tokens + output_tokens,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using Anthropic."""
        client = self._get_async_client()
        async with client.messages.stream(
            model=self.model or self.DEFAULT_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for text_block in stream.text_stream:
                yield text_block


class OpenAIProvider(_BaseOpenAIProvider):
    """OpenAI provider with cached SDK clients."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key=api_key, model=model, base_url=base_url)
        self._client = None
        self._async_client = None

    def _get_client(self):
        if self._client is None:
            import openai

            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self._client = openai.OpenAI(**client_kwargs)
        return self._client

    def _get_async_client(self):
        if self._async_client is None:
            import openai

            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self._async_client = openai.AsyncOpenAI(**client_kwargs)
        return self._async_client

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using OpenAI."""

        def _call() -> tuple[str, Optional[int], Optional[int]]:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = response.choices[0].message.content
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else None
            output_tokens = usage.completion_tokens if usage else None
            return text, input_tokens, output_tokens

        text, input_tokens, output_tokens = await asyncio.to_thread(_call)
        total_tokens = (input_tokens + output_tokens) if (input_tokens and output_tokens) else None

        return LLMResponse(
            text=text,
            model=self.model or self.DEFAULT_MODEL,
            provider="openai",
            tokens_used=total_tokens,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using OpenAI."""
        client = self._get_async_client()
        stream = await client.chat.completions.create(
            model=self.model or self.DEFAULT_MODEL,
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

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """Generate structured completion using OpenAI."""
        client = self._get_async_client()

        try:
            response = await client.chat.completions.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            result_text = response.choices[0].message.content
            return json.loads(result_text)
        except Exception as exc:
            logger.debug(f"OpenAI structured output failed, falling back to base: {exc}")
            return await super().complete_structured(
                system_prompt, user_prompt, json_schema, max_tokens, temperature
            )


class GeminiProvider(_BaseGeminiProvider):
    """Google Gemini provider with cached model client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key=api_key, model=model, base_url=base_url)
        self._client = None
        self._async_client = None

    def _get_model(self):
        if self._client is None:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model or self.DEFAULT_MODEL)
        return self._client

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using Google Gemini."""

        def _call() -> str:
            model = self._get_model()
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

        return LLMResponse(
            text=text,
            model=self.model or self.DEFAULT_MODEL,
            provider="gemini",
            tokens_used=None,
            metadata={},
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using Google Gemini."""

        def _stream():
            model = self._get_model()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                stream=True,
            )
            return response

        response = await asyncio.to_thread(_stream)

        for chunk in response:
            if chunk.text:
                yield chunk.text


class HTTPProvider(_BaseHTTPProvider):
    """Custom HTTP endpoint provider with shared AsyncClient."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key=api_key, endpoint=endpoint, model=model, base_url=base_url)
        self._client = None
        self._async_client = None

    def _get_async_client(self):
        if self._async_client is None:
            import httpx

            self._async_client = httpx.AsyncClient()
        return self._async_client

    async def close(self) -> None:
        """Close the shared HTTP client (call during shutdown)."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using custom HTTP endpoint."""
        client = self._get_async_client()
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
        result = response.json()
        completion = result.get("completion", result.get("text", ""))
        return LLMResponse(
            text=completion,
            model=self.model or "custom",
            provider="http",
            tokens_used=result.get("tokens_used"),
            metadata=result.get("metadata", {}),
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using custom HTTP endpoint (SSE or chunked)."""
        client = self._get_async_client()
        payload = {
            "system": system_prompt,
            "prompt": user_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        if self.model:
            payload["model"] = self.model
        async with client.stream(
            "POST",
            self.endpoint,
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            timeout=60.0,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            yield data.get("text", data.get("content", ""))
                        except json.JSONDecodeError:
                            yield line[6:]
                    else:
                        yield line


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
