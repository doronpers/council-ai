"""
Base class for consultation strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, AsyncIterator, TYPE_CHECKING

if TYPE_CHECKING:
    from ..council import Council, ConsultationMode
    from ..session import ConsultationResult


class ConsultationStrategy(ABC):
    """
    Abstract base class for consultation strategies.

    Each strategy implements a specific consultation mode logic.
    """

    @abstractmethod
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
        """
        Execute the consultation strategy.

        Args:
            council: The council instance
            query: The user query
            context: Additional context
            mode: Consultation mode
            members: List of specific members to consult
            session_id: Optional session ID
            auto_recall: Whether to auto-recall context
            **kwargs: Additional strategy-specific arguments

        Returns:
            ConsultationResult: The result of the consultation
        """
        pass

    @abstractmethod
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
        """
        Stream consultation results.

        Args:
            council: The council instance
            query: The user query
            context: Additional context
            mode: Consultation mode
            members: List of specific members to consult
            session_id: Optional session ID
            auto_recall: Whether to auto-recall context
            **kwargs: Additional strategy-specific arguments

        Yields:
            Dict[str, Any]: Event updates (response_start, progress, etc.)
        """
        # Yielding an empty iterator as a base case
        if False:
            yield {}
        pass
