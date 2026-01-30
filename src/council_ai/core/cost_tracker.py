"""Cost Tracking - Track token usage and calculate API costs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

# Provider pricing per 1M tokens (input/output)
# Prices in USD as of 2024
PRICING: Dict[str, Dict[str, Dict[str, float]]] = {
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-2.1": {"input": 8.0, "output": 24.0},
        "claude-2.0": {"input": 8.0, "output": 24.0},
        "claude-instant-1.2": {"input": 0.8, "output": 2.4},
    },
    "openai": {
        "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-32k": {"input": 60.0, "output": 120.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "gpt-3.5-turbo-16k": {"input": 3.0, "output": 4.0},
    },
    "gemini": {
        "gemini-pro": {"input": 0.5, "output": 1.5},
        "gemini-pro-vision": {"input": 0.25, "output": 0.625},
    },
}


@dataclass
class CostRecord:
    """Record of cost for a single API call."""

    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CostRecord":
        """Create from dictionary."""
        return cls(
            provider=data["provider"],
            model=data["model"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            cost_usd=data["cost_usd"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class CostTracker:
    """Track and calculate API costs."""

    def __init__(self):
        """Initialize cost tracker."""
        self._records: list[CostRecord] = []

    def calculate_cost(
        self, provider: str, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """
        Calculate cost for a given provider, model, and token usage.

        Args:
            provider: Provider name (anthropic, openai, gemini)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        # Normalize model name (remove version suffixes if needed)
        model_key = self._normalize_model_name(provider, model)

        # Get pricing
        provider_pricing = PRICING.get(provider, {})
        model_pricing = provider_pricing.get(model_key)

        if not model_pricing:
            # Fallback: use average pricing or return 0
            # For unknown models, estimate conservatively
            if provider == "anthropic":
                input_price = 3.0
                output_price = 15.0
            elif provider == "openai":
                input_price = 10.0
                output_price = 30.0
            elif provider == "gemini":
                input_price = 0.5
                output_price = 1.5
            else:
                # Unknown provider - return 0
                return 0.0
        else:
            input_price = model_pricing["input"]
            output_price = model_pricing["output"]

        # Calculate cost (prices are per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price

        return input_cost + output_cost

    def _normalize_model_name(self, provider: str, model: str) -> str:
        """Normalize model name for pricing lookup."""
        # Try exact match first
        provider_pricing = PRICING.get(provider, {})
        if model in provider_pricing:
            return model

        # Try partial matches (e.g., "claude-3-5-sonnet" matches "claude-3-5-sonnet-20241022")
        for key in provider_pricing.keys():
            if model.startswith(key) or key.startswith(model):
                return key

        # Return original if no match
        return model

    def record_cost(
        self, provider: str, model: str, input_tokens: int, output_tokens: int
    ) -> CostRecord:
        """
        Record a cost for tracking.

        Args:
            provider: Provider name
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used

        Returns:
            CostRecord with calculated cost
        """
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        record = CostRecord(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            timestamp=datetime.now(),
        )
        self._records.append(record)
        return record

    def get_total_cost(self) -> float:
        """Get total cost across all records."""
        return sum(record.cost_usd for record in self._records)

    def get_records(self) -> list[CostRecord]:
        """Get all cost records."""
        return self._records.copy()

    def clear(self) -> None:
        """Clear all records."""
        self._records.clear()


# Global cost tracker instance
_global_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()
    return _global_tracker
