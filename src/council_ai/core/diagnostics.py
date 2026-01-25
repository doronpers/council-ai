"""Diagnostic utilities for troubleshooting API keys and providers."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

from .config import get_api_key, is_placeholder_key, load_config, sanitize_api_key


def diagnose_api_keys() -> Dict[str, Any]:
    """
    Diagnose API key configuration and provide troubleshooting information.

    Returns:
        Dictionary with diagnostic information including all available providers
    """
    diagnostics: Dict[str, Any] = {
        "available_keys": {},
        "missing_keys": [],
        "recommendations": [],
        "provider_status": {},
        "best_provider": None,
    }

    # Check all providers including vercel, generic, and local LM Studio
    providers_to_check = ["openai", "anthropic", "gemini", "lmstudio", "vercel", "generic"]

    try:
        config = load_config()
        config_api_key = config.api.api_key
    except Exception:
        config_api_key = None

    for provider in providers_to_check:
        placeholder_sources: list[str] = []
        if provider == "vercel":
            raw_gateway_key = os.environ.get("AI_GATEWAY_API_KEY")
            if raw_gateway_key and is_placeholder_key(raw_gateway_key):
                placeholder_sources.append("AI_GATEWAY_API_KEY")
            key = sanitize_api_key(raw_gateway_key)
            env_var = "AI_GATEWAY_API_KEY"
        elif provider == "generic":
            raw_generic_key = os.environ.get("COUNCIL_API_KEY")
            if raw_generic_key and is_placeholder_key(raw_generic_key):
                placeholder_sources.append("COUNCIL_API_KEY")
            key = sanitize_api_key(raw_generic_key)
            env_var = "COUNCIL_API_KEY"
        else:
            raw_provider_key = os.environ.get(f"{provider.upper()}_API_KEY")
            if raw_provider_key and is_placeholder_key(raw_provider_key):
                placeholder_sources.append(f"{provider.upper()}_API_KEY")
            if provider in {"openai", "vercel"}:
                raw_gateway_key = os.environ.get("AI_GATEWAY_API_KEY")
                if raw_gateway_key and is_placeholder_key(raw_gateway_key):
                    placeholder_sources.append("AI_GATEWAY_API_KEY")
            raw_generic_key = os.environ.get("COUNCIL_API_KEY")
            if raw_generic_key and is_placeholder_key(raw_generic_key):
                placeholder_sources.append("COUNCIL_API_KEY")
            if config_api_key and is_placeholder_key(config_api_key):
                placeholder_sources.append("config.api.api_key")
            key = get_api_key(provider)
            env_var = f"{provider.upper()}_API_KEY"
            key = get_api_key(provider)

        if provider == "lmstudio":
            from .config import is_lmstudio_available

            has_valid_key = is_lmstudio_available()
            key = "lm-studio" if has_valid_key else None
        else:
            has_valid_key = bool(key)

        diagnostics["available_keys"][provider] = has_valid_key

        if has_valid_key and key:
            diagnostics["provider_status"][provider] = {
                "has_key": True,
                "key_length": len(key) if key else 0,
                "key_prefix": key[:8] + "..." if key and len(key) > 8 else "***",
                "env_var": env_var if provider != "lmstudio" else "Local Server",
            }
        else:
            if placeholder_sources:
                diagnostics["missing_keys"].append(provider)
                diagnostics["provider_status"][provider] = {
                    "has_key": False,
                    "env_var": env_var,
                    "note": "Placeholder API key detected - please replace with real key",
                    "placeholder_sources": placeholder_sources,
                }
            else:
                diagnostics["missing_keys"].append(provider)
                diagnostics["provider_status"][provider] = {
                    "has_key": False,
                    "env_var": env_var,
                }

    # Determine best provider
    from .config import get_best_available_provider

    best = get_best_available_provider()
    if best:
        diagnostics["best_provider"] = {
            "name": best[0],
            "has_key": True,
        }

    # Generate recommendations
    available_providers = [p for p, has_key in diagnostics["available_keys"].items() if has_key]

    if not available_providers:
        diagnostics["recommendations"].append(
            "No API keys found. Please set at least one of: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, AI_GATEWAY_API_KEY, or COUNCIL_API_KEY"
        )
        diagnostics["recommendations"].append(
            "You can get API keys from:\n"
            "  • Anthropic: https://console.anthropic.com/\n"
            "  • OpenAI: https://platform.openai.com/api-keys\n"
            "  • Gemini: https://ai.google.dev/"
        )
    else:
        diagnostics["recommendations"].append(
            f"Found {len(available_providers)} available provider(s): {', '.join(available_providers)}"
        )
        if best:
            diagnostics["recommendations"].append(
                f"Recommended provider: {best[0]} (will be used as default with automatic fallback)"
            )
        diagnostics["recommendations"].append(
            "Council AI will automatically use available providers with fallback if one fails."
        )

    # TTS checks
    if os.environ.get("ELEVENLABS_API_KEY"):
        diagnostics["available_keys"]["elevenlabs"] = True
        diagnostics["provider_status"]["elevenlabs"] = {"has_key": True}

    if os.environ.get("OPENAI_API_KEY"):
        # OpenAI key serves both LLM and TTS
        pass

    return diagnostics


def test_api_key(provider: str, api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Test if an API key is valid for a given provider.

    Args:
        provider: The provider to test (openai, anthropic, gemini)
        api_key: Optional API key to test. If not provided, uses environment variable.

    Returns:
        Tuple of (success, message)
    """
    # Get API key from parameter or environment
    key = api_key or get_api_key(provider)

    if not key:
        return False, f"No API key found for {provider}"

    if is_placeholder_key(key):
        return False, f"Placeholder API key detected for {provider}"

    # Basic format validation
    if len(key) < 10:
        return False, f"API key for {provider} appears too short"

    # Provider-specific validation
    if provider == "openai":
        if not key.startswith("sk-"):
            return False, "OpenAI API key should start with 'sk-'"
        return True, "API key is valid (format check passed)"

    elif provider == "anthropic":
        if not key.startswith("sk-ant-"):
            return False, "Anthropic API key should start with 'sk-ant-'"
        return True, "API key is valid (format check passed)"

    elif provider == "gemini":
        # Gemini keys don't have a specific prefix
        if len(key) < 20:
            return False, "Gemini API key appears too short"
        return True, "API key is valid (format check passed)"

    else:
        # Generic validation for unknown providers
        return True, f"API key is valid for {provider} (basic check passed)"


