"""Strategy execute return type compatibility tests."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council_ai import Council, Persona
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult():
    """Test that Council.consult_async handles ConsultationResult from strategies."""
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Mock provider to avoid API key requirements
    mock_provider = MagicMock()

    with patch("council_ai.core.council.get_strategy", return_value=DummyStrategy()):
        with patch.object(council, "_get_provider", return_value=mock_provider):
            result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_council_handles_strategy_returning_list():
    """Test that Council.consult_async handles legacy list[MemberResponse] from strategies."""
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a list of MemberResponse
    persona = Persona(id="T2", name="Test2", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona, content="ListAdvice", timestamp=datetime.now()
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return [member_response]

    # Mock provider to avoid API key requirements
    mock_provider = MagicMock()

    with patch("council_ai.core.council.get_strategy", return_value=DummyStrategy()):
        with patch.object(council, "_get_provider", return_value=mock_provider):
            result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "ListAdvice"


@pytest.mark.anyio
async def test_synthesis_strategy_returns_consultationresult():
    """Test that SynthesisStrategy returns ConsultationResult, not a list."""
    from council_ai.core.strategies.individual import IndividualStrategy
    from council_ai.core.strategies.synthesis import SynthesisStrategy

    council = Council(api_key="test-key")
    strategy = SynthesisStrategy()

    # Mock the individual strategy's response
    persona = Persona(id="T3", name="Test3", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona, content="SynthesisAdvice", timestamp=datetime.now()
    )
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    # Mock IndividualStrategy at the module where it's imported
    with patch.object(IndividualStrategy, "execute", new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = fake_result

        result = await strategy.execute(council=council, query="Test Q")

    # Should return ConsultationResult, not list
    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "SynthesisAdvice"


@pytest.mark.anyio
async def test_debate_strategy_returns_consultationresult():
    """Test that DebateStrategy returns ConsultationResult consistently."""
    from council_ai.core.strategies.debate import DebateStrategy
    from council_ai.core.strategies.individual import IndividualStrategy

    council = Council(api_key="test-key")
    strategy = DebateStrategy()

    # Mock active members
    persona1 = Persona(id="D1", name="Debater1", title="D", core_question="?", razor=".")
    persona2 = Persona(id="D2", name="Debater2", title="D", core_question="?", razor=".")

    with patch.object(council, "_get_active_members", return_value=[persona1, persona2]):
        # Mock individual strategy responses
        response1 = MemberResponse(persona=persona1, content="Position A", timestamp=datetime.now())
        response2 = MemberResponse(persona=persona2, content="Position B", timestamp=datetime.now())
        fake_result = ConsultationResult(query="Debate Q", responses=[response1, response2])

        with patch.object(IndividualStrategy, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = fake_result

            result = await strategy.execute(council=council, query="Debate Q", rounds=1)

    # Should return ConsultationResult, not list
    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 2
    assert result.mode == "debate"
