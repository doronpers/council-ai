"""Domain Configurations - Pre-configured councils for specific use cases."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DomainCategory(str, Enum):
    """Categories for organizing domains."""

    TECHNICAL = "technical"
    BUSINESS = "business"
    CREATIVE = "creative"
    PERSONAL = "personal"
    GENERAL = "general"


@dataclass
class Domain:
    """A domain configuration with recommended personas."""

    id: str
    name: str
    description: str
    category: DomainCategory
    default_personas: List[str]
    optional_personas: Optional[List[str]] = None
    recommended_mode: str = "synthesis"
    example_queries: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize default lists."""
        if self.optional_personas is None:
            self.optional_personas = []
        if self.example_queries is None:
            self.example_queries = []


# Built-in domain configurations
DOMAINS: Dict[str, Domain] = {
    "coding": Domain(
        id="coding",
        name="Software Development",
        description="Code review, architecture, and development decisions",
        category=DomainCategory.TECHNICAL,
        default_personas=["DR", "DK", "PH", "NT"],
        optional_personas=["MD"],
        example_queries=[
            "Review this API design",
            "Should we refactor this module?",
            "What's the security risk here?",
        ],
    ),
    "business": Domain(
        id="business",
        name="Business Strategy",
        description="Strategic business decisions and planning",
        category=DomainCategory.BUSINESS,
        default_personas=["AG", "NT", "MD", "DK"],
        example_queries=[
            "Should we enter the European market?",
            "What's our biggest competitive risk?",
            "How should we prioritize Q1?",
        ],
    ),
    "startup": Domain(
        id="startup",
        name="Startup Decisions",
        description="Early-stage startup strategy and pivots",
        category=DomainCategory.BUSINESS,
        default_personas=["AG", "NT", "DK", "DR"],
        example_queries=[
            "Should we pivot from B2C to B2B?",
            "Is this the right time to raise funding?",
            "Should we hire a sales team now?",
        ],
    ),
    "product": Domain(
        id="product",
        name="Product Management",
        description="Product decisions and roadmap planning",
        category=DomainCategory.BUSINESS,
        default_personas=["DK", "DR", "JT", "AG"],
        example_queries=[
            "Which feature should we build next?",
            "Should we add social features?",
            "How do we improve onboarding?",
        ],
    ),
    "leadership": Domain(
        id="leadership",
        name="Leadership & Management",
        description="Team leadership and organizational decisions",
        category=DomainCategory.BUSINESS,
        default_personas=["MD", "DK", "AG"],
        optional_personas=["JT"],
        example_queries=[
            "How should we structure the team?",
            "Should we go remote-first?",
            "How do we improve team morale?",
        ],
    ),
    "creative": Domain(
        id="creative",
        name="Creative Projects",
        description="Creative work, design, and artistic decisions",
        category=DomainCategory.CREATIVE,
        default_personas=["JT", "DR", "DK"],
        example_queries=[
            "What style should this video use?",
            "How do we make this more engaging?",
            "Should we simplify or add detail?",
        ],
    ),
    "writing": Domain(
        id="writing",
        name="Writing & Content",
        description="Written content creation and editing",
        category=DomainCategory.CREATIVE,
        default_personas=["JT", "DK", "DR"],
        example_queries=[
            "How should I structure this article?",
            "Is this clear enough?",
            "What's missing from this draft?",
        ],
    ),
    "career": Domain(
        id="career",
        name="Career Decisions",
        description="Career moves and professional development",
        category=DomainCategory.PERSONAL,
        default_personas=["AG", "DK", "MD", "NT"],
        example_queries=[
            "Should I take this job offer?",
            "Is this the right time to switch careers?",
            "How should I negotiate this offer?",
        ],
    ),
    "decisions": Domain(
        id="decisions",
        name="Major Life Decisions",
        description="Important personal and life decisions",
        category=DomainCategory.PERSONAL,
        default_personas=["DK", "NT", "MD"],
        example_queries=[
            "Should we buy or rent?",
            "Is this the right time for a major change?",
            "How should we think about this risk?",
        ],
    ),
    "devops": Domain(
        id="devops",
        name="DevOps & Infrastructure",
        description="Infrastructure, deployment, and operations",
        category=DomainCategory.TECHNICAL,
        default_personas=["MD", "PH", "NT", "AG"],
        example_queries=[
            "How should we structure our deployment pipeline?",
            "What are the security risks in this setup?",
            "Should we migrate to Kubernetes?",
        ],
    ),
    "data": Domain(
        id="data",
        name="Data Science & Analytics",
        description="Data analysis and machine learning decisions",
        category=DomainCategory.TECHNICAL,
        default_personas=["DK", "NT", "DR"],
        example_queries=[
            "How should we approach this model?",
            "What biases might we have?",
            "Is this metric reliable?",
        ],
    ),
    "general": Domain(
        id="general",
        name="General Purpose",
        description="General consultation on any topic with all council members",
        category=DomainCategory.GENERAL,
        default_personas=["MD", "DK", "DR", "JT", "PH", "NT", "AG"],
        example_queries=[
            "Help me think through this problem",
            "What am I missing here?",
            "What are the trade-offs?",
        ],
    ),
    "llm_review": Domain(
        id="llm_review",
        name="LLM Response Review",
        description=(
            "Supreme Court-style review of multiple LLM responses with scoring and synthesis. "
            "See documentation/REVIEWER_SETUP.md for setup and usage."
        ),
        category=DomainCategory.TECHNICAL,
        default_personas=["MD", "DK", "DR", "JT", "PH", "NT", "AG"],
        optional_personas=["signal_analyst", "compliance_auditor"],
        recommended_mode="synthesis",
        example_queries=[
            "Review these 3 responses about API security",
            "Which response best explains the concept?",
            "Evaluate accuracy and completeness of these answers",
        ],
    ),
    "sonotheia": Domain(
        id="sonotheia",
        name="Sonotheia Review",
        description=(
            "Full 9-justice court for Sonotheia deepfake audio defense "
            "and voice authenticity topics"
        ),
        category=DomainCategory.TECHNICAL,
        default_personas=[
            "MD",
            "DK",
            "DR",
            "JT",
            "PH",
            "NT",
            "AG",
            "signal_analyst",
            "compliance_auditor",
            "fraud_examiner",
        ],
        recommended_mode="synthesis",
        example_queries=[
            "Review this SAR narrative for completeness",
            "Assess voice fraud detection methodology",
            "Evaluate regulatory compliance framework",
            "Review responses about deepfake detection methods",
            "Evaluate explanations of voice biometrics",
        ],
    ),
    "audio_post": Domain(
        id="audio_post",
        name="Audio Post-Production",
        description="Dialogue editing, ADR, sound design, and re-recording mixing for film/TV",
        category=DomainCategory.CREATIVE,
        default_personas=[
            "dialogue_editor",
            "rerecording_mixer",
            "sound_designer",
            "adr_supervisor",
        ],
        recommended_mode="synthesis",
        example_queries=[
            "Evaluate this dialogue edit approach",
            "Should we ADR this line?",
            "Review this Atmos panning strategy",
            "Assess this noise floor management",
        ],
    ),
}


