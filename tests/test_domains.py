"""Tests for domain management."""

import pytest

from council_ai import DomainCategory, get_domain, list_domains


def test_all_domains_exist():
    """Test that all expected domains exist."""
    domains = list_domains()
    assert len(domains) == 15, f"Expected 15 domains, got {len(domains)}"

    expected_ids = [
        "coding",
        "business",
        "startup",
        "product",
        "leadership",
        "creative",
        "writing",
        "audio_post",
        "career",
        "decisions",
        "devops",
        "data",
        "general",
        "llm_review",
        "sonotheia",
    ]

    domain_ids = [d.id for d in domains]
    for expected in expected_ids:
        assert expected in domain_ids, f"Domain '{expected}' not found"


def test_domain_structure():
    """Test that domains have required fields."""
    domains = list_domains()

    for domain in domains:
        assert domain.id
        assert domain.name
        assert domain.description
        assert isinstance(domain.category, DomainCategory)
        assert len(domain.default_personas) > 0
        assert domain.recommended_mode in [
            "individual",
            "synthesis",
            "sequential",
            "debate",
            "vote",
        ]


def test_specific_domains():
    """Test specific domain configurations."""
    # Business domain
    business = get_domain("business")
    assert business.name == "Business Strategy"
    assert business.category == DomainCategory.BUSINESS
    assert "AG" in business.default_personas
    assert "NT" in business.default_personas
    assert len(business.example_queries) > 0

    # Coding domain
    coding = get_domain("coding")
    assert coding.name == "Software Development"
    assert coding.category == DomainCategory.TECHNICAL
    assert "DR" in coding.default_personas
    assert "PH" in coding.default_personas

    # Career domain
    career = get_domain("career")
    assert career.category == DomainCategory.PERSONAL
    assert len(career.default_personas) > 0


def test_domain_personas_exist():
    """Test that all personas referenced in domains actually exist."""
    from council_ai import get_persona

    domains = list_domains()

    for domain in domains:
        for persona_id in domain.default_personas:
            try:
                persona = get_persona(persona_id)
                assert (
                    persona is not None
                ), f"Persona '{persona_id}' in domain '{domain.id}' not found"
            except ValueError:
                pytest.fail(f"Persona '{persona_id}' in domain '{domain.id}' does not exist")


def test_domain_categories():
    """Test domain category filtering."""
    technical = list_domains(DomainCategory.TECHNICAL)
    business = list_domains(DomainCategory.BUSINESS)
    personal = list_domains(DomainCategory.PERSONAL)

    assert len(technical) > 0
    assert len(business) > 0
    assert len(personal) > 0

    for d in technical:
        assert d.category == DomainCategory.TECHNICAL

    for d in business:
        assert d.category == DomainCategory.BUSINESS


def test_get_nonexistent_domain():
    """Test error handling for nonexistent domain."""
    with pytest.raises(ValueError, match="not found"):
        get_domain("nonexistent_domain")


def test_domain_example_queries():
    """Test that domains have example queries."""
    domains = list_domains()

    for domain in domains:
        assert (
            len(domain.example_queries) >= 3
        ), f"Domain '{domain.id}' should have at least 3 example queries"

        for query in domain.example_queries:
            assert len(query) > 10, f"Query in domain '{domain.id}' too short: {query}"


def test_business_domains():
    """Test business-related domains."""
    business_domains = ["business", "startup", "product", "leadership"]

    for domain_id in business_domains:
        domain = get_domain(domain_id)
        assert domain.category in [DomainCategory.BUSINESS]
        assert len(domain.default_personas) >= 3


def test_technical_domains():
    """Test technical domains."""
    technical_domains = ["coding", "devops", "data"]

    for domain_id in technical_domains:
        domain = get_domain(domain_id)
        assert domain.category == DomainCategory.TECHNICAL
        assert len(domain.default_personas) >= 3


def test_personal_domains():
    """Test personal decision domains."""
    personal_domains = ["career", "decisions"]

    for domain_id in personal_domains:
        domain = get_domain(domain_id)
        assert domain.category == DomainCategory.PERSONAL
        assert len(domain.default_personas) >= 3


def test_creative_domains():
    """Test creative domains."""
    creative_domains = ["creative", "writing", "audio_post"]

    for domain_id in creative_domains:
        domain = get_domain(domain_id)
        assert domain.category == DomainCategory.CREATIVE
        if domain_id == "audio_post":
            assert "sound_designer" in domain.default_personas
        else:
            assert "treasure" in domain.default_personas or "rams" in domain.default_personas


def test_general_domain():
    """Test general purpose domain."""
    general = get_domain("general")
    assert general.category == DomainCategory.GENERAL
    assert len(general.default_personas) >= 4
    # Should include diverse perspectives
    assert any(pid in ["DK", "NT", "AG", "DR"] for pid in general.default_personas)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
