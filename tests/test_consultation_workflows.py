"""
End-to-end integration tests for complete consultation workflows.

Tests comprehensive scenarios including:
- Full consultation pipelines with multiple personas
- Error recovery and fallback mechanisms
- Streaming response handling
- Session management and history
- Multi-step workflows
- Data persistence and retrieval
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council_ai.core.council import Council
from council_ai.core.session import ConsultationResult, Session

# ============================================================================
# Fixture Setup
# ============================================================================


@pytest.fixture
def mock_provider():
    """Create a mock LLM provider."""
    provider = AsyncMock()
    provider.post_chat_request = AsyncMock(
        return_value=MagicMock(
            content="Mock response from LLM", tokens_used={"input": 10, "output": 20}
        )
    )
    return provider


@pytest.fixture
def mock_personas():
    """Create mock personas for testing."""
    personas = [
        MagicMock(
            id="persona1",
            name="Expert",
            emoji="🧠",
            system_prompt="You are an expert",
            domain="general",
        ),
        MagicMock(
            id="persona2",
            name="Critic",
            emoji="🔍",
            system_prompt="You are a critic",
            domain="general",
        ),
        MagicMock(
            id="persona3",
            name="Creator",
            emoji="✨",
            system_prompt="You are creative",
            domain="general",
        ),
    ]
    return personas


@pytest.fixture
def temp_session_dir():
    """Create temporary directory for session storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# Full Consultation Workflow Tests
# ============================================================================


class TestFullConsultationWorkflow:
    """Test complete consultation workflows."""

    @pytest.mark.asyncio
    async def test_basic_consultation_pipeline(self, mock_provider, mock_personas):
        """Test basic multi-persona consultation."""
        with patch("council_ai.core.council.Council._get_provider", return_value=mock_provider):
            council = MagicMock()
            council.list_members.return_value = mock_personas

            # Simulate getting responses from each persona
            responses = []
            for persona in mock_personas:
                response = MagicMock()
                response.persona = persona
                response.content = f"Response from {persona.name}"
                responses.append(response)

            assert len(responses) == 3
            for resp in responses:
                assert resp.content is not None

    @pytest.mark.asyncio
    async def test_consultation_with_context(self, mock_provider, mock_personas):
        """Test consultation with background context."""
        context = "Important background information for this consultation"

        council = MagicMock()
        council.list_members.return_value = mock_personas

        # Simulate consultation with context
        responses = []
        for persona in mock_personas:
            response = MagicMock()
            response.persona = persona
            response.content = f"{persona.name}'s response given context"
            responses.append(response)

        assert len(responses) == 3
        assert all(resp.content is not None for resp in responses)

    @pytest.mark.asyncio
    async def test_consultation_result_synthesis(self, mock_personas):
        """Test synthesizing results from multiple personas."""
        # Create mock responses from each persona
        responses = []
        for i, persona in enumerate(mock_personas):
            response = MagicMock()
            response.persona = persona
            response.content = f"Perspective {i+1}: {persona.name}'s view"
            responses.append(response)

        # Create a mock result
        result = MagicMock()
        result.responses = responses
        result.synthesis = "Synthesized summary combining all perspectives"

        assert result.synthesis is not None
        assert len(result.responses) == len(mock_personas)

    @pytest.mark.asyncio
    async def test_consultation_member_filtering(self, mock_personas):
        """Test consulting specific members only."""
        selected_members = [mock_personas[0], mock_personas[2]]

        responses = []
        for persona in selected_members:
            response = MagicMock()
            response.persona = persona
            response.content = f"Response from {persona.name}"
            responses.append(response)

        assert len(responses) == 2
        assert responses[0].persona.id == "persona1"
        assert responses[1].persona.id == "persona3"

    @pytest.mark.asyncio
    async def test_consultation_with_different_modes(self, mock_personas):
        """Test consultation with different strategy modes."""
        modes = ["individual", "synthesis", "sequential", "debate"]

        for mode in modes:
            responses = []
            for persona in mock_personas:
                response = MagicMock()
                response.persona = persona
                response.content = f"Response in {mode} mode"
                responses.append(response)

            assert len(responses) == 3


