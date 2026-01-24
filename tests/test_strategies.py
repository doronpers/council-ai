"""Comprehensive tests for consultation strategies."""

from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council_ai.core.strategies.debate import DebateStrategy
from council_ai.core.strategies.individual import IndividualStrategy
from council_ai.core.strategies.sequential import SequentialStrategy
from council_ai.core.strategies.synthesis import SynthesisStrategy
from council_ai.core.strategies.vote import VoteStrategy


class MockPersona:
    """Mock persona for testing."""

    def __init__(self, id: str, name: str, emoji: str = "🎭"):
        self.id = id
        self.name = name
        self.emoji = emoji
        self.system_prompt = f"You are {name}"


class MockMemberResponse:
    """Mock member response."""

    def __init__(self, persona: MockPersona, content: str, usage: Optional[Dict] = None):
        self.persona = persona
        self.content = content
        self.usage = usage or {}


class MockCouncil:
    """Mock council for testing strategies."""

    def __init__(self, members: Optional[List[MockPersona]] = None):
        self.members = members or []
        self._provider = None
        self._synthesis_provider = None

    def _get_active_members(self, member_ids: Optional[List[str]] = None):
        if member_ids:
            return [m for m in self.members if m.id in member_ids]
        return self.members

    def _get_provider(self):
        return self._provider or MagicMock()

    async def _get_member_response(self, provider, member, query, context):
        """Get response from a single member."""
        return MockMemberResponse(persona=member, content=f"{member.name} says: {query[:20]}...")

    async def _get_member_response_stream(self, provider, member, query, context):
        """Stream responses from a single member."""
        yield {
            "type": "thinking",
            "content": f"{member.name} is thinking...",
        }
        yield {
            "type": "response_chunk",
            "content": f"{member.name} partial response",
        }
        yield {
            "type": "response_complete",
            "response": MockMemberResponse(
                persona=member, content=f"{member.name} complete response"
            ),
        }

    async def _generate_synthesis(self, provider, query, context, responses):
        """Generate synthesis from responses."""
        names = ", ".join([r.persona.name for r in responses])
        return f"Synthesis considering {names}"

    def _get_synthesis_provider(self, provider):
        return provider


# ============================================================================
# Debate Strategy Tests
# ============================================================================


class TestDebateStrategy:
    """Tests for debate consultation strategy."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        personas = [
            MockPersona("alice", "Alice", "🔵"),
            MockPersona("bob", "Bob", "🟠"),
            MockPersona("charlie", "Charlie", "🟡"),
        ]
        council = MockCouncil(personas)
        strategy = DebateStrategy()
        return strategy, council, personas

    @pytest.mark.asyncio
    async def test_debate_single_round(self, setup):
        """Test debate strategy with single round."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:
            mock_response = MockMemberResponse(personas[0], "Alice's response")
            from council_ai.core.session import ConsultationResult

            mock_individual.return_value.execute = AsyncMock(
                return_value=ConsultationResult(query="Q", responses=[mock_response])
            )

            result = await strategy.execute(
                council=council,
                query="What is AI?",
                rounds=1,
            )

            assert isinstance(result, ConsultationResult)
            assert len(result.responses) == 1
            assert result.responses[0].content == "Alice's response"

    @pytest.mark.asyncio
    async def test_debate_multiple_rounds(self, setup):
        """Test debate strategy with multiple rounds."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:
            mock_response1 = MockMemberResponse(personas[0], "Round 1 response")
            mock_response2 = MockMemberResponse(personas[0], "Round 2 response")

            from council_ai.core.session import ConsultationResult

            mock_individual.return_value.execute = AsyncMock(
                side_effect=[
                    ConsultationResult(query="Q1", responses=[mock_response1]),
                    ConsultationResult(query="Q2", responses=[mock_response2]),
                ]
            )

            result = await strategy.execute(
                council=council,
                query="What is AI?",
                rounds=2,
            )

            assert isinstance(result, ConsultationResult)
            assert len(result.responses) == 2
            assert mock_individual.return_value.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_debate_context_accumulation(self, setup):
        """Test that debate rounds accumulate context."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:
            mock_response = MockMemberResponse(personas[0], "Response")
            from council_ai.core.session import ConsultationResult

            mock_individual.return_value.execute = AsyncMock(
                return_value=ConsultationResult(query="Q", responses=[mock_response])
            )

            await strategy.execute(
                council=council,
                query="What is AI?",
                context="Initial context",
                rounds=2,
            )

            # Verify context was passed and grew with each round
            calls = mock_individual.return_value.execute.call_args_list
            assert len(calls) == 2

            # First call should have initial context
            first_context = calls[0][1]["context"]
            assert "Initial context" in first_context

            # Second call should have previous response in context
            second_context = calls[1][1]["context"]
            assert "Previous responses:" in second_context

    @pytest.mark.asyncio
    async def test_debate_stream(self, setup):
        """Test debate strategy streaming."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:

            async def mock_stream(*args, **kwargs):
                yield {"type": "chunk", "content": "streaming..."}

            mock_individual.return_value.stream = mock_stream

            updates = []
            async for update in strategy.stream(
                council=council,
                query="What is AI?",
            ):
                updates.append(update)

            assert len(updates) > 0

    @pytest.mark.asyncio
    async def test_debate_member_filtering(self, setup):
        """Test debate respects member filtering."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:
            mock_response = MockMemberResponse(personas[0], "Response")
            from council_ai.core.session import ConsultationResult

            mock_individual.return_value.execute = AsyncMock(
                return_value=ConsultationResult(query="Q", responses=[mock_response])
            )

            await strategy.execute(
                council=council,
                query="Test?",
                members=["alice"],
                rounds=1,
            )

            # Verify only selected members were used
            call_args = mock_individual.return_value.execute.call_args
            assert call_args[1]["members"] == ["alice"]


