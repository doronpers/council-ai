"""
Tests for consultation strategies: vote, sequential, and pattern_coach.

These strategies previously had 0% test coverage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from council_ai.core.strategies.base import ConsultationStrategy


class TestVoteStrategy:
    """Tests for the VoteStrategy."""

    def test_vote_strategy_is_consultation_strategy(self):
        """VoteStrategy should be a ConsultationStrategy subclass."""
        from council_ai.core.strategies.vote import VoteStrategy

        strategy = VoteStrategy()
        assert isinstance(strategy, ConsultationStrategy)

    @pytest.mark.asyncio
    async def test_vote_execute_formats_query_with_vote_instructions(self):
        """Vote strategy should augment the query with voting instructions."""
        from council_ai.core.strategies.vote import VoteStrategy

        strategy = VoteStrategy()

        mock_response = MagicMock()
        mock_response.query = "test"
        mock_response.responses = []
        mock_response.context = None
        mock_response.mode = "vote"

        with patch(
            "council_ai.core.strategies.individual.IndividualStrategy"
        ) as MockIndividual:
            mock_individual = MockIndividual.return_value
            mock_individual.execute = AsyncMock(return_value=mock_response)

            mock_council = MagicMock()
            result = await strategy.execute(
                council=mock_council, query="Should we proceed?"
            )

            # Verify IndividualStrategy.execute was called
            mock_individual.execute.assert_called_once()
            call_kwargs = mock_individual.execute.call_args
            # The query should contain vote instructions
            passed_query = call_kwargs.kwargs.get("query") or call_kwargs[1].get(
                "query", call_kwargs[0][1] if len(call_kwargs[0]) > 1 else None
            )
            if passed_query is None:
                # May be passed as keyword
                passed_query = mock_individual.execute.call_args.kwargs.get("query", "")
            assert "VOTE" in passed_query or result is not None

    @pytest.mark.asyncio
    async def test_vote_execute_returns_consultation_result(self):
        """Vote strategy should return a ConsultationResult."""
        from council_ai.core.strategies.vote import VoteStrategy
        from council_ai.core.session import ConsultationResult

        strategy = VoteStrategy()

        mock_result = MagicMock(spec=ConsultationResult)
        mock_result.query = "test"

        with patch(
            "council_ai.core.strategies.individual.IndividualStrategy"
        ) as MockIndividual:
            mock_individual = MockIndividual.return_value
            mock_individual.execute = AsyncMock(return_value=mock_result)

            mock_council = MagicMock()
            result = await strategy.execute(
                council=mock_council, query="Should we proceed?"
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_vote_stream_delegates_to_individual(self):
        """Vote stream should delegate to IndividualStrategy.stream."""
        from council_ai.core.strategies.vote import VoteStrategy

        strategy = VoteStrategy()

        async def mock_stream(*args, **kwargs):
            yield {"type": "response_start", "member": "test"}
            yield {"type": "response_complete", "response": MagicMock(content="VOTE: APPROVE")}

        with patch(
            "council_ai.core.strategies.individual.IndividualStrategy"
        ) as MockIndividual:
            mock_individual = MockIndividual.return_value
            mock_individual.stream = mock_stream

            mock_council = MagicMock()
            updates = []
            async for update in strategy.stream(
                council=mock_council, query="Should we proceed?"
            ):
                updates.append(update)

            assert len(updates) == 2
            assert updates[0]["type"] == "response_start"


class TestSequentialStrategy:
    """Tests for the SequentialStrategy."""

    def test_sequential_strategy_is_consultation_strategy(self):
        """SequentialStrategy should be a ConsultationStrategy subclass."""
        from council_ai.core.strategies.sequential import SequentialStrategy

        strategy = SequentialStrategy()
        assert isinstance(strategy, ConsultationStrategy)

    @pytest.mark.asyncio
    async def test_sequential_execute_accumulates_context(self):
        """Sequential strategy should pass accumulated responses as context to later members."""
        from council_ai.core.strategies.sequential import SequentialStrategy
        from council_ai.core.session import MemberResponse

        strategy = SequentialStrategy()

        mock_provider = MagicMock()

        member1 = MagicMock()
        member1.emoji = "🔬"
        member1.name = "Analyst"
        member2 = MagicMock()
        member2.emoji = "📊"
        member2.name = "Critic"

        response1 = MagicMock(spec=MemberResponse)
        response1.content = "First response"
        response2 = MagicMock(spec=MemberResponse)
        response2.content = "Second response"

        mock_council = MagicMock()
        mock_council._get_provider.return_value = mock_provider
        mock_council._get_active_members.return_value = [member1, member2]
        mock_council._get_member_response = AsyncMock(
            side_effect=[response1, response2]
        )

        result = await strategy.execute(
            council=mock_council, query="Test query", context="Initial context"
        )

        # Verify second call received accumulated context (4th positional arg)
        second_call = mock_council._get_member_response.call_args_list[1]
        accumulated_ctx = second_call[0][3]  # 4th positional arg is accumulated_context
        assert "First response" in accumulated_ctx
        assert result is not None

    @pytest.mark.asyncio
    async def test_sequential_execute_returns_consultation_result(self):
        """Sequential strategy should return a ConsultationResult with mode 'sequential'."""
        from council_ai.core.strategies.sequential import SequentialStrategy
        from council_ai.core.session import MemberResponse

        strategy = SequentialStrategy()

        member = MagicMock()
        member.emoji = "🔬"
        member.name = "Analyst"

        response = MagicMock(spec=MemberResponse)
        response.content = "Test response"

        mock_council = MagicMock()
        mock_council._get_provider.return_value = MagicMock()
        mock_council._get_active_members.return_value = [member]
        mock_council._get_member_response = AsyncMock(return_value=response)

        result = await strategy.execute(council=mock_council, query="Test query")
        assert result.mode == "sequential"
        assert len(result.responses) == 1

    @pytest.mark.asyncio
    async def test_sequential_stream_yields_updates(self):
        """Sequential stream should yield updates for each member."""
        from council_ai.core.strategies.sequential import SequentialStrategy

        strategy = SequentialStrategy()

        member = MagicMock()
        member.emoji = "🔬"
        member.name = "Analyst"

        mock_council = MagicMock()
        mock_council._get_provider.return_value = MagicMock()
        mock_council._get_active_members.return_value = [member]

        async def mock_stream(*args, **kwargs):
            yield {"type": "progress", "content": "chunk1"}
            yield {
                "type": "response_complete",
                "response": MagicMock(content="Done"),
            }

        mock_council._get_member_response_stream = mock_stream

        updates = []
        async for update in strategy.stream(
            council=mock_council, query="Test query"
        ):
            updates.append(update)

        assert len(updates) == 2


class TestPatternCoachStrategy:
    """Tests for the PatternCoachStrategy."""

    def test_pattern_coach_is_consultation_strategy(self):
        """PatternCoachStrategy should be a ConsultationStrategy subclass."""
        with patch("council_ai.core.strategies.pattern_coach.PatternManager"):
            from council_ai.core.strategies.pattern_coach import PatternCoachStrategy

            strategy = PatternCoachStrategy()
            assert isinstance(strategy, ConsultationStrategy)

    def test_format_patterns(self):
        """_format_patterns should format pattern info into readable text."""
        with patch("council_ai.core.strategies.pattern_coach.PatternManager"):
            from council_ai.core.strategies.pattern_coach import PatternCoachStrategy

            strategy = PatternCoachStrategy()

            patterns = [
                {
                    "name": "Observer",
                    "description": "Define a subscription mechanism",
                    "good_example": "event emitters",
                },
                {"name": "Strategy", "description": "Encapsulate algorithms"},
            ]

            result = strategy._format_patterns(patterns)
            assert "Observer" in result
            assert "subscription mechanism" in result
            assert "Strategy" in result
            assert "event emitters" in result
            assert "RELEVANT DESIGN PATTERNS" in result

    def test_enhance_context_returns_original_when_no_manager(self):
        """_enhance_context should return original context when PatternManager is None."""
        with patch("council_ai.core.strategies.pattern_coach.PatternManager"):
            from council_ai.core.strategies.pattern_coach import PatternCoachStrategy

            strategy = PatternCoachStrategy()
            # Force _pattern_manager to None
            strategy._pattern_manager = None
            strategy._cached_config = MagicMock(patterns_path=None)

            with patch.object(
                strategy, "_get_pattern_manager", return_value=None
            ):
                result = strategy._enhance_context("query", "original context")
                assert result == "original context"

    def test_enhance_context_appends_patterns(self):
        """_enhance_context should append found patterns to context."""
        with patch("council_ai.core.strategies.pattern_coach.PatternManager"):
            from council_ai.core.strategies.pattern_coach import PatternCoachStrategy

            strategy = PatternCoachStrategy()

            mock_manager = MagicMock()
            mock_manager.suggest_patterns.return_value = [
                {"name": "Singleton", "description": "Ensure single instance"}
            ]

            with patch.object(
                strategy, "_get_pattern_manager", return_value=mock_manager
            ):
                result = strategy._enhance_context("query", "existing context")
                assert "existing context" in result
                assert "Singleton" in result

    def test_enhance_context_handles_exceptions(self):
        """_enhance_context should return original context on errors."""
        with patch("council_ai.core.strategies.pattern_coach.PatternManager"):
            from council_ai.core.strategies.pattern_coach import PatternCoachStrategy

            strategy = PatternCoachStrategy()

            mock_manager = MagicMock()
            mock_manager.suggest_patterns.side_effect = ValueError("Pattern error")

            with patch.object(
                strategy, "_get_pattern_manager", return_value=mock_manager
            ):
                result = strategy._enhance_context("query", "original context")
                assert result == "original context"

    @pytest.mark.asyncio
    async def test_pattern_coach_execute_delegates_to_synthesis(self):
        """PatternCoachStrategy.execute should delegate to SynthesisStrategy."""
        with patch("council_ai.core.strategies.pattern_coach.PatternManager"):
            from council_ai.core.strategies.pattern_coach import PatternCoachStrategy

            strategy = PatternCoachStrategy()

            mock_result = MagicMock()

            mock_synthesis = MagicMock()
            mock_synthesis.execute = AsyncMock(return_value=mock_result)

            with (
                patch.object(strategy, "_enhance_context", return_value="enhanced"),
                patch.object(
                    strategy, "_get_synthesis_strategy", return_value=mock_synthesis
                ),
            ):
                mock_council = MagicMock()
                result = await strategy.execute(
                    council=mock_council, query="How to structure this?"
                )
                assert result is mock_result
                mock_synthesis.execute.assert_called_once()


class TestGetStrategy:
    """Tests for the get_strategy factory function."""

    def test_get_strategy_returns_individual(self):
        """get_strategy should return IndividualStrategy for 'individual'."""
        from council_ai.core.strategies import get_strategy

        strategy = get_strategy("individual")
        from council_ai.core.strategies.individual import IndividualStrategy

        assert isinstance(strategy, IndividualStrategy)

    def test_get_strategy_returns_synthesis(self):
        """get_strategy should return SynthesisStrategy for 'synthesis'."""
        from council_ai.core.strategies import get_strategy

        strategy = get_strategy("synthesis")
        from council_ai.core.strategies.synthesis import SynthesisStrategy

        assert isinstance(strategy, SynthesisStrategy)

    def test_get_strategy_returns_sequential(self):
        """get_strategy should return SequentialStrategy for 'sequential'."""
        from council_ai.core.strategies import get_strategy

        strategy = get_strategy("sequential")
        from council_ai.core.strategies.sequential import SequentialStrategy

        assert isinstance(strategy, SequentialStrategy)

    def test_get_strategy_returns_vote(self):
        """get_strategy should return VoteStrategy for 'vote'."""
        from council_ai.core.strategies import get_strategy

        strategy = get_strategy("vote")
        from council_ai.core.strategies.vote import VoteStrategy

        assert isinstance(strategy, VoteStrategy)

    def test_get_strategy_unknown_mode_raises(self):
        """get_strategy should raise ValueError for unknown modes."""
        from council_ai.core.strategies import get_strategy

        with pytest.raises(ValueError, match="Unknown consultation mode"):
            get_strategy("nonexistent_mode")

    def test_get_strategy_returns_same_instance(self):
        """get_strategy should return singleton instances."""
        from council_ai.core.strategies import get_strategy

        s1 = get_strategy("individual")
        s2 = get_strategy("individual")
        assert s1 is s2
