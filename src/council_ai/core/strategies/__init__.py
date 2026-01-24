"""Consultation strategies package."""

from typing import Dict

from .base import ConsultationStrategy

# Map of mode to strategy instance (to be populated as we migrate)
_STRATEGIES: Dict[str, ConsultationStrategy] = {}


def get_strategy(mode_name: str) -> ConsultationStrategy:
    """Factory to get a strategy instance by mode name."""
    if mode_name not in _STRATEGIES:
        # Lazy import to avoid circular dependencies
        from ..council import ConsultationMode

        if mode_name == ConsultationMode.INDIVIDUAL.value:
            from .individual import IndividualStrategy

            _STRATEGIES[ConsultationMode.INDIVIDUAL.value] = IndividualStrategy()
        elif mode_name == ConsultationMode.SYNTHESIS.value:
            from .synthesis import SynthesisStrategy

            _STRATEGIES[ConsultationMode.SYNTHESIS.value] = SynthesisStrategy()
        elif mode_name == ConsultationMode.SEQUENTIAL.value:
            from .sequential import SequentialStrategy

            _STRATEGIES[ConsultationMode.SEQUENTIAL.value] = SequentialStrategy()
        elif mode_name == ConsultationMode.DEBATE.value:
            from .debate import DebateStrategy

            _STRATEGIES[ConsultationMode.DEBATE.value] = DebateStrategy()
        elif mode_name == ConsultationMode.VOTE.value:
            from .vote import VoteStrategy

            _STRATEGIES[ConsultationMode.VOTE.value] = VoteStrategy()
        else:
            raise ValueError(f"Unknown consultation mode: {mode_name}")

    return _STRATEGIES[mode_name]
