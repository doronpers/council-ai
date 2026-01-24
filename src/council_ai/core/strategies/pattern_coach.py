"""
Pattern Coach Strategy

This strategy enhances the consultation context with relevant software design patterns
retrieved from the shared-ai-utils PatternManager before synthesizing a response.
"""

import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional

from shared_ai_utils.patterns.manager import PatternManager

from ..config import load_config
from ..session import ConsultationResult
from .base import ConsultationStrategy
from .synthesis import SynthesisStrategy

if TYPE_CHECKING:
    from ..council import ConsultationMode, Council

logger = logging.getLogger(__name__)


class PatternCoachStrategy(ConsultationStrategy):
    """
    Strategy that retrieves relevant patterns and advises the user based on them.
    It extends the synthesis strategy but injects pattern context first.
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
    ) -> ConsultationResult:
        """
        Execute pattern coach consultation.

        1. Initialize PatternManager.
        2. Suggest relevant patterns based on query and context.
        3. Format pattern info into the context.
        4. Delegate to SynthesisStrategy for the actual consultation.
        """
        context = self._enhance_context(query, context)

        # Delegate to synthesis strategy
        synthesis_strategy = SynthesisStrategy()
        return await synthesis_strategy.execute(
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
        """Stream consultation results with pattern enhancement."""
        context = self._enhance_context(query, context)

        # Delegate streaming to synthesis strategy
        synthesis_strategy = SynthesisStrategy()
        async for chunk in synthesis_strategy.stream(
            council=council,
            query=query,
            context=context,
            mode=mode,
            members=members,
            session_id=session_id,
            auto_recall=auto_recall,
            **kwargs,
        ):
            yield chunk

    def _enhance_context(self, query: str, context: Optional[str]) -> Optional[str]:
        """Retrieve and append patterns to context."""
        try:
            config = load_config()
            patterns_path = config.patterns_path or "patterns.json"
            pattern_manager = PatternManager(pattern_library_path=patterns_path)

            # Suggest patterns
            search_text = f"{query}\n{context or ''}"
            suggestions = pattern_manager.suggest_patterns(search_text, limit=3)

            if suggestions:
                pattern_context = self._format_patterns(suggestions)
                logger.info(f"Enhanced context with {len(suggestions)} patterns")
                if context:
                    return f"{context}\n\n{pattern_context}"
                else:
                    return pattern_context
            else:
                logger.info("No relevant patterns found for this query")
                return context

        except Exception as e:
            logger.warning(f"Failed to retrieve patterns: {e}")
            return context

    def _format_patterns(self, patterns: List[dict]) -> str:
        """Format patterns for inclusion in context."""
        parts = ["RELEVANT DESIGN PATTERNS:"]

        for p in patterns:
            name = p.get("name", "Unknown Pattern")
            desc = p.get("description", "No description")
            good = p.get("good_example", "")

            part = f"Pattern: {name}\nDescription: {desc}"
            if good:
                part += f"\nExample:\n{good}"

            parts.append(part)

        parts.append("\nPlease consider these patterns when forming your advice.")
        return "\n\n".join(parts)
