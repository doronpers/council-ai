"""Configuration management for Council AI."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests  # type: ignore[import]
import yaml
from pydantic import BaseModel, Field

from ..utils.paths import get_config_path

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
    placeholder_substrings = ("paste-here", "enter-here", "your key", "your api key")

    if normalized in placeholder_exact:
        return True
    if normalized.startswith(placeholder_prefixes):
        return True
    if "your-" in normalized:
        return True
    if any(token in normalized for token in placeholder_substrings):
        return True
    if " here" in normalized:
        return True
    if normalized.endswith("here") and (
        normalized.startswith("your") or " " in normalized or "-" in normalized or "_" in normalized
    ):
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

    _env_loaded = False
    env_paths_to_try = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent.parent.parent / ".env",
        Path.home() / ".council-ai" / ".env",
    ]

    for env_path in env_paths_to_try:
        if env_path.exists():
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

            load_dotenv(env_path, override=has_placeholder)
            _env_loaded = True
            break
    if not _env_loaded:
        load_dotenv(override=False)
except ImportError:
    pass


class APIConfig(BaseModel):
    """API configuration."""

    provider: str = "anthropic"
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


class TTSConfig(BaseModel):
    """Text-to-Speech configuration."""

    enabled: bool = False
    provider: str = "elevenlabs"
    api_key: Optional[str] = None
    voice: Optional[str] = None
    model: Optional[str] = None
    fallback_provider: Optional[str] = "openai"
    fallback_api_key: Optional[str] = None
    fallback_voice: Optional[str] = None


class Config(BaseModel):
    """Main configuration."""

    api: APIConfig = Field(default_factory=APIConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    patterns_path: Optional[str] = None
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
    display: Dict[str, Any] = Field(default_factory=lambda: {"show_cost": False})


class ConfigManager:
    """Manages loading and saving configuration."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.path = Path(config_path)
        else:
            # Try to find a writable path for config
            # Priority: environment variable > workspace config > home config > current dir
            options = [
                os.environ.get("COUNCIL_CONFIG_PATH"),
                get_config_path("config.yaml", fallback_home=False),
                Path.home() / ".config" / "council-ai" / "config.yaml",  # Legacy fallback
                Path.cwd() / "config.yaml",
            ]
            for option in options:
                if not option:
                    continue
                path = Path(str(option))
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.path = path
                    break
                except OSError:
                    continue
            else:
                self.path = Path("config.yaml")

        self.config = self.load()

    def load(self) -> Config:
        """Load configuration from file with personal config support."""
        # Start with defaults
        default_config = Config()

        personal_data = self._load_personal_config()
        if personal_data:
            try:
                personal_config = Config(**personal_data)
                # Merge personal config into defaults
                default_config = self._merge_configs(default_config, personal_config)
            except Exception as e:
                logger.debug(f"Failed to parse personal config: {e}")

        # Load user config (highest priority, overrides personal)
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                user_config = Config(**data)
                # Merge user config over personal/default
                return self._merge_configs(default_config, user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.path}: {e}")
                return default_config

        return default_config

    def _load_personal_config(self) -> Optional[Dict]:
        """Load personal config from council-ai-personal if available."""
        try:
            from .personal_integration import PersonalIntegration

            integration = PersonalIntegration()
            repo_path = integration.detect_repo()
            if repo_path:
                personal_dir = repo_path / "personal" / "config"
                config_file = personal_dir / "config.yaml"
                if config_file.exists():
                    with open(config_file, encoding="utf-8") as f:
                        return yaml.safe_load(f) or {}
        except Exception as e:
            logger.debug(f"Could not load personal config: {e}")
        return None

    def _merge_configs(self, base: Config, override: Config) -> Config:
        """Merge two configs, with override taking precedence."""
        # Convert to dicts for easier merging
        base_dict = base.model_dump(exclude_none=True)
        override_dict = override.model_dump(exclude_none=True)

        # Deep merge
        merged = self._deep_merge(base_dict, override_dict)

        # Convert back to Config
        try:
            return Config(**merged)
        except Exception as e:
            logger.warning(f"Failed to merge configs: {e}")
            return base

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save(self, config: Optional[Config] = None) -> None:
        """Save configuration to file."""
        if config:
            self.config = config
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                )
        except OSError as e:
            logger.warning(f"Failed to save configuration to {self.path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key."""
        parts = key.split(".")
        value = self.config
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key."""
        parts = key.split(".")
        obj = self.config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict):
                if part not in obj:
                    obj[part] = {}
                obj = obj[part]
            else:
                raise KeyError(f"Invalid config path: {key}")

        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        elif isinstance(obj, dict):
            obj[final_key] = value
        else:
            raise KeyError(f"Invalid config key: {key}")


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration."""
    manager = ConfigManager(path)
    return manager.config


def save_config(config: Config, path: Optional[str] = None) -> None:
    """Save configuration."""
    manager = ConfigManager(path)
    manager.save(config)


def is_lmstudio_available() -> bool:
    """
    Check if LM Studio is running and accessible.

    Checks the configured base URL from config, or defaults to localhost:1234.

    Returns:
        True if LM Studio is running and responding, False otherwise
    """
    try:
        # Check if base_url is configured in config
        config = load_config()
        base_url = config.api.base_url

        # If base_url is configured, use it (it should already include /v1)
        if base_url:
            # Ensure we're checking the /models endpoint
            if base_url.endswith("/v1"):
                check_url = f"{base_url}/models"
            elif base_url.endswith("/v1/models"):
                check_url = base_url
            else:
                check_url = f"{base_url.rstrip('/')}/v1/models"
        else:
            # Default to localhost
            check_url = "http://localhost:1234/v1/models"

        response = requests.get(check_url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_api_key(provider: str = "anthropic") -> Optional[str]:
    """Get API key for a provider from environment or config."""
    provider_upper = provider.upper()
    env_key = sanitize_api_key(os.environ.get(f"{provider_upper}_API_KEY"))
    if env_key:
        return env_key

    if provider == "openai" or provider == "vercel":
        gateway_key = sanitize_api_key(os.environ.get("AI_GATEWAY_API_KEY"))
        if gateway_key:
            return gateway_key

    env_key = sanitize_api_key(os.environ.get("COUNCIL_API_KEY"))
    if env_key:
        return env_key

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
    provider_upper = provider.upper()
    env_key = os.environ.get(f"{provider_upper}_API_KEY")
    if env_key:
        return env_key

    try:
        config = load_config()
        if provider == config.tts.provider:
            return config.tts.api_key
        elif provider == config.tts.fallback_provider:
            return config.tts.fallback_api_key
    except Exception:
        pass
    return None
