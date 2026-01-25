"""Tests for proper cancellation handling in web search and other async operations."""

import asyncio

import pytest

from council_ai.core.council import Council, CouncilConfig
from council_ai.core.persona import Persona
from council_ai.tools.web_search import SearchResponse, WebSearchTool


class FakeWebSearchProvider:
    """Mock web search provider for testing."""

    async def search(self, query, max_results=5):
        """Return empty search results."""
        return SearchResponse(query=query, results=[], total_results=0)


@pytest.mark.asyncio
async def test_batch_enhance_contexts_propagates_cancelled_error(monkeypatch):
    """Test that CancelledError is propagated from web search tasks."""
    # Setup council with web search enabled
    config = CouncilConfig(enable_web_search=True)
    council = Council(api_key="test-key", provider="anthropic", config=config)

    # Mock the web search tool
    fake_tool = WebSearchTool(provider=FakeWebSearchProvider())
    monkeypatch.setattr(council, "_web_search_tool", fake_tool)

    # Create a mock that raises CancelledError
    async def mock_enhance(*args, **kwargs):
        raise asyncio.CancelledError("Task was cancelled")

    # Replace the enhancement method with our mock
    original_enhance = council._enhance_context_with_web_search
    council._enhance_context_with_web_search = mock_enhance

    # Create test personas
    personas = [
        Persona(
            id="test1",
            name="Test1",
            title="Expert1",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
    ]

    try:
        # This should propagate the CancelledError, not swallow it
        with pytest.raises(asyncio.CancelledError):
            await council._batch_enhance_contexts("query", None, personas)
    finally:
        # Restore original method
        council._enhance_context_with_web_search = original_enhance


@pytest.mark.asyncio
async def test_batch_enhance_contexts_propagates_keyboard_interrupt(monkeypatch):
    """Test that KeyboardInterrupt is propagated from web search tasks."""
    # Setup council with web search enabled
    config = CouncilConfig(enable_web_search=True)
    council = Council(api_key="test-key", provider="anthropic", config=config)

    # Mock the web search tool
    fake_tool = WebSearchTool(provider=FakeWebSearchProvider())
    monkeypatch.setattr(council, "_web_search_tool", fake_tool)

    # Create a mock that raises KeyboardInterrupt
    async def mock_enhance(*args, **kwargs):
        raise KeyboardInterrupt("User interrupted")

    # Replace the enhancement method with our mock
    original_enhance = council._enhance_context_with_web_search
    council._enhance_context_with_web_search = mock_enhance

    # Create test personas
    personas = [
        Persona(
            id="test1",
            name="Test1",
            title="Expert1",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
    ]

    try:
        # This should propagate the KeyboardInterrupt, not swallow it
        with pytest.raises(KeyboardInterrupt):
            await council._batch_enhance_contexts("query", None, personas)
    finally:
        # Restore original method
        council._enhance_context_with_web_search = original_enhance


@pytest.mark.asyncio
async def test_batch_enhance_contexts_handles_regular_exceptions(monkeypatch):
    """Test that regular exceptions are logged but don't stop processing."""
    # Setup council with web search enabled
    config = CouncilConfig(enable_web_search=True)
    council = Council(api_key="test-key", provider="anthropic", config=config)

    # Mock the web search tool
    fake_tool = WebSearchTool(provider=FakeWebSearchProvider())
    monkeypatch.setattr(council, "_web_search_tool", fake_tool)

    call_count = {"count": 0}

    # Create a mock that raises a regular exception for first persona, succeeds for second
    async def mock_enhance(query, context, member):
        call_count["count"] += 1
        if member.id == "test1":
            raise ValueError("Regular error in web search")
        return "Enhanced context for " + member.id

    # Replace the enhancement method with our mock
    original_enhance = council._enhance_context_with_web_search
    council._enhance_context_with_web_search = mock_enhance

    # Create test personas
    personas = [
        Persona(
            id="test1",
            name="Test1",
            title="Expert1",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
        Persona(
            id="test2",
            name="Test2",
            title="Expert2",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
    ]

    try:
        # This should not raise, but should return results for successful tasks
        result = await council._batch_enhance_contexts("query", None, personas)

        # Should have called for both personas
        assert call_count["count"] == 2

        # Should only have result for test2 (test1 failed)
        assert "test1" not in result
        assert "test2" in result
        assert "Enhanced context for test2" in result["test2"]
    finally:
        # Restore original method
        council._enhance_context_with_web_search = original_enhance


@pytest.mark.asyncio
async def test_batch_enhance_contexts_mixed_failures(monkeypatch):
    """Test handling mix of cancellation, regular errors, and success."""
    # Setup council with web search enabled
    config = CouncilConfig(enable_web_search=True)
    council = Council(api_key="test-key", provider="anthropic", config=config)

    # Mock the web search tool
    fake_tool = WebSearchTool(provider=FakeWebSearchProvider())
    monkeypatch.setattr(council, "_web_search_tool", fake_tool)

    # Create a mock with different behaviors for different personas
    async def mock_enhance(query, context, member):
        if member.id == "test1":
            return "Success for test1"
        elif member.id == "test2":
            raise ValueError("Regular error")
        elif member.id == "test3":
            # Simulate cancellation happening to one task
            raise asyncio.CancelledError("Cancelled")

    # Replace the enhancement method with our mock
    original_enhance = council._enhance_context_with_web_search
    council._enhance_context_with_web_search = mock_enhance

    # Create test personas
    personas = [
        Persona(
            id="test1",
            name="Test1",
            title="Expert1",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
        Persona(
            id="test2",
            name="Test2",
            title="Expert2",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
        Persona(
            id="test3",
            name="Test3",
            title="Expert3",
            core_question="?",
            razor=".",
            enable_web_search=True,
        ),
    ]

    try:
        # When any task is cancelled, the whole operation should be cancelled
        with pytest.raises(asyncio.CancelledError):
            await council._batch_enhance_contexts("query", None, personas)
    finally:
        # Restore original method
        council._enhance_context_with_web_search = original_enhance
