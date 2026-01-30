from datetime import datetime
from uuid import uuid4

import pytest

from council_ai.core.history import ConsultationHistory
from council_ai.core.persona import Persona
from council_ai.core.session import ConsultationResult, MemberResponse, Session


def test_session_serialization():
    """Test that Session objects can be serialized and deserialized."""
    session = Session(
        session_id=str(uuid4()),
        council_name="Test Council",
        members=["persona1", "persona2"],
        metadata={"key": "value"},
    )

    data = session.to_dict()
    assert data["session_id"] == session.session_id
    assert data["council_name"] == "Test Council"
    assert data["members"] == ["persona1", "persona2"]
    assert data["metadata"] == {"key": "value"}

    restored = Session.from_dict(data)
    assert restored.session_id == session.session_id
    assert restored.council_name == session.council_name
    assert restored.metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_sqlite_fts5_search(tmp_path):
    """Test that FTS5 search works in SQLite backend."""
    db_path = tmp_path / "test_history.db"
    history = ConsultationHistory(storage_path=str(tmp_path), use_sqlite=True)
    history.db_path = str(db_path)
    history._init_db()

    # Create a result
    persona = Persona(id="test", name="Tester", title="Test", core_question="?", razor=".")
    response = MemberResponse(
        persona=persona,
        content="The quick brown fox jumps over the lazy dog.",
        timestamp=datetime.now(),
    )
    result = ConsultationResult(
        query="Testing FTS5 search capability",
        responses=[response],
        synthesis="The fox jumped over the dog.",
        mode="individual",
        timestamp=datetime.now(),
    )
    result.session_id = str(uuid4())

    history.save(result)

    # Search for "fox"
    results = history.search("fox")
    assert len(results) > 0
    # The search results for SQLite FTS5 return the full consultation data
    assert any("fox" in r["query"] or "fox" in r.get("synthesis", "") for r in results)

    # Search for "capability" (only in query)
    results = history.search("capability")
    assert len(results) > 0
    assert "Testing" in results[0]["query"]


def test_session_persistence(tmp_path):
    """Test saving and loading sessions."""
    history = ConsultationHistory(storage_path=str(tmp_path), use_sqlite=True)
    session = Session(
        session_id=str(uuid4()), council_name="Persistence Council", members=["m1", "m2"]
    )

    history.save_session(session)

    # List sessions
    sessions = history.list_sessions()
    assert len(sessions) > 0
    assert any(s["id"] == session.session_id for s in sessions)

    # Load session
    loaded = history.load_session(session.session_id)
    assert loaded is not None
    assert loaded.session_id == session.session_id
    assert loaded.council_name == "Persistence Council"
