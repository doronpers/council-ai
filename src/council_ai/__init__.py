"""
Council AI - Intelligent Advisory Council System

Get advice from a council of AI-powered personas with diverse perspectives.

Quick Start:
    >>> from council_ai import Council
    >>> council = Council.for_domain("business", api_key="your-key")
    >>> result = council.consult("Should we expand to Europe?")
    >>> print(result.synthesis)

Features:
    - 7 built-in expert personas
    - 12 domain presets
    - Multiple consultation modes
    - Full customization support
    - CLI and Python API
"""

__version__ = "1.0.0"
__author__ = "Doron Reizes"
__license__ = "MIT"

# Core classes
from .core.council import ConsultationMode, Council, CouncilConfig
from .core.persona import Persona, PersonaCategory, Trait, get_persona, list_personas
from .core.session import ConsultationResult, MemberResponse, Session

# Domain and provider utilities
from .domains import Domain, DomainCategory, get_domain, list_domains
from .providers import get_provider, list_providers

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