async def check_provider_connectivity(provider: str) -> Tuple[bool, str, float]:
    """
    Test actual connectivity to a provider by generating a minimal response.

    Returns:
        Tuple of (success, message, latency_ms)
    """
    import time

    if provider == "lmstudio":
        from .config import is_lmstudio_available

        if not is_lmstudio_available():
            return False, "LM Studio not detected at http://localhost:1234", 0.0
    elif not get_api_key(provider):
        return False, f"No API key for {provider}", 0.0

    try:
        start_time = time.time()

        # Use the provider factory directly for a lighter test
        from ..providers import get_provider

        # Pass api_key as keyword argument if required by factory
        llm = get_provider(provider, api_key=get_api_key(provider))

        # Simple ping
        response = await llm.complete(
            system_prompt="", user_prompt="Ping. Reply with 'Pong'.", max_tokens=10
        )

        latency = (time.time() - start_time) * 1000
        content = response.text.strip() if response.text else ""

        if content:
            return True, f"Success: {content[:20]}...", latency
        else:
            return False, "Empty response received", latency

    except Exception as e:
        return False, str(e), 0.0


def check_tts_connectivity() -> Dict[str, Any]:
    """Check availability of configured TTS providers."""
    results = {}

    # ElevenLabs
    if os.environ.get("ELEVENLABS_API_KEY"):
        # We won't generate audio to save credits, just check if we can list voices
        try:
            import httpx  # type: ignore

            key = os.environ.get("ELEVENLABS_API_KEY")
            resp = httpx.get(
                "https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": key}, timeout=5
            )
            if resp.status_code == 200:
                results["elevenlabs"] = {"ok": True, "msg": "Connected (Voice list accessible)"}
            else:
                results["elevenlabs"] = {"ok": False, "msg": f"http {resp.status_code}"}
        except Exception as e:
            results["elevenlabs"] = {"ok": False, "msg": str(e)}

    return results
