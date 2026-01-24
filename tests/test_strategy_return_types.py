"""Strategy execute return type compatibility tests."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from council_ai import Council, Persona
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult(monkeypatch):
    council = Council(api_key="test-key")

    # Mock the provider
    mock_provider = Mock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)

    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_council_handles_strategy_returning_list(monkeypatch):
    council = Council(api_key="test-key")

    # Mock the provider
    mock_provider = Mock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)

    # Create a fake strategy that returns a list of MemberResponse
    persona = Persona(id="T2", name="Test2", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona, content="ListAdvice", timestamp=datetime.now()
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return [member_response]

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    result = await council.consult_async("Test Q")

    assert isinstance(result, ConsultationResult)
    assert len(result.responses) == 1
    assert result.responses[0].content == "ListAdvice"


@pytest.mark.anyio
async def test_council_skips_synthesis_when_strategy_provides_it(monkeypatch):
    """Test that synthesis generation is skipped when strategy already provides it."""
    from council_ai.core.council import ConsultationMode

    council = Council(api_key="test-key")

    # Mock the provider
    mock_provider = Mock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr(council, "_get_synthesis_provider", lambda provider: mock_provider)

    # Create a fake strategy that returns a ConsultationResult with synthesis
    persona = Persona(id="T3", name="Test3", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())
    fake_result = ConsultationResult(
        query="Test Q",
        responses=[member_response],
        synthesis="Strategy-provided synthesis",
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    # Track if _generate_synthesis was called
    generate_synthesis_called = False
    original_generate_synthesis = council._generate_synthesis

    async def mock_generate_synthesis(*args, **kwargs):
        nonlocal generate_synthesis_called
        generate_synthesis_called = True
        return await original_generate_synthesis(*args, **kwargs)

    monkeypatch.setattr(council, "_generate_synthesis", mock_generate_synthesis)

    # Test with SYNTHESIS mode (which normally triggers synthesis generation)
    result = await council.consult_async("Test Q", mode=ConsultationMode.SYNTHESIS)

    # Verify synthesis was NOT regenerated
    assert (
        not generate_synthesis_called
    ), "_generate_synthesis should not be called when strategy provides synthesis"
    assert result.synthesis == "Strategy-provided synthesis"


@pytest.mark.anyio
async def test_council_skips_structured_synthesis_when_strategy_provides_it(monkeypatch):
    """Test that structured synthesis generation is skipped when strategy already provides it."""
    from council_ai.core.council import ConsultationMode
    from council_ai.core.schemas import ActionItem, SynthesisSchema

    council = Council(api_key="test-key")

    # Mock the provider
    mock_provider = Mock()
    monkeypatch.setattr(council, "_get_provider", lambda fallback=False: mock_provider)
    monkeypatch.setattr(council, "_get_synthesis_provider", lambda provider: mock_provider)

    # Create a fake strategy that returns a ConsultationResult with structured synthesis
    persona = Persona(id="T4", name="Test4", title="T", core_question="?", razor=".")
    member_response = MemberResponse(persona=persona, content="Advice", timestamp=datetime.now())

    structured = SynthesisSchema(
        key_points_of_agreement=["Agreement 1"],
        key_points_of_tension=["Tension 1"],
        synthesized_recommendation="Recommendation",
        action_items=[ActionItem(description="Action 1", priority="high")],
    )

    fake_result = ConsultationResult(
        query="Test Q",
        responses=[member_response],
        structured_synthesis=structured,
    )

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    monkeypatch.setattr("council_ai.core.council.get_strategy", lambda mode: DummyStrategy())

    # Track if _generate_structured_synthesis was called
    generate_structured_synthesis_called = False
    original_generate_structured_synthesis = council._generate_structured_synthesis

    async def mock_generate_structured_synthesis(*args, **kwargs):
        nonlocal generate_structured_synthesis_called
        generate_structured_synthesis_called = True
        return await original_generate_structured_synthesis(*args, **kwargs)

    monkeypatch.setattr(
        council, "_generate_structured_synthesis", mock_generate_structured_synthesis
    )

    # Enable structured output in config
    council.config.use_structured_output = True

    # Test with SYNTHESIS mode (which normally triggers synthesis generation)
    result = await council.consult_async("Test Q", mode=ConsultationMode.SYNTHESIS)

    # Verify structured synthesis was NOT regenerated
    assert (
        not generate_structured_synthesis_called
    ), "_generate_structured_synthesis should not be called when strategy provides it"
    assert result.structured_synthesis == structured
