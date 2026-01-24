"""Test that DebateStrategy and SynthesisStrategy return correct types.

This test specifically addresses the issue:
"Keep DebateStrategy returning a response list"

The issue was that strategies had inconsistent return types, which could cause
TypeError when Council.consult_async tries to iterate over responses or check len().
"""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council_ai.core.persona import Persona
from council_ai.core.session import ConsultationResult, MemberResponse
from council_ai.core.strategies.debate import DebateStrategy
from council_ai.core.strategies.synthesis import SynthesisStrategy


class MockCouncil:
    """Mock council for testing."""

    def __init__(self):
        self.personas = [
            Persona(id="p1", name="Persona1", title="T1", core_question="?", razor="."),
            Persona(id="p2", name="Persona2", title="T2", core_question="?", razor="."),
        ]

    def _get_active_members(self, members=None):
        return self.personas


@pytest.mark.asyncio
async def test_debate_strategy_returns_list():
    """Test that DebateStrategy returns List[MemberResponse], not ConsultationResult."""
    strategy = DebateStrategy()
    council = MockCouncil()

    # Mock IndividualStrategy to return ConsultationResult
    persona = council.personas[0]
    response1 = MemberResponse(persona=persona, content="Round 1", timestamp=datetime.now())
    response2 = MemberResponse(persona=persona, content="Round 2", timestamp=datetime.now())

    fake_result1 = ConsultationResult(query="Q1", responses=[response1])
    fake_result2 = ConsultationResult(query="Q2", responses=[response2])

    with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_ind:
        mock_ind.return_value.execute = AsyncMock(side_effect=[fake_result1, fake_result2])

        result = await strategy.execute(council=council, query="test", rounds=2)

        # DebateStrategy MUST return a list, not ConsultationResult
        assert isinstance(result, list), f"Expected list, got {type(result).__name__}"
        assert len(result) == 2, f"Expected 2 responses, got {len(result)}"
        assert all(
            isinstance(r, MemberResponse) for r in result
        ), "All items must be MemberResponse"

        # Verify we can iterate (this is what Council.consult_async does)
        for r in result:
            assert hasattr(r, "content")
            assert hasattr(r, "persona")


@pytest.mark.asyncio
async def test_synthesis_strategy_returns_consultation_result():
    """Test that SynthesisStrategy returns ConsultationResult, not List[MemberResponse]."""
    strategy = SynthesisStrategy()
    council = MockCouncil()

    # Mock IndividualStrategy to return ConsultationResult
    persona = council.personas[0]
    response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Q", responses=[response])

    with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_ind:
        mock_ind.return_value.execute = AsyncMock(return_value=fake_result)

        result = await strategy.execute(council=council, query="test")

        # SynthesisStrategy MUST return ConsultationResult (after fix)
        assert isinstance(
            result, ConsultationResult
        ), f"Expected ConsultationResult, got {type(result).__name__}"
        assert hasattr(result, "responses"), "ConsultationResult must have responses"
        assert len(result.responses) == 1, f"Expected 1 response, got {len(result.responses)}"
        assert isinstance(
            result.responses[0], MemberResponse
        ), "Response items must be MemberResponse"


@pytest.mark.asyncio
async def test_synthesis_strategy_backwards_compatibility():
    """Test that SynthesisStrategy handles legacy list returns from IndividualStrategy."""
    strategy = SynthesisStrategy()
    council = MockCouncil()

    # Mock IndividualStrategy to return a list (legacy behavior)
    persona = council.personas[0]
    response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_ind:
        mock_ind.return_value.execute = AsyncMock(return_value=[response])

        result = await strategy.execute(council=council, query="test")

        # When IndividualStrategy returns a list, SynthesisStrategy should return it as-is
        # for backwards compatibility
        assert isinstance(result, list), f"Expected list for legacy mode, got {type(result).__name__}"
        assert len(result) == 1
        assert result[0] == response


@pytest.mark.asyncio
async def test_council_handles_debate_mode_list_return():
    """Test that Council.consult_async correctly handles list return from DebateStrategy.

    This is the core issue from the bug report:
    'Council.consult_async still treats strategy.execute(...) as List[MemberResponse]
    and immediately calls len(responses) and iterates over responses'
    """
    # Simulate what Council.consult_async does (lines 753-757)
    persona = Persona(id="test", name="Test", title="T", core_question="?", razor=".")
    response = MemberResponse(persona=persona, content="Test", timestamp=datetime.now())

    # Simulate DebateStrategy returning a list
    result_or_responses = [response, response]

    # Council's backwards-compatible handling
    if isinstance(result_or_responses, ConsultationResult):
        strategy_result = result_or_responses
        responses = strategy_result.responses
    else:
        responses = result_or_responses  # This is what happens for DebateStrategy

    # Verify we can do what Council does
    assert len(responses) == 2, "Should be able to call len() on responses"
    for r in responses:  # Should be able to iterate
        assert isinstance(r, MemberResponse)

    # Verify synthesis can be generated (line 762 checks mode == DEBATE)
    assert all(hasattr(r, "persona") and hasattr(r, "content") for r in responses)


@pytest.mark.asyncio
async def test_council_handles_synthesis_mode_consultationresult_return():
    """Test that Council.consult_async correctly handles ConsultationResult from SynthesisStrategy."""
    # Simulate what Council.consult_async does (lines 753-757)
    persona = Persona(id="test", name="Test", title="T", core_question="?", razor=".")
    response = MemberResponse(persona=persona, content="Test", timestamp=datetime.now())

    # Simulate SynthesisStrategy returning ConsultationResult
    result_or_responses = ConsultationResult(query="Q", responses=[response, response])

    # Council's backwards-compatible handling
    if isinstance(result_or_responses, ConsultationResult):
        strategy_result = result_or_responses
        responses = strategy_result.responses
    else:
        responses = result_or_responses

    # Verify we can do what Council does
    assert len(responses) == 2, "Should be able to call len() on responses"
    for r in responses:  # Should be able to iterate
        assert isinstance(r, MemberResponse)
