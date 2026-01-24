"""Strategy execute return type compatibility tests."""
from datetime import datetime

import pytest

from council_ai import Council, Persona
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult(monkeypatch):
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_council_handles_strategy_returning_list(monkeypatch):
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a list of MemberResponse
    persona = Persona(id="T2", name="Test2", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona, content="ListAdvice", timestamp=datetime.now()
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return [member_response]

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "ListAdvice"
