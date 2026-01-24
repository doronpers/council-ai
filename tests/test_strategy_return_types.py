"""Strategy execute return type compatibility tests."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from council_ai import Council, Persona
from council_ai.core.council import ConsultationMode
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult(monkeypatch):
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_council_handles_strategy_returning_list(monkeypatch):
    council = Council(api_key="test-key")

    # Create a fake strategy that returns a list of MemberResponse
    persona = Persona(id="T2", name="Test2", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona, content="ListAdvice", timestamp=datetime.now()
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return [member_response]

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "ListAdvice"


@pytest.mark.anyio
async def test_council_preserves_prepopulated_synthesis(monkeypatch):
    """Test that pre-populated synthesis in ConsultationResult is not overwritten."""
    council = Council(api_key="test-key")
    council.config.mode = ConsultationMode.SYNTHESIS

    persona = Persona(id="T3", name="Test3", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    # Strategy returns ConsultationResult with pre-populated synthesis
    fake_result = ConsultationResult(
        query="Test Q", responses=[member_response], synthesis="Pre-populated synthesis"
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    # Verify the pre-populated synthesis is preserved
    assert result.synthesis == "Pre-populated synthesis"


@pytest.mark.anyio
async def test_council_merges_computed_synthesis(monkeypatch):
    """Test that council-computed synthesis is merged into ConsultationResult without synthesis."""
    council = Council(api_key="test-key")
    council.config.mode = ConsultationMode.SYNTHESIS

    persona = Persona(id="T4", name="Test4", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    # Strategy returns ConsultationResult WITHOUT synthesis
    fake_result = ConsultationResult(query="Test Q", responses=[member_response], synthesis=None)

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Mock synthesis generation to return a specific value
    async def mock_generate_synthesis(provider, query, context, responses):
        return "Council-computed synthesis"

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())
    monkeypatch.setattr(council, "_generate_synthesis", mock_generate_synthesis)
    monkeypatch.setattr(council, "_get_synthesis_provider", lambda provider: mock_provider)

    result = await council.consult_async("Test Q")

    # Verify the council-computed synthesis is merged in
    assert result.synthesis == "Council-computed synthesis"


@pytest.mark.anyio
async def test_council_fills_partial_fields(monkeypatch):
    """Test that fallback logic fills in missing context, mode, and timestamp."""
    council = Council(api_key="test-key")

    persona = Persona(id="T5", name="Test5", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    # Strategy returns ConsultationResult with missing context, mode, timestamp
    fake_result = ConsultationResult(
        query="Test Q", responses=[member_response], context=None, mode=None, timestamp=None
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q", context="Test context")

    # Verify fallback values were set
    assert result.context == "Test context"
    assert result.mode == ConsultationMode.SYNTHESIS.value  # Default mode
    assert result.timestamp is not None  # Should be set to current time


@pytest.mark.anyio
async def test_synthesis_mode_triggers_synthesis_generation(monkeypatch):
    """Test that SYNTHESIS mode triggers synthesis generation when using legacy list return."""
    council = Council(api_key="test-key")
    council.config.mode = ConsultationMode.SYNTHESIS

    persona = Persona(id="T6", name="Test6", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    class DummyStrategy:
        async def execute(self, **kwargs):
            # Legacy behavior: return list
            return [member_response]

    # Mock synthesis generation
    async def mock_generate_synthesis(provider, query, context, responses):
        return "Generated synthesis for SYNTHESIS mode"

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())
    monkeypatch.setattr(council, "_generate_synthesis", mock_generate_synthesis)
    monkeypatch.setattr(council, "_get_synthesis_provider", lambda provider: mock_provider)

    result = await council.consult_async("Test Q")

    # Verify synthesis was generated
    assert result.synthesis == "Generated synthesis for SYNTHESIS mode"
    assert result.mode == ConsultationMode.SYNTHESIS.value


@pytest.mark.anyio
async def test_debate_mode_triggers_synthesis_generation(monkeypatch):
    """Test that DEBATE mode triggers synthesis generation when using legacy list return."""
    council = Council(api_key="test-key")
    council.config.mode = ConsultationMode.DEBATE

    persona = Persona(id="T7", name="Test7", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    class DummyStrategy:
        async def execute(self, **kwargs):
            # Legacy behavior: return list
            return [member_response]

    # Mock synthesis generation
    async def mock_generate_synthesis(provider, query, context, responses):
        return "Generated synthesis for DEBATE mode"

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())
    monkeypatch.setattr(council, "_generate_synthesis", mock_generate_synthesis)
    monkeypatch.setattr(council, "_get_synthesis_provider", lambda provider: mock_provider)

    result = await council.consult_async("Test Q")

    # Verify synthesis was generated
    assert result.synthesis == "Generated synthesis for DEBATE mode"
    assert result.mode == ConsultationMode.DEBATE.value


@pytest.mark.anyio
async def test_individual_mode_no_synthesis(monkeypatch):
    """Test that INDIVIDUAL mode does not trigger synthesis generation."""
    council = Council(api_key="test-key")
    council.config.mode = ConsultationMode.INDIVIDUAL

    persona = Persona(id="T8", name="Test8", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Response", timestamp=datetime.now())

    class DummyStrategy:
        async def execute(self, **kwargs):
            # Legacy behavior: return list
            return [member_response]

    # Mock provider and strategy
    mock_provider = MagicMock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    # Verify NO synthesis was generated for INDIVIDUAL mode
    assert result.synthesis is None
    assert result.mode == ConsultationMode.INDIVIDUAL.value
