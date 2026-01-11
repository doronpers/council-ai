"""
Configuration Management
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class APIConfig(BaseModel):
    """API configuration."""
    provider: str = "anthropic"
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


class Config(BaseModel):
    """Main configuration."""
    api: APIConfig = Field(default_factory=APIConfig)
    default_mode: str = "synthesis"
    default_domain: str = "general"
    temperature: float = 0.7
    max_tokens_per_response: int = 1000
    custom_personas_path: Optional[str] = None
    custom_domains_path: Optional[str] = None
    presets: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """Manages loading and saving configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.path = Path(config_path)
        else:
            config_dir = Path.home() / ".config" / "council-ai"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.path = config_dir / "config.yaml"
        
        self.config = self._load()
    
    def _load(self) -> Config:
        """Load configuration from file."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = yaml.safe_load(f) or {}
                return Config(**data)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.path}: {e}")
                return Config()
        return Config()
    
    def save(self) -> None:
        """Save configuration to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            yaml.dump(
                self.config.model_dump(exclude_none=True),
                f,
                default_flow_style=False,
                sort_keys=False,
            )
    
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
    manager.config = config
    manager.save()


def get_api_key(provider: str = "anthropic") -> Optional[str]:
    """Get API key for a provider from environment or config."""
    # Try provider-specific env var
    env_key = os.environ.get(f"{provider.upper()}_API_KEY")
    if env_key:
        return env_key
    
    # Try generic env var
    env_key = os.environ.get("COUNCIL_API_KEY")
    if env_key:
        return env_key
    
    # Try config file
    try:
        config = load_config()
        return config.api.api_key
    except Exception:
        return None