def _load_personal_domains() -> Dict[str, Domain]:
    """Load personal domains from council-ai-personal if available."""
    personal_domains = {}
    try:
        from council_ai.core.personal_integration import detect_personal_repo

        repo_path = detect_personal_repo()
        if repo_path:
            personal_dir = repo_path / "personal" / "config"
            domains_file = personal_dir / "domains.yaml"
            if domains_file.exists():
                import yaml

                with open(domains_file, encoding="utf-8") as f:
                    domains_data = yaml.safe_load(f) or {}
                    for domain_id, domain_data in domains_data.items():
                        try:
                            domain = Domain(
                                id=domain_id,
                                name=domain_data.get("name", domain_id),
                                description=domain_data.get("description", ""),
                                category=DomainCategory(domain_data.get("category", "general")),
                                default_personas=domain_data.get("default_personas", []),
                                optional_personas=domain_data.get("optional_personas"),
                                recommended_mode=domain_data.get("recommended_mode", "synthesis"),
                                example_queries=domain_data.get("example_queries"),
                            )
                            personal_domains[domain_id] = domain
                        except Exception as e:
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.warning(f"Failed to load personal domain {domain_id}: {e}")
    except Exception:
        pass
    return personal_domains


def get_domain(domain_id: str) -> Domain:
    """Get a domain by ID, checking personal domains first."""
    # Check personal domains first (they can override built-ins)
    personal_domains = _load_personal_domains()
    if domain_id in personal_domains:
        return personal_domains[domain_id]

    # Check built-in domains
    if domain_id not in DOMAINS:
        available = ", ".join(list(DOMAINS.keys()) + list(personal_domains.keys()))
        raise ValueError(f"Domain '{domain_id}' not found. Available: {available}")
    return DOMAINS[domain_id]


def list_domains(category: Optional[DomainCategory] = None) -> List[Domain]:
    """List all domains, optionally filtered by category, including personal domains."""
    # Start with built-in domains
    all_domains = dict(DOMAINS)

    # Add personal domains (they can override built-ins)
    personal_domains = _load_personal_domains()
    all_domains.update(personal_domains)

    domains = list(all_domains.values())
    if category:
        domains = [d for d in domains if d.category == category]
    return sorted(domains, key=lambda d: (d.category.value, d.name))
