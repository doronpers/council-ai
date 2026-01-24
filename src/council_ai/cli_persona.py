"""Backwards-compatible shim for old import path `council_ai.cli_persona`.

This module re-exports commonly used functions/classes expected by legacy tests
and external integrations that import `council_ai.cli_persona`.
"""

# Re-export persona command functions and core persona helpers for back-compat
from council_ai.cli.persona import *  # commands: persona, persona_list, persona_show, persona_create, persona_edit
from council_ai.core.persona import get_persona, PersonaManager, Persona

__all__ = [
    # CLI commands (from council_ai.cli.persona)
    "persona",
    "persona_list",
    "persona_show",
    "persona_create",
    "persona_edit",
    # Core helpers
    "get_persona",
    "PersonaManager",
    "Persona",
]
