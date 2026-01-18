"""Tests for the analysis module."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from council_ai.core.analysis import AnalysisEngine, AnalysisResult
from council_ai.providers import LLMProvider, LLMResponse


@pytest.mark.asyncio
async def test_analysis_engine_success():
    """Test successful analysis."""
    # Mock provider
    mock_provider = MagicMock(spec=LLMProvider)
    mock_provider.complete = AsyncMock(
        return_value=LLMResponse(
            text="""
        {
            "consensus_score": 85,
            "consensus_summary": "Agreement on main points",
            "key_themes": ["Theme A", "Theme B"],
            "tensions": ["Tension 1"],
            "recommendation": "Do X"
        }
        """,
            model="test-model",
            provider="test-provider",
        )
    )

    engine = AnalysisEngine(mock_provider)
    result = await engine.analyze(
        query="Test query",
        context=None,
        responses=[
            {"persona": {"name": "A"}, "content": "I think X."},
            {"persona": {"name": "B"}, "content": "I agree with X but worry about Y."},
        ],
    )

    assert isinstance(result, AnalysisResult)
    assert result.consensus_score == 85
    assert result.key_themes == ["Theme A", "Theme B"]


@pytest.mark.asyncio
async def test_analysis_engine_failure_fallback():
    """Test fallback on failure."""
    mock_provider = MagicMock(spec=LLMProvider)
    mock_provider.complete = AsyncMock(side_effect=Exception("API Error"))

    engine = AnalysisEngine(mock_provider)
    result = await engine.analyze("Q", None, [])

    assert result.consensus_score == 50
    assert "Analysis failed" in result.consensus_summary
