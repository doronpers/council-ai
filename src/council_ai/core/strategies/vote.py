"""Vote consultation strategy."""

from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, cast

from .base import ConsultationStrategy

if TYPE_CHECKING:
    from ..council import ConsultationMode, Council
    from ..session import ConsultationResult


class VoteStrategy(ConsultationStrategy):
    """Members vote on a decision."""

    async def execute(
        self,
        council: "Council",
        query: str,
        context: Optional[str] = None,
        mode: Optional["ConsultationMode"] = None,
        members: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        auto_recall: bool = True,
        **kwargs: Any,
    ) -> "ConsultationResult":
        vote_query = f"""
{query}

Please provide:
1. Your VOTE: APPROVE / REJECT / ABSTAIN
2. Your CONFIDENCE: HIGH / MEDIUM / LOW
3. Brief reasoning (2-3 sentences)

Format your response as:
VOTE: [your vote]
CONFIDENCE: [your confidence]
REASONING: [your reasoning]
"""
        from .individual import IndividualStrategy

        individual = IndividualStrategy()
        result = await individual.execute(
            council=council, query=vote_query, context=context, members=members
        )
        from ..session import ConsultationResult, MemberResponse

        mode_str = mode.value if mode is not None else "vote"

        if isinstance(result, ConsultationResult):
            return result
        return ConsultationResult(
            query=query,
            responses=cast(List[MemberResponse], result),
            context=context,
            mode=mode_str,
        )

    async def stream(
        self,
        council: "Council",
        query: str,
        context: Optional[str] = None,
        mode: Optional["ConsultationMode"] = None,
        members: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        auto_recall: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Vote mode with streaming."""
        vote_query = f"""
{query}

Please provide:
1. Your VOTE: APPROVE / REJECT / ABSTAIN
2. Your CONFIDENCE: HIGH / MEDIUM / LOW
3. Brief reasoning (2-3 sentences)

Format your response as:
VOTE: [your vote]
CONFIDENCE: [your confidence]
REASONING: [your reasoning]
"""
        from .individual import IndividualStrategy

        individual = IndividualStrategy()
        async for update in individual.stream(
            council=council,
            query=vote_query,
            context=context,
            mode=mode,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
            **kwargs,
        ):
            yield update