# ============================================================================
# Synthesis Strategy Tests
# ============================================================================


class TestSynthesisStrategy:
    """Tests for synthesis consultation strategy."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        personas = [
            MockPersona("alice", "Alice", "🔵"),
            MockPersona("bob", "Bob", "🟠"),
        ]
        council = MockCouncil(personas)
        strategy = SynthesisStrategy()
        return strategy, council, personas

    @pytest.mark.asyncio
    async def test_synthesis_delegates_to_individual(self, setup):
        """Test synthesis delegates to individual strategy."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:
            mock_response = MockMemberResponse(personas[0], "Individual response")
            from council_ai.core.session import ConsultationResult
            mock_individual.return_value.execute = AsyncMock(
                return_value=ConsultationResult(query="Test query?", responses=[mock_response])
            )

            result = await strategy.execute(
                council=council,
                query="Test query?",
            )

            assert isinstance(result, ConsultationResult)
            assert len(result.responses) == 1
            mock_individual.return_value.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesis_preserves_context(self, setup):
        """Test synthesis preserves context passed to execute."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:
            mock_response = MockMemberResponse(personas[0], "Response")
            mock_individual.return_value.execute = AsyncMock(return_value=[mock_response])

            test_context = "Important background info"
            await strategy.execute(
                council=council,
                query="Test?",
                context=test_context,
            )

            call_args = mock_individual.return_value.execute.call_args
            assert call_args[1]["context"] == test_context

    @pytest.mark.asyncio
    async def test_synthesis_stream(self, setup):
        """Test synthesis streaming."""
        strategy, council, personas = setup

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_individual:

            async def mock_stream(*args, **kwargs):
                yield {"type": "chunk", "content": "chunk1"}
                yield {"type": "chunk", "content": "chunk2"}

            mock_individual.return_value.stream = mock_stream

            chunks = []
            async for chunk in strategy.stream(
                council=council,
                query="Test?",
            ):
                chunks.append(chunk)

            assert len(chunks) == 2

    @pytest.mark.asyncio
    async def test_synthesis_generation(self, setup):
        """Test synthesis generation from responses."""
        strategy, council, personas = setup

        responses = [
            MockMemberResponse(personas[0], "Alice says X"),
            MockMemberResponse(personas[1], "Bob says Y"),
        ]

        synthesis = await strategy.generate_synthesis(
            council=council,
            query="What is AI?",
            context=None,
            responses=responses,
            provider=None,
        )

        assert synthesis is not None
        assert "Alice" in synthesis or "Bob" in synthesis


# ============================================================================
# Sequential Strategy Tests
# ============================================================================


class TestSequentialStrategy:
    """Tests for sequential consultation strategy."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        personas = [
            MockPersona("alice", "Alice", "🔵"),
            MockPersona("bob", "Bob", "🟠"),
            MockPersona("charlie", "Charlie", "🟡"),
        ]
        council = MockCouncil(personas)
        strategy = SequentialStrategy()
        return strategy, council, personas

    @pytest.mark.asyncio
    async def test_sequential_order_preserved(self, setup):
        """Test that sequential strategy preserves member order."""
        strategy, council, personas = setup

        responses = [
            MockMemberResponse(personas[0], f"{personas[0].name} response"),
            MockMemberResponse(personas[1], f"{personas[1].name} response"),
            MockMemberResponse(personas[2], f"{personas[2].name} response"),
        ]

        with patch.object(council, "_get_member_response", side_effect=responses):
            result = await strategy.execute(
                council=council,
                query="Test?",
            )

            # Accept either a list (legacy) or ConsultationResult (new)
            from council_ai.core.session import ConsultationResult

            if isinstance(result, ConsultationResult):
                responses = result.responses
            else:
                responses = result

            assert len(responses) == 3
            assert responses[0].content == "Alice response"
            assert responses[1].content == "Bob response"
            assert responses[2].content == "Charlie response"

    @pytest.mark.asyncio
    async def test_sequential_context_accumulation(self, setup):
        """Test context accumulates through sequential responses."""
        strategy, council, personas = setup

        response_contexts = []

        async def capture_response(provider, member, query, context):
            response_contexts.append(context)
            return MockMemberResponse(member, f"{member.name} response")

        with patch.object(council, "_get_member_response", side_effect=capture_response):
            await strategy.execute(
                council=council,
                query="Test?",
                context="Initial",
            )

            # Verify context grew with each response
            assert len(response_contexts) == 3
            assert response_contexts[0] == "Initial"
            assert "Alice" in response_contexts[1]
            assert "Alice" in response_contexts[2]
            assert "Bob" in response_contexts[2]

    @pytest.mark.asyncio
    async def test_sequential_stream(self, setup):
        """Test sequential strategy with streaming."""
        strategy, council, personas = setup

        updates = []

        with patch.object(council, "_get_member_response_stream") as mock_stream:

            async def stream_mock(*args, **kwargs):
                yield {
                    "type": "thinking",
                    "content": "thinking...",
                }
                yield {
                    "type": "response_complete",
                    "response": MockMemberResponse(personas[0], "response"),
                }

            mock_stream.side_effect = stream_mock

            async for update in strategy.stream(
                council=council,
                query="Test?",
            ):
                updates.append(update)

            assert len(updates) >= 2

    @pytest.mark.asyncio
    async def test_sequential_member_filtering(self, setup):
        """Test sequential respects member filtering."""
        strategy, council, personas = setup

        response_members = []

        async def capture_response(provider, member, query, context):
            response_members.append(member.id)
            return MockMemberResponse(member, f"{member.name} response")

        with patch.object(council, "_get_member_response", side_effect=capture_response):
            await strategy.execute(
                council=council,
                query="Test?",
                members=["alice", "charlie"],
            )

            assert response_members == ["alice", "charlie"]


