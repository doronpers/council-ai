"""
Tests for core/cost_tracker.py — CostRecord, CostTracker, PRICING.

This module previously had only 41% test coverage.
"""

from datetime import datetime

import pytest

from council_ai.core.cost_tracker import (
    PRICING,
    CostRecord,
    CostTracker,
    get_cost_tracker,
)


class TestCostRecord:
    """Tests for the CostRecord dataclass."""

    def test_create_record(self):
        record = CostRecord(
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
        )
        assert record.provider == "anthropic"
        assert record.model == "claude-3-sonnet-20240229"
        assert record.input_tokens == 100
        assert record.output_tokens == 50
        assert record.cost_usd == 0.001

    def test_to_dict(self):
        ts = datetime(2024, 1, 15, 10, 0, 0)
        record = CostRecord(
            provider="openai",
            model="gpt-4",
            input_tokens=200,
            output_tokens=100,
            cost_usd=0.012,
            timestamp=ts,
        )
        d = record.to_dict()
        assert d["provider"] == "openai"
        assert d["model"] == "gpt-4"
        assert d["input_tokens"] == 200
        assert d["output_tokens"] == 100
        assert d["cost_usd"] == 0.012
        assert d["timestamp"] == ts.isoformat()

    def test_from_dict(self):
        data = {
            "provider": "gemini",
            "model": "gemini-pro",
            "input_tokens": 300,
            "output_tokens": 150,
            "cost_usd": 0.005,
            "timestamp": "2024-01-15T10:00:00",
        }
        record = CostRecord.from_dict(data)
        assert record.provider == "gemini"
        assert record.input_tokens == 300
        assert record.timestamp == datetime(2024, 1, 15, 10, 0, 0)

    def test_round_trip(self):
        ts = datetime(2024, 6, 1, 12, 30, 0)
        original = CostRecord(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            input_tokens=500,
            output_tokens=250,
            cost_usd=0.002,
            timestamp=ts,
        )
        restored = CostRecord.from_dict(original.to_dict())
        assert restored.provider == original.provider
        assert restored.model == original.model
        assert restored.input_tokens == original.input_tokens
        assert restored.output_tokens == original.output_tokens
        assert restored.cost_usd == original.cost_usd
        assert restored.timestamp == original.timestamp


class TestCostTracker:
    """Tests for the CostTracker class."""

    def test_init_empty(self):
        tracker = CostTracker()
        assert tracker.get_total_cost() == 0.0
        assert tracker.get_records() == []

    def test_calculate_cost_known_model(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "anthropic", "claude-3-sonnet-20240229", input_tokens=1_000_000, output_tokens=0
        )
        assert cost == 3.0  # $3/1M input tokens

    def test_calculate_cost_output_tokens(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "anthropic", "claude-3-sonnet-20240229", input_tokens=0, output_tokens=1_000_000
        )
        assert cost == 15.0  # $15/1M output tokens

    def test_calculate_cost_both_tokens(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "anthropic", "claude-3-sonnet-20240229", input_tokens=1000, output_tokens=500
        )
        # (1000/1M * 3.0) + (500/1M * 15.0) = 0.003 + 0.0075 = 0.0105
        assert abs(cost - 0.0105) < 1e-9

    def test_calculate_cost_openai_model(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "openai", "gpt-4", input_tokens=1_000_000, output_tokens=1_000_000
        )
        assert cost == 30.0 + 60.0  # $30 input + $60 output

    def test_calculate_cost_unknown_model_uses_fallback(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "anthropic", "claude-unknown-model", input_tokens=1_000_000, output_tokens=0
        )
        # Fallback for anthropic: $3/1M input
        assert cost == 3.0

    def test_calculate_cost_unknown_provider_returns_zero(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "unknown_provider", "some-model", input_tokens=1000, output_tokens=500
        )
        assert cost == 0.0

    def test_calculate_cost_gemini_fallback(self):
        tracker = CostTracker()
        cost = tracker.calculate_cost(
            "gemini", "gemini-unknown", input_tokens=1_000_000, output_tokens=0
        )
        assert cost == 0.5

    def test_normalize_model_name_exact_match(self):
        tracker = CostTracker()
        result = tracker._normalize_model_name("anthropic", "claude-3-sonnet-20240229")
        assert result == "claude-3-sonnet-20240229"

    def test_normalize_model_name_partial_match(self):
        tracker = CostTracker()
        result = tracker._normalize_model_name("anthropic", "claude-3-5-sonnet")
        assert result == "claude-3-5-sonnet-20241022"

    def test_normalize_model_name_no_match(self):
        tracker = CostTracker()
        result = tracker._normalize_model_name("anthropic", "nonexistent-model")
        assert result == "nonexistent-model"

    def test_record_cost(self):
        tracker = CostTracker()
        record = tracker.record_cost("anthropic", "claude-3-haiku-20240307", 1000, 500)
        assert isinstance(record, CostRecord)
        assert record.provider == "anthropic"
        assert record.input_tokens == 1000
        assert record.output_tokens == 500
        assert record.cost_usd > 0
        assert len(tracker.get_records()) == 1

    def test_get_total_cost(self):
        tracker = CostTracker()
        tracker.record_cost("openai", "gpt-3.5-turbo", 1_000_000, 0)
        tracker.record_cost("openai", "gpt-3.5-turbo", 0, 1_000_000)
        total = tracker.get_total_cost()
        assert total == 0.5 + 1.5  # $0.5 input + $1.5 output

    def test_get_records_returns_copy(self):
        tracker = CostTracker()
        tracker.record_cost("anthropic", "claude-3-haiku-20240307", 100, 50)
        records = tracker.get_records()
        records.clear()
        assert len(tracker.get_records()) == 1  # Original unaffected

    def test_clear(self):
        tracker = CostTracker()
        tracker.record_cost("anthropic", "claude-3-haiku-20240307", 100, 50)
        tracker.clear()
        assert tracker.get_total_cost() == 0.0
        assert tracker.get_records() == []


class TestPricingTable:
    """Tests for the PRICING constant."""

    def test_pricing_has_major_providers(self):
        assert "anthropic" in PRICING
        assert "openai" in PRICING
        assert "gemini" in PRICING

    def test_pricing_has_input_output(self):
        for provider_name, models in PRICING.items():
            for model_name, prices in models.items():
                assert "input" in prices, f"{provider_name}/{model_name} missing input"
                assert "output" in prices, f"{provider_name}/{model_name} missing output"
                assert prices["input"] > 0
                assert prices["output"] > 0


class TestGetCostTracker:
    """Tests for the global cost tracker accessor."""

    def test_returns_cost_tracker(self):
        tracker = get_cost_tracker()
        assert isinstance(tracker, CostTracker)

    def test_singleton(self):
        t1 = get_cost_tracker()
        t2 = get_cost_tracker()
        assert t1 is t2
