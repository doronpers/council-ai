# tests/test_strategy_return_types.py
"""Strategy execute return type compatibility tests."""

import inspect
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from council_ai import Council, Persona
from council_ai.core.council import ConsultationMode
from council_ai.core.session import ConsultationResult, MemberResponse


@pytest.fixture
def mock_env_keys(monkeypatch):
    """Mock environment variables for API keys."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")


@pytest.fixture
def mock_get_api_key(monkeypatch):
    """Mock get_api_key function."""
    with patch("council_ai.core.council.get_api_key") as mock:
        mock.side_effect = lambda name: f"key-for-{name}"
        yield mock


@pytest.fixture
def mock_get_provider(monkeypatch):
    """Mock _get_provider on Council to avoid real provider initialization."""
    with patch("council_ai.core.council.LLMManager") as llm_manager_cls:
        mock_manager = MagicMock()
        llm_manager_cls.return_value = mock_manager

        def _fake_get_provider(self, fallback: bool = False):
            return object()

        monkeypatch.setattr(Council, "_get_provider", _fake_get_provider)
        yield mock_manager


@pytest.fixture
def mock_llm_manager():
    """Fixture kept for compatibility with other tests that expect it."""
    return MagicMock()


@pytest.mark.anyio
async def test_council_handles_strategy_returning_consultationresult(
    monkeypatch, mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Council should pass through ConsultationResult returned by a strategy."""
    council = Council(api_key="test-key")

    # Defensive: ensure _get_provider returns a dummy provider
    monkeypatch.setattr(council, "_get_provider", lambda fallback=True: object())

    # Create a fake strategy that returns a ConsultationResult
    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona,
        content="Advice",
        timestamp=datetime.now(),
    )
    fake_result = ConsultationResult(query="Test Q", responses=[member_response])

    class DummyStrategy:
        async def execute(self, **kwargs):
            return fake_result

    # Monkeypatch the strategy lookup to return our dummy strategy
    from council_ai.core.strategies import base as strategies_base

    monkeypatch.setattr(
        strategies_base,
        "get_strategy",
        lambda mode_value: DummyStrategy(),
    )

    # Avoid starting a real session
    monkeypatch.setattr(
        council,
        "_start_session",
        lambda *args, **kwargs: MagicMock(session_id="test-session"),
    )

    result = await council.consult_async(
        query="Test Q",
        mode="synthesis",
    )

    assert isinstance(result, ConsultationResult)
    # Should be the exact object returned by the strategy
    assert result is fake_result
    assert result.responses[0].content == "Advice"


@pytest.mark.anyio
async def test_council_handles_strategy_returning_list_of_memberresponses(
    monkeypatch, mock_get_provider, mock_llm_manager, mock_get_api_key, mock_env_keys
):
    """Council should wrap legacy List[MemberResponse] into ConsultationResult."""
    council = Council(api_key="test-key")

    monkeypatch.setattr(council, "_get_provider", lambda fallback=True: object())

    persona = Persona(id="T1", name="Test1", title="T", core_question="?", razor=".")
    member_response = MemberResponse(
        persona=persona,
        content="Legacy",
        timestamp=datetime.now(),
    )
    fake_list = [member_response]

    class LegacyStrategy:
        async def execute(self, **kwargs):
            # Legacy behavior: return list[MemberResponse]
            return fake_list

    from council_ai.core.strategies import base as strategies_base

    monkeypatch.setattr(
        strategies_base,
        "get_strategy",
        lambda mode_value: LegacyStrategy(),
    )

    monkeypatch.setattr(
        council,
        "_start_session",
        lambda *args, **kwargs: MagicMock(session_id="test-session"),
    )

    result = await council.consult_async(
        query="Legacy Q",
        mode="synthesis",
    )

    assert isinstance(result, ConsultationResult)
    assert result.responses == fake_list
    assert result.responses[0].content == "Legacy"


def test_all_built_in_strategies_return_consultationresult_signature():
    """Ensure execute signature of built-in strategies returns ConsultationResult."""
    from council_ai.core.strategies.debate import DebateStrategy
    from council_ai.core.strategies.individual import IndividualStrategy
    from council_ai.core.strategies.synthesis import SynthesisStrategy

    strategies = [DebateStrategy, SynthesisStrategy, IndividualStrategy]

    for strategy_cls in strategies:
        execute_sig = inspect.signature(strategy_cls.execute)
        return_annotation = execute_sig.return_annotation
        assert (
            return_annotation == "ConsultationResult" or return_annotation is ConsultationResult
        ), f"{strategy_cls.__name__}.execute must return ConsultationResult"


@pytest.mark.anyio
async def test_stream_methods_are_async_generators(monkeypatch, mock_env_keys):
    """Ensure stream(...) methods on strategies are async iterators."""
    from council_ai.core.strategies.debate import DebateStrategy
    from council_ai.core.strategies.individual import IndividualStrategy
    from council_ai.core.strategies.synthesis import SynthesisStrategy

    strategies = [DebateStrategy(), SynthesisStrategy(), IndividualStrategy()]

    council = Council(api_key="test-key")

    # Avoid real provider/session
    monkeypatch.setattr(council, "_get_provider", lambda fallback=True: object())
    monkeypatch.setattr(
        council,
        "_start_session",
        lambda *args, **kwargs: MagicMock(session_id="test-session"),
    )

    async def consume_stream(strategy):
        """Helper to consume a few items from stream to verify it is async iterator."""
        stream = strategy.stream(
            council=council,
            query="Test",
            context=None,
            mode=ConsultationMode.SYNTHESIS,
            members=None,
            session_id=None,
            auto_recall=True,
        )
        assert hasattr(stream, "__aiter__")
        assert hasattr(stream, "__anext__")
        # We don't care about contents here; just that it is iterable
        async for _ in stream:
            break

    for strategy in strategies:
        await consume_stream(strategy)


@pytest.mark.anyio
async def test_consult_async_returns_consultationresult(monkeypatch, mock_env_keys):
    """Smoke test: consult_async always returns ConsultationResult for built-in modes."""
    council = Council(api_key="test-key")

    monkeypatch.setattr(council, "_get_provider", lambda fallback=True: object())
    monkeypatch.setattr(
        council,
        "_start_session",
        lambda *args, **kwargs: MagicMock(session_id="test-session"),
    )

    for mode in [
        ConsultationMode.SYNTHESIS,
        ConsultationMode.DEBATE,
        ConsultationMode.INDIVIDUAL,
    ]:
        result = await council.consult_async(query="Test", mode=mode.value)
        assert isinstance(result, ConsultationResult)
        assert result.mode in {mode.value, "debate", "synthesis", "individual"}
