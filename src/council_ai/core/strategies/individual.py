"""Individual consultation strategy."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional

from .base import ConsultationStrategy

if TYPE_CHECKING:
    from ..council import ConsultationMode, Council
    from ..session import MemberResponse, Persona

logger = logging.getLogger(__name__)


class IndividualStrategy(ConsultationStrategy):
    """Each member responds separately and in parallel."""

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
    ) -> List["MemberResponse"]:
        provider = council._get_provider()
        active_members = council._get_active_members(members)

        tasks = [
            council._get_member_response(provider, member, query, context)
            for member in active_members
        ]
        return await asyncio.gather(*tasks)

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
        """Get individual responses from all members concurrently (streaming)."""
        provider = council._get_provider()
        active_members = council._get_active_members(members)

        if not active_members:
            return

        queue: asyncio.Queue[object] = asyncio.Queue()
        done_sentinel = object()

        async def consume_member_stream(member: "Persona") -> None:
            """Consume a single member's stream and put updates in the queue."""
            try:
                async for update in council._get_member_response_stream(
                    provider, member, query, context
                ):
                    if isinstance(update, dict) and "persona_id" not in update:
                        update = {**update, "persona_id": member.id}
                    await queue.put(update)
            except Exception as e:
                logger.error("Error in stream for %s: %s", member.name, e)
                # We need MemberResponse here. Import it inside if needed or through TYPE_CHECKING
                from datetime import datetime

                from ..session import MemberResponse

                response = MemberResponse(
                    persona=member,
                    content=f"[Error getting response: {e}]",
                    timestamp=datetime.now(),
                    error=str(e),
                )
                await queue.put(
                    {
                        "type": "response_complete",
                        "persona_id": member.id,
                        "response": response,
                    }
                )
            finally:
                await queue.put(done_sentinel)

        tasks = [asyncio.create_task(consume_member_stream(member)) for member in active_members]

        completed_streams = 0
        try:
            while completed_streams < len(tasks):
                update = await queue.get()
                if update is done_sentinel:
                    completed_streams += 1
                    continue
                if isinstance(update, dict) and "persona_id" not in update:
                    update = {**update, "persona_id": "unknown"}
                yield update  # type: ignore[misc]
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
