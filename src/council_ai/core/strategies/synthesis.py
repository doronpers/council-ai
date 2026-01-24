"""Synthesis consultation strategy."""

import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional

from .base import ConsultationStrategy

if TYPE_CHECKING:
    from ..council import ConsultationMode, Council
    from ..session import MemberResponse

logger = logging.getLogger(__name__)


class SynthesisStrategy(ConsultationStrategy):
    """Individual responses followed by a synthesized summary."""

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
        from .individual import IndividualStrategy

        individual = IndividualStrategy()
        result = await individual.execute(
            council=council,
            query=query,
            context=context,
            mode=mode,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
            **kwargs,
        )
        from ..session import ConsultationResult

        if isinstance(result, ConsultationResult):
            return result.responses
        return result

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

    async def generate_synthesis(
        self,
        council: "Council",
        query: str,
        context: Optional[str],
        responses: List["MemberResponse"],
        provider: Any,
    ) -> Optional[str]:
        """Helper to generate synthesis."""
        synthesis_provider = council._get_synthesis_provider(provider)
        return await council._generate_synthesis(synthesis_provider, query, context, responses)
