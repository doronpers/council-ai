"""Sequential consultation strategy."""

from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, cast

from .base import ConsultationStrategy

if TYPE_CHECKING:
    from ..council import ConsultationMode, Council
    from ..session import ConsultationResult


class SequentialStrategy(ConsultationStrategy):
    """Members respond in order, each seeing previous responses."""

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
        provider = council._get_provider()
        active_members = council._get_active_members(members)

        responses: List["MemberResponse"] = []
        accumulated_context = context or ""

        for member in active_members:
            response = await council._get_member_response(
                provider, member, query, accumulated_context
            )
            responses.append(response)

            # Add this response to context for next member
            accumulated_context += f"\n\n{member.emoji} {member.name} said:\n{response.content}"

        # Build ConsultationResult for consistency
        from ..session import ConsultationResult, MemberResponse

        mode_str = mode.value if mode is not None else "sequential"
        return ConsultationResult(
            query=query,
            responses=cast(List[MemberResponse], responses),
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
        """Get responses sequentially, each seeing previous responses (streaming)."""
        provider = council._get_provider()
        active_members = council._get_active_members(members)
        accumulated_context = context or ""

        for member in active_members:
            async for update in council._get_member_response_stream(
                provider, member, query, accumulated_context
            ):
                yield update
                if update.get("type") == "response_complete":
                    response = update["response"]
                    accumulated_context += (
                        f"\n\n{member.emoji} {member.name} said:\n{response.content}"
                    )