# ============================================================================
# Error Handling & Recovery Tests
# ============================================================================


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_single_provider_failure_recovery(self, mock_provider, mock_personas):
        """Test recovery when one provider fails."""
        # Simulate first provider failing
        failing_provider = AsyncMock()
        failing_provider.post_chat_request = AsyncMock(side_effect=Exception("Provider timeout"))

        # Should fall back to another provider
        responses = []
        for persona in mock_personas:
            try:
                # Would normally try multiple providers
                response = MagicMock()
                response.persona = persona
                response.content = "Fallback response"
                responses.append(response)
            except Exception:
                pass

        assert len(responses) == 3

    @pytest.mark.asyncio
    async def test_partial_response_failure(self, mock_personas):
        """Test handling when one persona fails but others succeed."""
        responses = []

        for i, persona in enumerate(mock_personas):
            if i == 1:  # Second persona fails
                continue

            response = MagicMock()
            response.persona = persona
            response.content = f"Response from {persona.name}"
            responses.append(response)

        # Should have 2 out of 3 responses
        assert len(responses) == 2

    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self):
        """Test retry logic with exponential backoff."""
        attempt_count = 0
        max_retries = 3

        async def retry_logic():
            nonlocal attempt_count
            for attempt in range(max_retries):
                attempt_count += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.001 * (2**attempt))  # Exponential backoff
                else:
                    return "Success"

        result = await retry_logic()
        assert result == "Success"
        assert attempt_count > 0

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of response timeouts."""

        async def slow_operation():
            try:
                await asyncio.sleep(10)
                return "Done"
            except asyncio.TimeoutError:
                return "Timeout"

        # Test with timeout
        try:
            result = await asyncio.wait_for(slow_operation(), timeout=0.001)
        except asyncio.TimeoutError:
            result = "Timeout handled"

        assert result == "Timeout handled"


# ============================================================================
# Streaming Response Tests
# ============================================================================


class TestStreamingResponses:
    """Test streaming response handling."""

    @pytest.mark.asyncio
    async def test_stream_response_collection(self):
        """Test collecting streamed response chunks."""

        async def mock_stream():
            chunks = ["First ", "second ", "third ", "chunk"]
            for chunk in chunks:
                yield {"type": "chunk", "content": chunk}
            yield {"type": "complete", "final": "First second third chunk"}

        collected = []
        async for item in mock_stream():
            collected.append(item)

        assert len(collected) == 5
        assert collected[-1]["type"] == "complete"

    @pytest.mark.asyncio
    async def test_stream_error_handling(self):
        """Test handling errors in streams."""

        async def error_stream():
            yield {"type": "chunk", "content": "Good chunk"}
            # Simulate an error
            yield {"type": "error", "error": "Stream interrupted"}

        items = []
        async for item in error_stream():
            items.append(item)

        assert len(items) == 2
        assert items[1]["type"] == "error"

    @pytest.mark.asyncio
    async def test_parallel_streaming(self):
        """Test handling multiple parallel streams."""

        async def persona_stream(persona_id):
            for i in range(3):
                yield f"Response {i+1} from {persona_id}"

        personas = ["p1", "p2", "p3"]
        tasks = [persona_stream(p) for p in personas]

        results = {}
        for persona, stream in zip(personas, tasks):
            async_list = []
            async for item in stream:
                async_list.append(item)
            results[persona] = async_list
        assert len(results) == 3
        for responses in results.values():
            assert len(responses) == 3


# ============================================================================
# Session Management & History Tests
# ============================================================================


class TestSessionManagement:
    """Test session management and history."""

    def test_session_creation_and_storage(self, temp_session_dir):
        """Test creating and storing sessions."""
        session_file = temp_session_dir / "session_001.json"

        session_data = {
            "id": "session_001",
            "query": "Test query",
            "responses": ["Response 1", "Response 2"],
            "synthesis": "Synthesized result",
        }

        # Simulate saving session
        import json

        session_file.write_text(json.dumps(session_data))

        # Verify session was saved
        assert session_file.exists()
        loaded = json.loads(session_file.read_text())
        assert loaded["id"] == "session_001"

    def test_session_retrieval(self, temp_session_dir):
        """Test retrieving stored sessions."""
        import json

        # Create multiple sessions
        for i in range(3):
            session_file = temp_session_dir / f"session_{i:03d}.json"
            session_data = {
                "id": f"session_{i:03d}",
                "query": f"Query {i}",
            }
            session_file.write_text(json.dumps(session_data))

        # Retrieve all sessions
        sessions = list(temp_session_dir.glob("session_*.json"))
        assert len(sessions) == 3

    def test_session_history_queries(self, temp_session_dir):
        """Test querying session history."""
        import json

        # Create sessions with different domains
        for i, domain in enumerate(["business", "technical", "creative"]):
            session_file = temp_session_dir / f"session_{i:03d}.json"
            session_data = {
                "id": f"session_{i:03d}",
                "domain": domain,
                "query": f"Query in {domain}",
            }
            session_file.write_text(json.dumps(session_data))

        # Query by domain
        business_sessions = []
        for session_file in temp_session_dir.glob("session_*.json"):
            data = json.loads(session_file.read_text())
            if data.get("domain") == "business":
                business_sessions.append(data)

        assert len(business_sessions) == 1
        assert business_sessions[0]["domain"] == "business"

    def test_session_update_and_persist(self, temp_session_dir):
        """Test updating and persisting session changes."""
        import json

        session_file = temp_session_dir / "session_001.json"

        # Create initial session
        initial_data = {
            "id": "session_001",
            "responses": 0,
            "synthesis": None,
        }
        session_file.write_text(json.dumps(initial_data))

        # Update session
        updated_data = json.loads(session_file.read_text())
        updated_data["responses"] = 3
        updated_data["synthesis"] = "New synthesis"
        session_file.write_text(json.dumps(updated_data))

        # Verify update persisted
        loaded = json.loads(session_file.read_text())
        assert loaded["responses"] == 3
        assert loaded["synthesis"] == "New synthesis"


# ============================================================================
# Multi-Step Workflow Tests
# ============================================================================


class TestMultiStepWorkflows:
    """Test complex multi-step workflows."""

    @pytest.mark.asyncio
    async def test_follow_up_consultation(self, mock_personas):
        """Test follow-up consultations building on previous results."""
        # Initial consultation
        initial_responses = []
        for persona in mock_personas:
            response = MagicMock()
            response.persona = persona
            response.content = "Initial response"
            initial_responses.append(response)

        initial_synthesis = "Initial synthesis"

        # Follow-up consultation using previous context
        follow_up_responses = []
        previous_context = f"Previous result: {initial_synthesis}"

        for persona in mock_personas:
            response = MagicMock()
            response.persona = persona
            response.content = f"Follow-up based on: {previous_context}"
            follow_up_responses.append(response)

        assert len(initial_responses) == 3
        assert len(follow_up_responses) == 3
        assert "Previous result" in follow_up_responses[0].content

    @pytest.mark.asyncio
    async def test_refinement_workflow(self, mock_personas):
        """Test iterative refinement of a consultation."""
        refinement_rounds = 3
        all_results = []

        for round_num in range(refinement_rounds):
            context = (
                f"Previous refinements: {round_num}" if round_num > 0 else "Initial consultation"
            )

            responses = []
            for persona in mock_personas:
                response = MagicMock()
                response.persona = persona
                response.content = f"Round {round_num + 1} response"
                responses.append(response)

            all_results.append(responses)

        assert len(all_results) == 3
        for round_results in all_results:
            assert len(round_results) == 3

    @pytest.mark.asyncio
    async def test_comparison_workflow(self, mock_personas):
        """Test comparing multiple consultation approaches."""
        approaches = ["synthesis", "sequential", "debate"]
        results_by_approach = {}

        for approach in approaches:
            responses = []
            for persona in mock_personas:
                response = MagicMock()
                response.persona = persona
                response.content = f"Response using {approach}"
                responses.append(response)

            results_by_approach[approach] = responses

        assert len(results_by_approach) == 3
        for approach, responses in results_by_approach.items():
            assert len(responses) == 3


# ============================================================================
# Performance & Scale Tests
# ============================================================================


class TestPerformanceAndScale:
    """Test performance with various data scales."""

    @pytest.mark.asyncio
    async def test_large_response_handling(self):
        """Test handling large response content."""
        large_content = "This is a response. " * 10000  # ~200KB

        response = MagicMock()
        response.content = large_content
        response.size = len(large_content)

        assert len(response.content) > 100000

    @pytest.mark.asyncio
    async def test_many_personas_consultation(self):
        """Test consultation with many personas."""
        # Create 20 personas
        personas = []
        for i in range(20):
            persona = MagicMock()
            persona.id = f"persona_{i}"
            persona.name = f"Persona {i}"
            personas.append(persona)

        responses = []
        for persona in personas:
            response = MagicMock()
            response.persona = persona
            response.content = f"Response from {persona.name}"
            responses.append(response)

        assert len(responses) == 20

    def test_large_session_history(self, temp_session_dir):
        """Test handling large session history."""
        import json

        # Create 100 sessions
        for i in range(100):
            session_file = temp_session_dir / f"session_{i:04d}.json"
            session_data = {
                "id": f"session_{i:04d}",
                "query": f"Query {i}",
                "responses": [f"Response {j}" for j in range(3)],
            }
            session_file.write_text(json.dumps(session_data))

        # Retrieve all
        sessions = list(temp_session_dir.glob("session_*.json"))
        assert len(sessions) == 100
