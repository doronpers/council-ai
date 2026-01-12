"""
Text-to-Speech (TTS) provider implementations for Council AI.

Supports ElevenLabs (primary) and OpenAI (fallback) TTS providers.
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

import aiohttp

logger = logging.getLogger(__name__)


class TTSProvider(ABC):
    """Base class for TTS providers."""

    @abstractmethod
    async def generate_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> bytes:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice ID or name
            model: TTS model to use

        Returns:
            Audio bytes in MP3 format
        """
        pass

    @abstractmethod
    async def stream_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        Stream speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice ID or name
            model: TTS model to use

        Yields:
            Audio chunk bytes
        """
        pass

    @abstractmethod
    async def list_voices(self) -> list[dict]:
        """
        List available voices.

        Returns:
            List of voice dictionaries with 'id', 'name', and optional metadata
        """
        pass


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS provider implementation."""

    DEFAULT_VOICE = "EXAVITQu4vr4xnSDxMaL"  # Sarah voice
    DEFAULT_MODEL = "eleven_turbo_v2_5"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ElevenLabs provider.

        Args:
            api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY environment variable "
                "or provide api_key parameter."
            )
        self.base_url = "https://api.elevenlabs.io/v1"

    async def generate_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> bytes:
        """Generate speech using ElevenLabs API."""
        voice = voice or self.DEFAULT_VOICE
        model = model or self.DEFAULT_MODEL

        url = f"{self.base_url}/text-to-speech/{voice}"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs TTS error: {error_text}")
                        raise Exception(f"ElevenLabs API error: {response.status}")
                    return await response.read()
        except Exception as e:
            logger.error(f"ElevenLabs TTS generation failed: {e}")
            raise

    async def stream_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """Stream speech using ElevenLabs API."""
        voice = voice or self.DEFAULT_VOICE
        model = model or self.DEFAULT_MODEL

        url = f"{self.base_url}/text-to-speech/{voice}/stream"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs TTS streaming error: {error_text}")
                        raise Exception(f"ElevenLabs API error: {response.status}")

                    async for chunk in response.content.iter_chunked(4096):
                        if chunk:
                            yield chunk
        except Exception as e:
            logger.error(f"ElevenLabs TTS streaming failed: {e}")
            raise

    async def list_voices(self) -> list[dict]:
        """List available ElevenLabs voices."""
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to list ElevenLabs voices: {response.status}")
                        return self._get_default_voices()

                    data = await response.json()
                    voices = []
                    for voice in data.get("voices", []):
                        voices.append(
                            {
                                "id": voice["voice_id"],
                                "name": voice["name"],
                                "category": voice.get("category", "premade"),
                                "labels": voice.get("labels", {}),
                            }
                        )
                    return voices
        except Exception as e:
            logger.error(f"Failed to fetch ElevenLabs voices: {e}")
            return self._get_default_voices()

    def _get_default_voices(self) -> list[dict]:
        """Return default voice options."""
        return [
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "category": "premade"},
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "category": "premade"},
            {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "category": "premade"},
            {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "category": "premade"},
        ]


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS provider implementation (fallback)."""

    DEFAULT_VOICE = "alloy"
    DEFAULT_MODEL = "tts-1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI TTS provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or provide api_key parameter."
            )
        self.base_url = "https://api.openai.com/v1"

    async def generate_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> bytes:
        """Generate speech using OpenAI TTS API."""
        voice = voice or self.DEFAULT_VOICE
        model = model or self.DEFAULT_MODEL

        url = f"{self.base_url}/audio/speech"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "input": text, "voice": voice, "response_format": "mp3"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI TTS error: {error_text}")
                        raise Exception(f"OpenAI API error: {response.status}")
                    return await response.read()
        except Exception as e:
            logger.error(f"OpenAI TTS generation failed: {e}")
            raise

    async def stream_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        Stream speech using OpenAI TTS API.
        Note: OpenAI doesn't support true streaming, so we generate and chunk the response.
        """
        audio_data = await self.generate_speech(text, voice, model)

        # Chunk the audio data for pseudo-streaming
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i : i + chunk_size]
            await asyncio.sleep(0.01)  # Small delay to simulate streaming

    async def list_voices(self) -> list[dict]:
        """List available OpenAI voices."""
        # OpenAI voices are hardcoded in their API
        return [
            {"id": "alloy", "name": "Alloy", "description": "Neutral and balanced"},
            {"id": "echo", "name": "Echo", "description": "Male voice"},
            {"id": "fable", "name": "Fable", "description": "British accent"},
            {"id": "onyx", "name": "Onyx", "description": "Deep and authoritative"},
            {"id": "nova", "name": "Nova", "description": "Friendly female"},
            {"id": "shimmer", "name": "Shimmer", "description": "Warm and expressive"},
        ]


class TTSProviderFactory:
    """Factory for creating TTS providers."""

    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: Optional[str] = None,
        fallback_provider: Optional[str] = None,
        fallback_api_key: Optional[str] = None,
    ) -> tuple[TTSProvider, Optional[TTSProvider]]:
        """
        Create TTS provider with optional fallback.

        Args:
            provider_name: Primary provider name ("elevenlabs" or "openai")
            api_key: API key for primary provider
            fallback_provider: Fallback provider name
            fallback_api_key: API key for fallback provider

        Returns:
            Tuple of (primary_provider, fallback_provider)
        """
        primary = None
        fallback = None

        # Create primary provider
        try:
            if provider_name.lower() == "elevenlabs":
                primary = ElevenLabsTTSProvider(api_key)
            elif provider_name.lower() == "openai":
                primary = OpenAITTSProvider(api_key)
            else:
                raise ValueError(f"Unknown TTS provider: {provider_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize primary TTS provider {provider_name}: {e}")

        # Create fallback provider
        if fallback_provider:
            try:
                if fallback_provider.lower() == "elevenlabs":
                    fallback = ElevenLabsTTSProvider(fallback_api_key)
                elif fallback_provider.lower() == "openai":
                    fallback = OpenAITTSProvider(fallback_api_key)
            except Exception as e:
                logger.warning(
                    f"Failed to initialize fallback TTS provider {fallback_provider}: {e}"
                )

        return primary, fallback


async def generate_speech_with_fallback(
    text: str,
    primary: Optional[TTSProvider],
    fallback: Optional[TTSProvider],
    voice: Optional[str] = None,
    model: Optional[str] = None,
) -> bytes:
    """
    Generate speech with automatic fallback.

    Args:
        text: Text to convert to speech
        primary: Primary TTS provider
        fallback: Fallback TTS provider
        voice: Voice ID or name
        model: TTS model

    Returns:
        Audio bytes in MP3 format

    Raises:
        Exception if both providers fail
    """
    if primary:
        try:
            return await primary.generate_speech(text, voice, model)
        except Exception as e:
            logger.warning(f"Primary TTS provider failed, trying fallback: {e}")

    if fallback:
        try:
            return await fallback.generate_speech(text, voice, model)
        except Exception as e:
            logger.error(f"Fallback TTS provider also failed: {e}")
            raise Exception("All TTS providers failed")

    raise Exception("No TTS providers available")
