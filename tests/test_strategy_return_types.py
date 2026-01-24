"""Strategy execute return type compatibility tests."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from council_ai import Council, Persona
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult(monkeypatch):
    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Mock provider to avoid API key requirement
    mock_provider = MagicMock()
    
    # Mock the Council methods that need a provider
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())
    
    council = Council(api_key="test-key")
    monkeypatch.setattr(council, "_get_provider", lambda **kwargs: mock_provider)
    monkeypatch.setattr(council, "_start_session", lambda *args, **kwargs: MagicMock(session_id="test-session"))

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_all_strategies_return_consultationresult():
    """Test that all built-in strategies return ConsultationResult."""
    from council_ai.core.strategies.debate import DebateStrategy
    from council_ai.core.strategies.individual import IndividualStrategy
    from council_ai.core.strategies.sequential import SequentialStrategy
    from council_ai.core.strategies.synthesis import SynthesisStrategy
    from council_ai.core.strategies.vote import VoteStrategy

    strategies = [
        IndividualStrategy,
        SequentialStrategy,
        SynthesisStrategy,
        DebateStrategy,
        VoteStrategy,
    ]

    for strategy_class in strategies:
        strategy = strategy_class()
        # Check the return type annotation
        import inspect
        sig = inspect.signature(strategy.execute)
        return_annotation = sig.return_annotation
        
        # The return type should be "ConsultationResult" or ConsultationResult class
        assert "ConsultationResult" in str(return_annotation), (
            f"{strategy_class.__name__}.execute() should return ConsultationResult, "
            f"but has return type: {return_annotation}"
        )
