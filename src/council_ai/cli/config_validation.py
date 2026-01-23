"""
Configuration validation utilities for CLI

Validates configuration settings and provides helpful guidance
"""

import os
from typing import Dict, List, Optional, Tuple

from rich.console import Console

console = Console()


class ConfigValidator:
    """Validates Council AI configuration"""

    # Valid configuration keys and their types
    VALID_KEYS: Dict[str, type] = {
        # API settings
        "api.provider": str,
        "api.api_key": str,
        "api.model": str,
        "api.base_url": str,
        # Defaults
        "default_domain": str,
        "default_mode": str,
        "temperature": float,
        "max_tokens_per_response": int,
        # Synthesis
        "synthesis_provider": str,
        "synthesis_model": str,
        "synthesis_max_tokens": int,
        # Paths
        "custom_personas_path": str,
        "custom_domains_path": str,
    }

    VALID_PROVIDERS = ["openai", "anthropic", "google", "groq", "huggingface"]
    VALID_MODES = ["individual", "synthesis", "reasoning"]
    VALID_DOMAINS = ["general", "business", "technical", "creative"]

    @staticmethod
    def validate_key(key: str) -> Optional[str]:
        """
        Validate configuration key.
        Returns error message if invalid, None if valid.
        """
        if key not in ConfigValidator.VALID_KEYS:
            valid_keys_str = "\n  ".join(sorted(ConfigValidator.VALID_KEYS.keys()))
            return f"Invalid configuration key: {key}\n\n" f"Valid keys:\n  {valid_keys_str}"
        return None

    @staticmethod
    def validate_value(key: str, value) -> Optional[str]:
        """
        Validate configuration value.
        Returns error message if invalid, None if valid.
        """
        # Type check
        expected_type = ConfigValidator.VALID_KEYS.get(key)
        if expected_type and not isinstance(value, expected_type):
            return f"Invalid value type for {key}: expected {expected_type.__name__}, got {type(value).__name__}"

        # Provider validation
        if key == "api.provider" and value not in ConfigValidator.VALID_PROVIDERS:
            return (
                f"Invalid provider: {value}\n"
                f"Valid providers: {', '.join(ConfigValidator.VALID_PROVIDERS)}"
            )

        # Mode validation
        if key == "default_mode" and value not in ConfigValidator.VALID_MODES:
            return (
                f"Invalid mode: {value}\n" f"Valid modes: {', '.join(ConfigValidator.VALID_MODES)}"
            )

        # Domain validation
        if key == "default_domain" and value not in ConfigValidator.VALID_DOMAINS:
            return (
                f"Invalid domain: {value}\n"
                f"Valid domains: {', '.join(ConfigValidator.VALID_DOMAINS)}"
            )

        # API key format validation
        if key == "api.api_key":
            if not value or len(value) < 10:
                return "API key must be at least 10 characters long"
            if value.lower() in ("your-api-key-here", "placeholder", "xxx"):
                return "Please enter your actual API key, not a placeholder"

        # Temperature range validation
        if key == "temperature":
            if not 0 <= value <= 2:
                return "Temperature must be between 0 and 2"

        # Token limit validation
        if "max_tokens" in key:
            if value < 100 or value > 4000:
                return f"{key} must be between 100 and 4000"

        return None

    @staticmethod
    def suggest_fixes(error_message: str, key: str) -> str:
        """Suggest fixes for common configuration errors"""
        suggestions = {
            "Invalid provider": (
                "To set a provider:\n"
                "  council config set api.provider openai\n"
                "  council config set api.provider anthropic\n"
                "Tip: Use 'council doctor' to check available providers"
            ),
            "Invalid mode": (
                "To set consultation mode:\n"
                "  council config set default_mode synthesis\n"
                "  council config set default_mode individual\n"
                "  council config set default_mode reasoning"
            ),
            "API key": (
                "To set your API key:\n"
                "  council config set api.api_key YOUR_ACTUAL_KEY\n"
                "  Or use environment variable: export {provider}_API_KEY=YOUR_KEY\n"
                "Tip: Run 'council doctor' to verify your API key is recognized"
            ),
            "Invalid domain": (
                "To set default domain:\n"
                "  council config set default_domain business\n"
                "  council config set default_domain technical\n"
                "  council config set default_domain creative"
            ),
        }

        for error_type, suggestion in suggestions.items():
            if error_type in error_message:
                return suggestion

        return "Run 'council config show' to see all settings"


def validate_configuration(config_dict: Dict[str, any]) -> Tuple[bool, List[str]]:
    """
    Validate entire configuration dictionary.
    Returns (is_valid, list_of_error_messages)
    """
    errors = []

    for key, value in config_dict.items():
        # Skip internal keys
        if key.startswith("_"):
            continue

        # Validate key
        key_error = ConfigValidator.validate_key(key)
        if key_error:
            errors.append(key_error)
            continue

        # Validate value
        value_error = ConfigValidator.validate_value(key, value)
        if value_error:
            errors.append(f"{key}: {value_error}")

    return len(errors) == 0, errors


def display_config_warning(key: str, value: any, warning: str) -> None:
    """Display configuration warning to user"""
    console.print(f"[yellow]⚠️  Configuration Warning[/yellow]")
    console.print(f"  Key: {key}")
    console.print(f"  Value: {value}")
    console.print(f"  Issue: {warning}")


def display_config_validation_result(is_valid: bool, errors: List[str]) -> None:
    """Display configuration validation results"""
    if is_valid:
        console.print("[green]✓[/green] Configuration is valid")
    else:
        console.print("[red]✗[/red] Configuration has errors:")
        for error in errors:
            console.print(f"  • {error}")
        console.print("\nRun 'council config show' to view current configuration")


def check_required_api_key(provider: str) -> bool:
    """Check if API key is configured for provider"""
    from ..core.config import ConfigManager

    config_manager = ConfigManager()

    # Check config
    api_key = config_manager.get("api.api_key")
    if api_key:
        return True

    # Check environment
    env_var = f"{provider.upper()}_API_KEY"
    if os.getenv(env_var):
        return True

    return False


def suggest_next_steps() -> None:
    """Suggest next steps after configuration"""
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Verify API key: council doctor")
    console.print("  2. Try consultation: council consult 'Your query'")
    console.print("  3. Explore interactive mode: council interactive")
    console.print("  4. View help: council --help")
