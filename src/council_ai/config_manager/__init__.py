"""
Local Config Manager Implementation

This module provides a local implementation of config manager
that was originally planned to come from shared-ai-utils package.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, Type, TypeVar

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ConfigManager:
    """Manager for loading and saving configuration."""

    def __init__(self, config_path: Optional[str] = None, app_name: str = "app"):
        """Initialize config manager.

        Args:
            config_path: Optional explicit path to config file
            app_name: Application name for default config location
        """
        if config_path:
            self.path = Path(config_path)
        else:
            # Default to ~/.config/<app_name>/config.yaml
            config_dir = Path.home() / ".config" / app_name
            config_dir.mkdir(parents=True, exist_ok=True)
            self.path = config_dir / "config.yaml"

        self._config: Optional[BaseModel] = None

    def load(self, config_class: Type[T]) -> T:
        """Load configuration from file or create default.

        Args:
            config_class: Pydantic model class for configuration

        Returns:
            Configuration instance
        """
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    data = yaml.safe_load(f) or {}
                self._config = config_class(**data)
                logger.debug(f"Loaded config from {self.path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.path}: {e}, using defaults")
                self._config = config_class()
        else:
            logger.debug(f"Config file {self.path} not found, using defaults")
            self._config = config_class()

        return self._config

    def save(self, config: BaseModel) -> None:
        """Save configuration to file.

        Args:
            config: Configuration instance to save
        """
        self._config = config
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                # Convert to dict and write as YAML
                data = config.model_dump()
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            logger.debug(f"Saved config to {self.path}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.path}: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "api.provider")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self._config:
            return default

        try:
            value = self._config
            for part in key.split("."):
                value = getattr(value, part)
            return value
        except AttributeError:
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "api.provider")
            value: Value to set
        """
        if not self._config:
            raise ValueError("No configuration loaded")

        parts = key.split(".")
        obj = self._config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)


__all__ = ["ConfigManager"]
