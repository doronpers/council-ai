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

from shared_ai_utils.llm import AnthropicProvider as _BaseAnthropicProvider
from shared_ai_utils.llm import GeminiProvider as _BaseGeminiProvider
from shared_ai_utils.llm import HTTPProvider as _BaseHTTPProvider
from shared_ai_utils.llm import (
    LLMManager,
    LLMProvider,
    LLMResponse,
    ModelInfo,
    ModelParameterSpec,
)
from shared_ai_utils.llm import OpenAIProvider as _BaseOpenAIProvider

from .resilience import RateLimiter, ResilienceConfig, ResilientProvider

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
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
    ) -> LLMResponse:
        """Generate a completion using OpenAI (supports LM Studio extensions)."""

        def _call() -> tuple[str, Optional[int], Optional[int]]:
            client = self._get_client()
            # Build parameters dict, only including non-None values
            create_params = {
                "model": self.model or self.DEFAULT_MODEL,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
            # Add optional parameters
            # Standard OpenAI API parameters (always supported by OpenAI Python client)
            if top_p is not None:
                create_params["top_p"] = top_p
            if frequency_penalty is not None:
                create_params["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                create_params["presence_penalty"] = presence_penalty

            # Note: top_k and repetition_penalty are NOT supported by the OpenAI Python client
            # even if the underlying API (like LM Studio) supports them. These parameters
            # would need to be passed via extra_headers or a different mechanism.
            # For now, we only use standard OpenAI parameters to avoid TypeError.

            response = client.chat.completions.create(**create_params)
            text = response.choices[0].message.content
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else None
            output_tokens = usage.completion_tokens if usage else None
            return text, input_tokens, output_tokens

        text, input_tokens, output_tokens = await asyncio.to_thread(_call)
        total_tokens = (
            input_tokens + output_tokens
            if (input_tokens is not None and output_tokens is not None)
            else None
        )

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
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """Stream a completion using OpenAI (supports LM Studio extensions)."""
        client = self._get_async_client()
        create_params = {
            "model": self.model or self.DEFAULT_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }
        # Add optional parameters
        # Standard OpenAI API parameters (always supported by OpenAI Python client)
        if top_p is not None:
            create_params["top_p"] = top_p
        if frequency_penalty is not None:
            create_params["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            create_params["presence_penalty"] = presence_penalty

        # Note: top_k and repetition_penalty are NOT supported by the OpenAI Python client
        # even if the underlying API (like LM Studio) supports them. These parameters
        # would need to be passed via extra_headers or a different mechanism.
        # For now, we only use standard OpenAI parameters to avoid TypeError.

        stream = await client.chat.completions.create(**create_params)
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
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("OpenAI returned empty response for structured output")
            return json.loads(content)
        except Exception as exc:
            logger.debug(
                f"OpenAI structured output failed, falling back to base: {exc}"
            )
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

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
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
            client = self._get_client()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = client.models.generate_content(
                model=self.model or self.DEFAULT_MODEL,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            try:
                # Accessing response.text can raise a ValueError if the response was blocked.
                content = response.text
                if content is None:
                    raise ValueError("Gemini returned a null response.")
                return content
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Gemini returned an empty or invalid response: {e}") from e

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
            client = self._get_client()
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            from google.genai import types

            response = client.models.generate_content_stream(
                model=self.model or self.DEFAULT_MODEL,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            return response

        response = await asyncio.to_thread(_stream)

        for chunk in response:
            # Extract text from chunk - structure may vary
            chunk_text = None
            if hasattr(chunk, "text") and chunk.text:
                chunk_text = chunk.text
            elif hasattr(chunk, "candidates") and chunk.candidates:
                # Some chunk formats have candidates
                for candidate in chunk.candidates:
                    if hasattr(candidate, "content") and hasattr(
                        candidate.content, "parts"
                    ):
                        for part in candidate.content.parts:
                            if hasattr(part, "text"):
                                chunk_text = part.text
                                break
                    if chunk_text:
                        break
            if chunk_text:
                yield chunk_text


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
    "lmstudio": ModelInfo(
        provider="lmstudio",
        default_model="local-model",  # LM Studio uses whatever model is loaded
        models=["local-model"],
        parameters=_GENERATION_PARAM_SPECS,
    ),
}

_PROVIDERS: Dict[str, Type[LLMProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "http": HTTPProvider,
    "vercel": OpenAIProvider,
    "lmstudio": OpenAIProvider,  # LM Studio uses OpenAI-compatible API
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

    # Set base_url for lmstudio if not provided
    if name == "lmstudio" and "base_url" not in kwargs:
        kwargs["base_url"] = "http://localhost:1234/v1"
        # LM Studio doesn't require an API key
        if "api_key" not in kwargs:
            kwargs["api_key"] = (
                "lm-studio"  # pragma: allowlist secret  # Dummy key for OpenAI client
            )

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
        # Support standard parameters plus LM Studio/OpenAI-compatible extensions
        if norm_key in {
            "temperature",
            "max_tokens",
            "top_p",
            "top_k",
            "repetition_penalty",
            "frequency_penalty",
            "presence_penalty",
        }:
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
    if "top_p" in params:
        top_p = params["top_p"]
        if not (0.0 <= top_p <= 1.0):
            raise ValueError("top_p must be between 0.0 and 1.0")
    if "top_k" in params:
        top_k = params["top_k"]
        if not (isinstance(top_k, int) and top_k >= 0):
            raise ValueError("top_k must be a non-negative integer")
    if "repetition_penalty" in params:
        rp = params["repetition_penalty"]
        if not (0.0 <= rp <= 2.0):
            raise ValueError("repetition_penalty must be between 0.0 and 2.0")
    if "frequency_penalty" in params:
        fp = params["frequency_penalty"]
        if not (-2.0 <= fp <= 2.0):
            raise ValueError("frequency_penalty must be between -2.0 and 2.0")
    if "presence_penalty" in params:
        pp = params["presence_penalty"]
        if not (-2.0 <= pp <= 2.0):
            raise ValueError("presence_penalty must be between -2.0 and 2.0")


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
    "ResilientProvider",
    "ResilienceConfig",
    "RateLimiter",
    "register_provider",
    "get_provider",
    "get_llm_manager",
    "list_providers",
    "list_model_capabilities",
    "normalize_model_params",
    "validate_model_params",
]
