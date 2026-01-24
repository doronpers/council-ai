"""Debate consultation strategy."""

from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional

from .base import ConsultationStrategy

if TYPE_CHECKING:
    from ..council import ConsultationMode, Council
    from ..session import ConsultationResult, MemberResponse


class DebateStrategy(ConsultationStrategy):
    """Multi-round debate between members."""

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
        rounds = kwargs.get("rounds", 2)
        active_members = council._get_active_members(members)

        all_responses: List["MemberResponse"] = []

        for round_num in range(rounds):
            round_context = context or ""

            # Add previous round responses to context
            if all_responses:
                round_context += "\n\nPrevious responses:\n"
                for resp in all_responses:
                    round_context += f"\n{resp.persona.emoji} {resp.persona.name}: {resp.content}\n"

            round_query = (
                query
                if round_num == 0
                else f"[Round {round_num + 1}] Respond to your colleagues' points on: {query}"
            )

            from .individual import IndividualStrategy

            individual = IndividualStrategy()
            round_result = await individual.execute(
                council=council,
                query=round_query,
                context=round_context,
                members=[m.id for m in active_members],
            )
            # IndividualStrategy now always returns ConsultationResult
            from ..session import ConsultationResult as ResultType

            if isinstance(round_result, ResultType):
                round_responses = round_result.responses
            else:
                # Legacy fallback (should not happen with updated strategies)
                round_responses = round_result

            all_responses.extend(round_responses)

        # Return ConsultationResult for consistency with other strategies

        mode_str = mode.value if mode is not None else "debate"
        return ConsultationResult(
            query=query,
            responses=all_responses,
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
        """Debate mode with streaming (simplified - streams first round)."""
        from .individual import IndividualStrategy

        individual = IndividualStrategy()
        async for update in individual.stream(
            council=council,
            query=query,
            context=context,
            mode=mode,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
            **kwargs,
        ):
            yield update
