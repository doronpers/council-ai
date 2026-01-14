"""
Domain Configurations - Pre-configured councils for specific use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


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
    optional_personas: List[str] = None
    recommended_mode: str = "synthesis"
    example_queries: List[str] = None

    def __post_init__(self):
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
        default_personas=["rams", "kahneman", "holman", "taleb"],
        optional_personas=["dempsey"],
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
        default_personas=["grove", "taleb", "dempsey", "kahneman"],
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
        default_personas=["grove", "taleb", "kahneman", "rams"],
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
        default_personas=["kahneman", "rams", "treasure", "grove"],
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
        default_personas=["dempsey", "kahneman", "grove"],
        optional_personas=["treasure"],
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
        default_personas=["treasure", "rams", "kahneman"],
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
        default_personas=["treasure", "kahneman", "rams"],
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
        default_personas=["grove", "kahneman", "dempsey", "taleb"],
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
        default_personas=["kahneman", "taleb", "dempsey"],
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
        default_personas=["dempsey", "holman", "taleb", "grove"],
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
        default_personas=["kahneman", "taleb", "rams"],
        example_queries=[
            "How should we approach this model?",
            "What biases might we have?",
            "Is this metric reliable?",
        ],
    ),
    "general": Domain(
        id="general",
        name="General Purpose",
        description="General consultation on any topic",
        category=DomainCategory.GENERAL,
        default_personas=["kahneman", "taleb", "grove", "rams"],
        example_queries=[
            "Help me think through this problem",
            "What am I missing here?",
            "What are the trade-offs?",
        ],
    ),
    "llm_review": Domain(
        id="llm_review",
        name="LLM Response Review",
        description="Supreme Court-style review of multiple LLM responses with scoring and synthesis",
        category=DomainCategory.TECHNICAL,
        default_personas=["dempsey", "kahneman", "rams", "treasure", "holman", "taleb", "grove"],
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
        description="Full 9-justice court for Sonotheia deepfake audio defense and voice authenticity topics",
        category=DomainCategory.TECHNICAL,
        default_personas=["dempsey", "kahneman", "rams", "treasure", "holman", "taleb", "grove", "signal_analyst", "compliance_auditor"],
        recommended_mode="synthesis",
        example_queries=[
            "Review responses about deepfake detection methods",
            "Evaluate explanations of voice biometrics",
            "Assess regulatory compliance guidance",
        ],
    ),
}


def get_domain(domain_id: str) -> Domain:
    """Get a domain by ID."""
    if domain_id not in DOMAINS:
        available = ", ".join(DOMAINS.keys())
        raise ValueError(f"Domain '{domain_id}' not found. Available: {available}")
    return DOMAINS[domain_id]


def list_domains(category: Optional[DomainCategory] = None) -> List[Domain]:
    """List all domains, optionally filtered by category."""
    domains = list(DOMAINS.values())
    if category:
        domains = [d for d in domains if d.category == category]
    return sorted(domains, key=lambda d: (d.category.value, d.name))
