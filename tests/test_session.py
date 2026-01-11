"""
Tests for session and result handling.
"""

from datetime import datetime

import pytest

from council_ai import Persona
from council_ai.core.session import ConsultationResult, MemberResponse, Session


def test_member_response_creation():
    """Test creating a member response."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="This is advice",
        timestamp=datetime.now(),
    )

    assert response.persona.id == "test"
    assert response.content == "This is advice"
    assert response.error is None
    assert isinstance(response.timestamp, datetime)


def test_member_response_with_error():
    """Test member response with error."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="Error occurred",
        timestamp=datetime.now(),
        error="API timeout",
    )

    assert response.error == "API timeout"


def test_member_response_to_dict():
    """Test exporting member response to dict."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="Advice",
        timestamp=datetime.now(),
    )

    data = response.to_dict()
    assert data["persona_id"] == "test"
    assert data["persona_name"] == "Test"
    assert data["content"] == "Advice"
    assert "timestamp" in data


def test_consultation_result_creation():
    """Test creating a consultation result."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="Advice",
        timestamp=datetime.now(),
    )

    result = ConsultationResult(
        query="Should we do this?",
        responses=[response],
        synthesis="Based on advice, yes.",
        context="Context here",
        mode="synthesis",
    )

    assert result.query == "Should we do this?"
    assert len(result.responses) == 1
    assert result.synthesis == "Based on advice, yes."
    assert result.mode == "synthesis"


def test_consultation_result_to_dict():
    """Test exporting consultation result to dict."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="Advice",
        timestamp=datetime.now(),
    )

    result = ConsultationResult(
        query="Query",
        responses=[response],
    )

    data = result.to_dict()
    assert data["query"] == "Query"
    assert "responses" in data
    assert len(data["responses"]) == 1
    assert "timestamp" in data


def test_consultation_result_to_markdown():
    """Test exporting consultation result to markdown."""
    persona = Persona(
        id="test",
        name="Test Expert",
        title="Expert",
        emoji="🧪",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="This is my advice",
        timestamp=datetime.now(),
    )

    result = ConsultationResult(
        query="Should we do this?",
        responses=[response],
        synthesis="Yes, we should.",
    )

    markdown = result.to_markdown()

    assert "# Council Consultation" in markdown
    assert "Should we do this?" in markdown
    assert "Test Expert" in markdown
    assert "This is my advice" in markdown
    assert "Yes, we should." in markdown


def test_session_creation():
    """Test creating a session."""
    session = Session(
        council_name="Test Council",
        members=["rams", "grove"],
    )

    assert session.council_name == "Test Council"
    assert len(session.members) == 2
    assert isinstance(session.started_at, datetime)
    assert len(session.consultations) == 0


def test_session_add_consultation():
    """Test adding consultations to session."""
    session = Session(
        council_name="Test Council",
        members=["test"],
    )

    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="Advice",
        timestamp=datetime.now(),
    )

    result = ConsultationResult(
        query="Query",
        responses=[response],
    )

    session.add_consultation(result)

    assert len(session.consultations) == 1
    assert session.consultations[0].query == "Query"


def test_session_to_dict():
    """Test exporting session to dict."""
    session = Session(
        council_name="Test Council",
        members=["test1", "test2"],
    )

    data = session.to_dict()
    assert data["council_name"] == "Test Council"
    assert len(data["members"]) == 2
    assert "started_at" in data
    assert "consultations" in data


def test_consultation_result_without_synthesis():
    """Test consultation result without synthesis."""
    persona = Persona(
        id="test",
        name="Test",
        title="Expert",
        core_question="?",
        razor=".",
    )

    response = MemberResponse(
        persona=persona,
        content="Advice",
        timestamp=datetime.now(),
    )

    result = ConsultationResult(
        query="Query",
        responses=[response],
        synthesis=None,  # No synthesis
    )

    assert result.synthesis is None
    markdown = result.to_markdown()
    assert "## Individual Responses" in markdown


def test_multiple_responses():
    """Test consultation with multiple responses."""
    personas = [
        Persona(id="p1", name="P1", title="E1", core_question="?", razor="."),
        Persona(id="p2", name="P2", title="E2", core_question="?", razor="."),
        Persona(id="p3", name="P3", title="E3", core_question="?", razor="."),
    ]

    responses = [
        MemberResponse(persona=p, content=f"Advice from {p.name}", timestamp=datetime.now())
        for p in personas
    ]

    result = ConsultationResult(
        query="Query",
        responses=responses,
    )

    assert len(result.responses) == 3
    data = result.to_dict()
    assert len(data["responses"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
