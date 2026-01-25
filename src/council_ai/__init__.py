"""
Council AI - Intelligent Advisory Council System

Get advice from a council of AI-powered personas with diverse perspectives.

Quick Start:
    >>> from council_ai import Council
    >>> council = Council.for_domain("business", api_key="your-key")
    >>> result = council.consult("Should we expand to Europe?")
    >>> print(result.synthesis)

Features:
    - 9 built-in expert personas
    - 14 domain presets
    - Multiple consultation modes
    - Full customization support
    - CLI and Python API

API Keys:
    Council AI automatically loads API keys from:
    1. .env file in project root (recommended)
    2. Environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
    3. Config file (workspace: .workspace-config/council-ai/config.yaml or legacy: ~/.config/council-ai/config.yaml)
    4. CLI flags (--api-key)
"""

__version__ = "2.0.0"
__author__ = "Doron Reizes"
__license__ = "MIT"

# Import config module to trigger .env loading
from .core import config  # noqa: F401

# Core classes
from .core.council import ConsultationMode, Council, CouncilConfig
from .core.persona import Persona, PersonaCategory, Trait, get_persona, list_personas
from .core.session import ConsultationResult, MemberResponse, Session

# Domain and provider utilities
from .domains import Domain, DomainCategory, get_domain, list_domains
from .providers import get_provider, list_providers

# Context loading utilities (optional import)
try:
    from .utils.context import (  # noqa: F401
        load_code_files,
        load_context_from_files,
        load_images,
        load_markdown_files,
        load_text_files,
    )

    _utils_available = True
except ImportError:
    _utils_available = False

__all__ = [
    # Main classes
    "Council",
    "ConsultationMode",
    "CouncilConfig",
    # Persona management
    "Persona",
    "PersonaCategory",
    "Trait",
    "get_persona",
    "list_personas",
    # Results and sessions
    "ConsultationResult",
    "MemberResponse",
    "Session",
    # Domains
    "Domain",
    "DomainCategory",
    "get_domain",
    "list_domains",
    # Providers
    "get_provider",
    "list_providers",
]

# Add context utilities to __all__ if available
if _utils_available:
    __all__.extend(
        [
            "load_markdown_files",
            "load_code_files",
            "load_text_files",
            "load_images",
            "load_context_from_files",
        ]
    )
