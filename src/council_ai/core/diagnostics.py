"""
Diagnostic utilities for troubleshooting API keys and providers.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

from .config import get_api_key, is_placeholder_key, sanitize_api_key


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
    vercel_key = sanitize_api_key(os.environ.get("AI_GATEWAY_API_KEY"))
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
        if is_placeholder_key(os.environ.get("AI_GATEWAY_API_KEY", "")):
            diagnostics["provider_status"]["vercel"]["note"] = "Placeholder API key detected"

    # Check generic key
    generic_key = sanitize_api_key(os.environ.get("COUNCIL_API_KEY"))
    if generic_key:
        diagnostics["available_keys"]["generic"] = True
        diagnostics["provider_status"]["generic"] = {
            "has_key": True,
            "key_length": len(generic_key),
        }
    elif is_placeholder_key(os.environ.get("COUNCIL_API_KEY", "")):
        diagnostics["provider_status"]["generic"] = {
            "has_key": False,
            "env_var": "COUNCIL_API_KEY",
            "note": "Placeholder API key detected",
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

    # TTS checks
    if os.environ.get("ELEVENLABS_API_KEY"):
        diagnostics["available_keys"]["elevenlabs"] = True
        diagnostics["provider_status"]["elevenlabs"] = {"has_key": True}
    
    if os.environ.get("OPENAI_API_KEY"):
         # OpenAI key serves both LLM and TTS
         pass

    return diagnostics


async def check_provider_connectivity(provider: str) -> Tuple[bool, str, float]:
    """
    Test actual connectivity to a provider by generating a minimal response.
    
    Returns:
        Tuple of (success, message, latency_ms)
    """
    import time
    from ..core.council import Council
    
    if not get_api_key(provider):
         return False, f"No API key for {provider}", 0.0

    try:
        start_time = time.time()
        # Initialize council with just one member to minimize token usage
        # We use a throwaway instance
        council = Council(provider=provider, model="default") 
        # But Council usually needs a persona. 
        # Let's try to instantiate the provider directly to avoid overhead?
        # Actually, best to test the full stack including Council class if possible,
        # but Council requires personas.
        
        # Let's use the provider factory directly for a lighter test
        from ..providers import get_provider
        llm = get_provider(provider, get_api_key(provider))
        
        # Simple ping
        response = await llm.generate_response(
            messages=[{"role": "user", "content": "Ping. Reply with 'Pong'."}],
            model=None # Use default
        )
        
        latency = (time.time() - start_time) * 1000
        content = response.content.strip() if response.content else ""
        
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
             import requests
             key = os.environ.get("ELEVENLABS_API_KEY")
             resp = requests.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": key}, timeout=5)
             if resp.status_code == 200:
                 results["elevenlabs"] = {"ok": True, "msg": "Connected (Voice list accessible)"}
             else:
                 results["elevenlabs"] = {"ok": False, "msg": f"http {resp.status_code}"}
        except Exception as e:
             results["elevenlabs"] = {"ok": False, "msg": str(e)}
    
    return results
