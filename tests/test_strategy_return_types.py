"""Strategy execute return type compatibility tests."""

from datetime import datetime
from unittest.mock import patch

import pytest

from council_ai import Council, Persona
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.fixture
def mock_env_keys(monkeypatch):
    """Mock environment variables for API keys."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")


@pytest.fixture
def mock_get_api_key(monkeypatch):
    """Mock get_api_key function."""
    with patch("council_ai.core.council.get_api_key") as mock:
        mock.side_effect = lambda name: f"key-for-{name}"
        yield mock


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult(
    monkeypatch, mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Test that council properly handles strategies that return ConsultationResult."""
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

        async def stream(self, **kwargs):
            return
            yield  # Make this a generator function

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_council_handles_strategy_returning_list(
    monkeypatch, mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Test that council properly handles strategies that return List[MemberResponse]."""
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a list of MemberResponse
    persona = Persona(id="T2", name="Test2", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona, content="ListAdvice", timestamp=datetime.now()
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return [member_response]

        async def stream(self, **kwargs):
            return
            yield  # Make this a generator function

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "ListAdvice"


@pytest.mark.anyio
async def test_council_validates_strategy_return_type(
    monkeypatch, mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Test that council raises TypeError for invalid strategy return types."""
    council = Council(api_key="test-key")

    class BadStrategy:
        async def execute(self, **kwargs):
            return "invalid-return-type"  # Neither ConsultationResult nor list

        async def stream(self, **kwargs):
            return
            yield  # Make this a generator function

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: BadStrategy())

    with pytest.raises(
        TypeError, match="Strategy returned unexpected type.*Expected ConsultationResult or List"
    ):
        await council.consult_async("Test Q")


@pytest.mark.anyio
async def test_consultation_result_mode_validation():
    """Test that ConsultationResult validates mode field."""
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())

    # Valid mode should work
    result = ConsultationResult(query="Test Q", responses=[member_response], mode="synthesis")
    assert result.mode == "synthesis"

    # Invalid mode should raise ValueError
    with pytest.raises(ValueError, match="Invalid mode.*Must be one of"):
        ConsultationResult(query="Test Q", responses=[member_response], mode="invalid-mode")
