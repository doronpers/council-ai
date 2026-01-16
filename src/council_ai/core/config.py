"""
Configuration Management
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from shared_ai_utils.config import ConfigManager as SharedConfigManager

logger = logging.getLogger(__name__)


def is_placeholder_key(value: Optional[str]) -> bool:
    """Return True if an API key looks like a placeholder value."""
    if value is None:
        return False
    normalized = value.strip().lower()
    if not normalized:
        return False

    placeholder_exact = {"your-key", "your_api_key", "your api key", "here"}
    placeholder_prefixes = ("your-", "your_", "your ")
    placeholder_substrings = ("paste-here", "enter-here")

    if normalized in placeholder_exact:
        return True
    if normalized.startswith(placeholder_prefixes):
        return True
    if "your-" in normalized:
        return True
    if any(token in normalized for token in placeholder_substrings):
        return True

    return False


def sanitize_api_key(value: Optional[str]) -> Optional[str]:
    """Normalize and drop placeholder API keys."""
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or is_placeholder_key(cleaned):
        return None
    return cleaned


# Load .env file automatically if python-dotenv is available
try:
    from dotenv import load_dotenv

    # Load .env from project root (wherever the package is installed/run from)
    # Try multiple common locations
    _env_loaded = False
    env_paths_to_try = [
        Path.cwd() / ".env",  # Current working directory
        Path(__file__).parent.parent.parent.parent / ".env",  # Project root (if running from repo)
        Path.home() / ".council-ai" / ".env",  # User home directory
    ]

    for env_path in env_paths_to_try:
        if env_path.exists():
            # Check if any API key env vars are placeholders - if so, override them
            api_key_vars = [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GEMINI_API_KEY",
                "AI_GATEWAY_API_KEY",
                "COUNCIL_API_KEY",
                "ELEVENLABS_API_KEY",
            ]
            has_placeholder = False
            for var in api_key_vars:
                existing_val = os.environ.get(var, "")
                if existing_val and is_placeholder_key(existing_val):
                    has_placeholder = True
                    break

            # Override placeholders or use override=False to preserve real env vars
            load_dotenv(env_path, override=has_placeholder)
            _env_loaded = True
            break
    # Also try loading from current directory as fallback
    if not _env_loaded:
        load_dotenv(override=False)
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


class APIConfig(BaseModel):
    """API configuration."""

    provider: str = "openai"
    api_key: Optional[str] = None
    model: Optional[str] = None  # Uses provider default if not set
    base_url: Optional[str] = None


class TTSConfig(BaseModel):
    """Text-to-Speech configuration."""

    enabled: bool = False  # TTS disabled by default
    provider: str = "elevenlabs"  # Primary provider
    api_key: Optional[str] = None  # Primary API key
    voice: Optional[str] = None  # Voice ID/name (uses provider default if not set)
    model: Optional[str] = None  # TTS model (uses provider default if not set)
    fallback_provider: Optional[str] = "openai"  # Fallback provider
    fallback_api_key: Optional[str] = None  # Fallback API key
    fallback_voice: Optional[str] = None  # Fallback voice


class Config(BaseModel):
    """Main configuration."""

    api: APIConfig = Field(default_factory=APIConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    default_mode: str = "synthesis"
    default_domain: str = "general"
    temperature: float = 0.7
    max_tokens_per_response: int = 1000
    synthesis_provider: Optional[str] = None
    synthesis_model: Optional[str] = None
    synthesis_max_tokens: Optional[int] = None
    custom_personas_path: Optional[str] = None
    custom_domains_path: Optional[str] = None
    presets: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """Manages loading and saving configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self._manager = SharedConfigManager(config_path, app_name="council-ai")
        self.path = self._manager.path
        self.config = self._manager.load(Config)

    def save(self) -> None:
        """Save configuration to file."""
        self._manager.save(self.config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key."""
        return self._manager.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key."""
        self._manager.set(key, value)


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration."""
    manager = ConfigManager(path)
    return manager.config


def save_config(config: Config, path: Optional[str] = None) -> None:
    """Save configuration."""
    manager = ConfigManager(path)
    manager.config = config
    manager.save()


def get_api_key(provider: str = "anthropic") -> Optional[str]:
    """Get API key for a provider from environment or config."""
    # Try provider-specific env var first
    provider_upper = provider.upper()
    env_key = sanitize_api_key(os.environ.get(f"{provider_upper}_API_KEY"))
    if env_key:
        return env_key

    # Special handling for Vercel AI Gateway (OpenAI-compatible)
    if provider == "openai" or provider == "vercel":
        gateway_key = sanitize_api_key(os.environ.get("AI_GATEWAY_API_KEY"))
        if gateway_key:
            return gateway_key

    # Try generic env var
    env_key = sanitize_api_key(os.environ.get("COUNCIL_API_KEY"))
    if env_key:
        return env_key

    # Try config file
    try:
        config = load_config()
        return sanitize_api_key(config.api.api_key)
    except Exception:
        return None


def get_available_providers() -> list[tuple[str, Optional[str]]]:
    """
    Get list of available providers with their API keys.

    Returns:
        List of (provider_name, api_key) tuples. api_key is None if not available.
        Includes all supported providers: openai, anthropic, gemini, vercel, and generic.
    """
    providers = []

    # Check standard providers
    for provider_name in ["openai", "anthropic", "gemini"]:
        key = get_api_key(provider_name)
        providers.append((provider_name, key))

    # Check Vercel AI Gateway (OpenAI-compatible)
    vercel_key = sanitize_api_key(os.environ.get("AI_GATEWAY_API_KEY"))
    if vercel_key and not is_placeholder_key(vercel_key):
        providers.append(("vercel", vercel_key))
    else:
        providers.append(("vercel", None))

    # Check generic COUNCIL_API_KEY (can work with any provider)
    generic_key = sanitize_api_key(os.environ.get("COUNCIL_API_KEY"))
    if generic_key and not is_placeholder_key(generic_key):
        providers.append(("generic", generic_key))
    else:
        providers.append(("generic", None))

    return providers


def get_best_available_provider() -> Optional[tuple[str, Optional[str]]]:
    """
    Get the best available provider based on availability and preferences.

    Priority order:
    1. Anthropic (if available)
    2. OpenAI (if available)
    3. Gemini (if available)
    4. Vercel AI Gateway (if available)
    5. Generic COUNCIL_API_KEY (if available)

    Returns:
        Tuple of (provider_name, api_key) or None if no providers available
    """
    providers = get_available_providers()

    # Priority order
    priority = ["anthropic", "openai", "gemini", "vercel", "generic"]

    for preferred in priority:
        for provider_name, api_key in providers:
            if provider_name == preferred and api_key:
                return (provider_name, api_key)

    return None


def get_tts_api_key(provider: str = "elevenlabs") -> Optional[str]:
    """Get API key for a TTS provider from environment or config."""
    # Try provider-specific env var first
    provider_upper = provider.upper()
    env_key = os.environ.get(f"{provider_upper}_API_KEY")
    if env_key:
        return env_key

    # Try config file
    try:
        config = load_config()
        if provider == config.tts.provider:
            return config.tts.api_key
        elif provider == config.tts.fallback_provider:
            return config.tts.fallback_api_key
    except Exception:
        pass

    return None
