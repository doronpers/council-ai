import pytest
from pathlib import Path
import sqlite3
import shutil
from council_ai.core.history import ConsultationHistory
from council_ai.core.session import Session
from datetime import datetime

@pytest.fixture
def temp_storage(tmp_path):
    storage = tmp_path / "storage"
    storage.mkdir()
    yield storage
    if storage.exists():
        shutil.rmtree(storage)

def test_delete_session_sqlite(temp_storage):
    history = ConsultationHistory(storage_path=temp_storage, use_sqlite=True)
    
    # Create a session
    session_id = "test-session-1"
    history.save_session(Session(session_id=session_id, council_name="Test Council", members=[]))
    
    # Add a consultation to it
    from council_ai.core.session import MemberResponse, ConsultationResult
    from council_ai.core.persona import Persona
    
    dummy_persona = Persona(
        id="test", 
        name="Test", 
        description="test", 
        title="test", 
        system_prompt="test",
        core_question="test?",
        razor="test"
    )
    
    result = ConsultationResult(
        query="hello",
        responses=[MemberResponse(persona=dummy_persona, content="hi", timestamp=datetime.now())],
        session_id=session_id
    )
    
    history.save(result=result)
    
    # Verify it exists
    sessions = history.list_sessions()
    assert len(sessions) == 1
    
    # Delete the session
    success = history.delete_session(session_id)
    assert success is True
    
    # Verify it's gone
    sessions = history.list_sessions()
    assert len(sessions) == 0
    
    # Verify consultations are gone too
    conn = sqlite3.connect(history.db_path)
    count = conn.execute("SELECT COUNT(*) FROM consultations WHERE session_id = ?", (session_id,)).fetchone()[0]
    assert count == 0
    conn.close()

def test_delete_session_json(temp_storage):
    history = ConsultationHistory(storage_path=temp_storage, use_sqlite=False)
    
    # Create a session
    session_id = "test-session-json"
    history.save_session(Session(session_id=session_id, council_name="Test Council", members=[]))
    
    # Verify file exists
    session_file = temp_storage / "sessions" / f"{session_id}.json"
    assert session_file.exists()
    
    # Delete it
    success = history.delete_session(session_id)
    assert success is True
    
    # Verify file is gone
    assert not session_file.exists()

def test_delete_nonexistent_session(temp_storage):
    history = ConsultationHistory(storage_path=temp_storage, use_sqlite=True)
    success = history.delete_session("ghost")
    assert success is False
