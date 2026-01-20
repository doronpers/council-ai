"""
Synthesis consultation strategy.
"""

import logging
from typing import List, Optional, Any, Dict, AsyncIterator, TYPE_CHECKING
from .base import ConsultationStrategy

if TYPE_CHECKING:
    from ..council import Council, ConsultationMode
    from ..session import MemberResponse

logger = logging.getLogger(__name__)


class SynthesisStrategy(ConsultationStrategy):
    """
    Individual responses followed by a synthesized summary.
    """

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
        return await individual.execute(
            council=council,
            query=query,
            context=context,
            mode=mode,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
            **kwargs,
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
        provider = council._get_provider()
        active_members = council._get_active_members(members)
        return council._consult_individual_stream(provider, active_members, query, context)

    async def generate_synthesis(
        self,
        council: "Council",
        query: str,
        context: Optional[str],
        responses: List["MemberResponse"],
        provider: Any,
    ) -> Optional[str]:
        """
        Helper to generate synthesis.
        """
        synthesis_provider = council._get_synthesis_provider(provider)
        return await council._generate_synthesis(synthesis_provider, query, context, responses)