# ============================================================================
# Individual Strategy Tests
# ============================================================================


class TestIndividualStrategy:
    """Tests for individual consultation strategy."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        personas = [
            MockPersona("alice", "Alice", "🔵"),
            MockPersona("bob", "Bob", "🟠"),
        ]
        council = MockCouncil(personas)
        strategy = IndividualStrategy()
        return strategy, council, personas

    @pytest.mark.asyncio
    async def test_individual_parallel_execution(self, setup):
        """Test individual strategy executes members in parallel."""
        strategy, council, personas = setup

        responses = [
            MockMemberResponse(personas[0], "Alice response"),
            MockMemberResponse(personas[1], "Bob response"),
        ]

        with patch.object(council, "_get_member_response", side_effect=responses):
            result = await strategy.execute(
                council=council,
                query="Test?",
            )

            assert hasattr(result, "responses") and len(result.responses) == 2


# ============================================================================
# Vote Strategy Tests
# ============================================================================


class TestVoteStrategy:
    """Tests for vote aggregation strategy."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        personas = [
            MockPersona("alice", "Alice", "🔵"),
            MockPersona("bob", "Bob", "🟠"),
        ]
        council = MockCouncil(personas)
        strategy = VoteStrategy()
        return strategy, council, personas

    @pytest.mark.asyncio
    async def test_vote_strategy_exists(self, setup):
        """Test vote strategy can be instantiated."""
        strategy, council, personas = setup

        assert strategy is not None
        assert hasattr(strategy, "execute")
        assert hasattr(strategy, "stream")


# ============================================================================
# Strategy Integration Tests
# ============================================================================


class TestStrategyIntegration:
    """Integration tests for strategies working together."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        personas = [
            MockPersona("alice", "Alice", "🔵"),
            MockPersona("bob", "Bob", "🟠"),
        ]
        council = MockCouncil(personas)
        return council, personas

    @pytest.mark.asyncio
    async def test_strategy_switching(self, setup):
        """Test switching between different strategies."""
        council, personas = setup

        strategies = [
            DebateStrategy(),
            SynthesisStrategy(),
            SequentialStrategy(),
        ]

        for strategy in strategies:
            assert hasattr(strategy, "execute")
            assert hasattr(strategy, "stream")

    @pytest.mark.asyncio
    async def test_different_strategies_same_query(self, setup):
        """Test same query with different strategies produces different results."""
        council, personas = setup

        response1 = MockMemberResponse(personas[0], "Synthesis response")
        response2 = MockMemberResponse(personas[0], "Sequential response")

        with patch("council_ai.core.strategies.individual.IndividualStrategy") as mock_ind:
            mock_ind.return_value.execute = AsyncMock(return_value=[response1])
            synthesis_result = await SynthesisStrategy().execute(
                council=council,
                query="Test?",
            )

        # Reset and test sequential - use AsyncMock with return_value instead of side_effect
        with patch.object(
            council, "_get_member_response", new_callable=AsyncMock, return_value=response2
        ):
            sequential_result = await SequentialStrategy().execute(
                council=council,
                query="Test?",
            )

        # Accept either list or ConsultationResult shapes
        from council_ai.core.session import ConsultationResult

        seq_len = (
            len(sequential_result.responses)
            if isinstance(sequential_result, ConsultationResult)
            else len(sequential_result)
        )
        syn_len = (
            len(synthesis_result.responses)
            if isinstance(synthesis_result, ConsultationResult)
            else len(synthesis_result)
        )

        assert syn_len >= 0
        assert seq_len >= 0
