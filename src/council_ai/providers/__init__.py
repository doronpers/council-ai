"""
LLM Provider Abstractions

Supports multiple LLM providers (Anthropic, OpenAI, custom endpoints).
"""

from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Optional, Type


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

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Stream a completion token by token.

        Default implementation collects stream and yields chunks.
        Providers should override for true streaming.
        """
        result = await self.complete(system_prompt, user_prompt, max_tokens, temperature)
        # Yield in chunks for default implementation
        chunk_size = 10
        for i in range(0, len(result), chunk_size):
            yield result[i : i + chunk_size]

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """
        Generate a structured completion following a JSON schema.

        Default implementation uses complete() and parses JSON.
        Providers should override for native structured output support.
        """
        import json

        # Add schema instruction to prompt
        schema_instruction = (
            f"\n\nRespond with valid JSON matching this schema: {json.dumps(json_schema, indent=2)}"
        )
        enhanced_prompt = user_prompt + schema_instruction

        result = await self.complete(system_prompt, enhanced_prompt, max_tokens, temperature)

        # Try to parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
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
            # Fallback: try to extract JSON object
            import re

            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse structured JSON from response: {result[:200]}")


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

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using Anthropic."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        async with client.messages.stream(
            model=self.model or self.DEFAULT_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for text_block in stream.text_stream:
                yield text_block

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """Generate structured completion using Anthropic."""
        try:
            import json

            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        # Anthropic supports response_format for structured output
        try:
            message = await client.messages.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                response_format={"type": "json_object"},
            )
            result_text = message.content[0].text
            return json.loads(result_text)
        except Exception:
            # Fallback to base implementation
            return await super().complete_structured(
                system_prompt, user_prompt, json_schema, max_tokens, temperature
            )


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider (also supports Vercel AI Gateway)."""

    DEFAULT_MODEL = "gpt-4-turbo-preview"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        # Try OpenAI key first, then Vercel AI Gateway key
        resolved_key = (
            api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
        )

        # If using Vercel AI Gateway, set the base URL
        if (
            not base_url
            and os.environ.get("AI_GATEWAY_API_KEY")
            and not os.environ.get("OPENAI_API_KEY")
        ):
            # Vercel AI Gateway endpoint (can be overridden)
            base_url = (
                base_url or os.environ.get("VERCEL_AI_GATEWAY_URL") or "https://api.vercel.ai/v1"
            )

        super().__init__(
            resolved_key,
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY, AI_GATEWAY_API_KEY, or pass api_key."
            )

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
            try:
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
            except openai.AuthenticationError as e:
                error_msg = str(e)
                # Provide helpful error messages
                if (
                    "Invalid API key" in error_msg
                    or "Incorrect API key" in error_msg
                    or "401" in error_msg
                ):
                    raise ValueError(
                        f"OpenAI API key authentication failed. "
                        f"Please verify your OPENAI_API_KEY or AI_GATEWAY_API_KEY is correct and not expired. "
                        f"Error details: {error_msg}. "
                        f"Run 'council providers --diagnose' for troubleshooting."
                    ) from e
                raise ValueError(f"OpenAI authentication error: {error_msg}") from e
            except openai.APIError as e:
                error_msg = str(e)
                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    raise ValueError(f"OpenAI rate limit exceeded: {error_msg}") from e
                raise ValueError(f"OpenAI API error: {error_msg}") from e
            except Exception as e:
                # Catch-all for other errors (network, timeout, etc.)
                error_msg = str(e)
                raise ValueError(f"OpenAI request failed: {error_msg}") from e

        return await asyncio.to_thread(_call)

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using OpenAI."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = openai.AsyncOpenAI(**client_kwargs)

        try:
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
        except openai.AuthenticationError as e:
            error_msg = str(e)
            if (
                "Invalid API key" in error_msg
                or "Incorrect API key" in error_msg
                or "401" in error_msg
            ):
                raise ValueError(
                    f"OpenAI API key authentication failed. "
                    f"Please verify your OPENAI_API_KEY or AI_GATEWAY_API_KEY is correct and not expired. "
                    f"Error details: {error_msg}. "
                    f"Run 'council providers --diagnose' for troubleshooting."
                ) from e
            raise ValueError(f"OpenAI authentication error: {error_msg}") from e
        except openai.APIError as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower() or "429" in error_msg:
                raise ValueError(f"OpenAI rate limit exceeded: {error_msg}") from e
            raise ValueError(f"OpenAI API error: {error_msg}") from e
        except Exception as e:
            error_msg = str(e)
            raise ValueError(f"OpenAI request failed: {error_msg}") from e

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """Generate structured completion using OpenAI."""
        try:
            import json

            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = openai.AsyncOpenAI(**client_kwargs)

        try:
            # OpenAI supports response_format for JSON mode
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
        except Exception:
            # Fallback to base implementation
            return await super().complete_structured(
                system_prompt, user_prompt, json_schema, max_tokens, temperature
            )


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

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using Google Gemini."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model or self.DEFAULT_MODEL)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Gemini streaming - need to use async wrapper
        def _stream():
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

        # Yield chunks as they arrive
        for chunk in response:
            if chunk.text:
                yield chunk.text


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

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using custom HTTP endpoint (SSE or chunked)."""
        import httpx

        async with httpx.AsyncClient() as client:
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
                # Try to parse as SSE (Server-Sent Events)
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            import json

                            chunk_data = json.loads(data)
                            if "completion" in chunk_data:
                                yield chunk_data["completion"]
                            elif "content" in chunk_data:
                                yield chunk_data["content"]
                            elif "delta" in chunk_data and "content" in chunk_data["delta"]:
                                yield chunk_data["delta"]["content"]
                        except json.JSONDecodeError:
                            # If not JSON, yield the raw data
                            if data.strip():
                                yield data
                    elif line.strip() and not line.startswith(":"):
                        # Plain text chunk
                        yield line


# Provider registry
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


def get_provider(name: str, **kwargs) -> LLMProvider:
    """Get a provider instance by name."""
    if name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Provider '{name}' not found. Available: {available}")

    return _PROVIDERS[name](**kwargs)


def list_providers() -> list[str]:
    """List available provider names."""
    return list(_PROVIDERS.keys())
