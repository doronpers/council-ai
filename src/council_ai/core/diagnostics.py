"""
Diagnostic utilities for troubleshooting API keys and providers.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

from .config import get_api_key


def diagnose_api_keys() -> Dict[str, Any]:
    """
    Diagnose API key configuration and provide troubleshooting information.

    Returns:
        Dictionary with diagnostic information
    """
    diagnostics = {
        "available_keys": {},
        "missing_keys": [],
        "recommendations": [],
        "provider_status": {},
    }

    # Check each provider
    providers_to_check = ["openai", "anthropic", "gemini"]

    for provider in providers_to_check:
        key = get_api_key(provider)
        diagnostics["available_keys"][provider] = bool(key)

        if key:
            diagnostics["provider_status"][provider] = {
                "has_key": True,
                "key_length": len(key),
                "key_prefix": key[:8] + "..." if len(key) > 8 else "***",
            }
        else:
            diagnostics["missing_keys"].append(provider)
            diagnostics["provider_status"][provider] = {
                "has_key": False,
                "env_var": f"{provider.upper()}_API_KEY",
            }

    # Check Vercel AI Gateway
    vercel_key = os.environ.get("AI_GATEWAY_API_KEY")
    if vercel_key:
        diagnostics["available_keys"]["vercel"] = True
        diagnostics["provider_status"]["vercel"] = {
            "has_key": True,
            "key_length": len(vercel_key),
            "key_prefix": vercel_key[:8] + "..." if len(vercel_key) > 8 else "***",
            "note": "Vercel AI Gateway can be used with OpenAI provider",
        }
    else:
        diagnostics["provider_status"]["vercel"] = {
            "has_key": False,
            "env_var": "AI_GATEWAY_API_KEY",
        }

    # Check generic key
    generic_key = os.environ.get("COUNCIL_API_KEY")
    if generic_key:
        diagnostics["available_keys"]["generic"] = True
        diagnostics["provider_status"]["generic"] = {
            "has_key": True,
            "key_length": len(generic_key),
        }

    # Generate recommendations
    if not any(diagnostics["available_keys"].values()):
        diagnostics["recommendations"].append(
            "No API keys found. Please set at least one of: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, or AI_GATEWAY_API_KEY"
        )
    else:
        available = [p for p, has_key in diagnostics["available_keys"].items() if has_key]
        diagnostics["recommendations"].append(
            f"Available providers: {', '.join(available)}. "
            f"Council AI will use these with automatic fallback."
        )

    # OpenAI-specific troubleshooting
    if diagnostics["available_keys"].get("openai") or vercel_key:
        diagnostics["recommendations"].append(
            "OpenAI/Vercel: If authentication fails, check: "
            "1) Key is valid and not expired, 2) Key has proper permissions, "
            "3) For Vercel, ensure VERCEL_AI_GATEWAY_URL is set if using custom endpoint"
        )

    return diagnostics


def test_api_key(provider: str, api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Test if an API key works for a provider.

    Args:
        provider: Provider name
        api_key: API key to test (uses get_api_key if None)

    Returns:
        Tuple of (success: bool, message: str)
    """
    if api_key is None:
        api_key = get_api_key(provider)

    if not api_key:
        return False, f"No API key found for {provider}"

    try:
        from ..providers import get_provider

        # Try to create provider instance (this validates the key format)
        get_provider(provider, api_key=api_key)

        # Basic validation - key should not be empty
        if len(api_key.strip()) < 10:
            return False, f"API key for {provider} appears too short (may be invalid)"

        return True, f"API key for {provider} appears valid (format check passed)"
    except ValueError as e:
        return False, f"API key validation failed: {str(e)}"
    except ImportError as e:
        return False, f"Provider package not installed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error testing {provider}: {str(e)}"
