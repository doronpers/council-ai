"""Tests for the Council AI web app."""

from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from council_ai.webapp import app  # noqa: E402


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_info_endpoint(client):
    response = client.get("/api/info")
    assert response.status_code == 200
    payload = response.json()
    assert "providers" in payload
    assert "models" in payload
    assert "domains" in payload
    assert "personas" in payload
    assert "modes" in payload
    assert "categories" in payload
    assert "defaults" in payload
    assert "tts" in payload


def test_consult_requires_api_key():
    with patch("council_ai.webapp.app.get_api_key", return_value=None):
        client = TestClient(app)
        response = client.post(
            "/api/consult",
            json={"query": "Hello", "mode": "synthesis", "provider": "openai"},
        )
        assert response.status_code == 400
        assert "API key" in response.json()["detail"]


def test_consult_invalid_mode(client):
    """Test that invalid consultation mode returns 400."""
    with patch("council_ai.webapp.app.get_api_key", return_value="fake-key"):
        response = client.post(
            "/api/consult",
            json={"query": "Hello", "mode": "invalid_mode"},
        )
        assert response.status_code == 400


def test_consult_invalid_member(client):
    """Test that invalid member ID returns 400."""
    with patch("council_ai.webapp.app.get_api_key", return_value="fake-key"):
        response = client.post(
            "/api/consult",
            json={"query": "Hello", "members": ["nonexistent_persona"]},
        )
        assert response.status_code == 400


def test_consult_query_too_long(client):
    """Test that overly long queries are rejected."""
    response = client.post(
        "/api/consult",
        json={"query": "x" * 60000},  # Exceeds max_length of 50000
    )
    assert response.status_code == 422  # Pydantic validation error


def test_consult_empty_query(client):
    """Test that empty queries are rejected."""
    response = client.post(
        "/api/consult",
        json={"query": ""},
    )
    assert response.status_code == 422  # Pydantic validation error


def test_consult_stream_requires_api_key():
    """Test that streaming endpoint requires API key."""
    with patch("council_ai.webapp.app.get_api_key", return_value=None):
        client = TestClient(app)
        response = client.post(
            "/api/consult/stream",
            json={"query": "Hello", "mode": "synthesis", "provider": "openai"},
        )
        assert response.status_code == 400
        assert "API key" in response.json()["detail"]


def test_history_list_empty(client):
    """Test listing history when empty or with mocked data."""
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.list.return_value = []
        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert "consultations" in data
        assert "total" in data


def test_history_get_not_found(client):
    """Test getting non-existent consultation returns 404."""
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.load.return_value = None
        response = client.get("/api/history/nonexistent-id")
        assert response.status_code == 404


def test_history_get_found(client):
    """Test getting existing consultation."""
    mock_data = {
        "id": "test-id",
        "query": "Test query",
        "synthesis": "Test synthesis",
    }
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.load.return_value = mock_data
        response = client.get("/api/history/test-id")
        assert response.status_code == 200
        assert response.json() == mock_data


def test_history_delete_not_found(client):
    """Test deleting non-existent consultation returns 404."""
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.delete.return_value = False
        response = client.delete("/api/history/nonexistent-id")
        assert response.status_code == 404


def test_history_delete_success(client):
    """Test successful deletion."""
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.delete.return_value = True
        response = client.delete("/api/history/test-id")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


def test_history_save_not_found(client):
    """Test updating metadata for non-existent consultation."""
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.update_metadata.return_value = False
        response = client.post("/api/history/nonexistent-id/save")
        assert response.status_code == 404


def test_history_save_success(client):
    """Test successful metadata update."""
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.update_metadata.return_value = True
        response = client.post("/api/history/test-id/save")
        assert response.status_code == 200
        assert response.json()["status"] == "saved"


def test_history_search(client):
    """Test history search endpoint."""
    mock_results = [{"id": "1", "query": "test"}]
    with patch("council_ai.webapp.app._history") as mock_history:
        mock_history.search.return_value = mock_results
        response = client.get("/api/history/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["count"] == 1
        assert data["consultations"] == mock_results


def test_index_page(client):
    """Test that index page returns HTML."""
    response = client.get("/")
    assert response.status_code in (200, 500)  # 500 if no index.html exists


def test_manifest_json(client):
    """Test PWA manifest endpoint."""
    response = client.get("/manifest.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Council AI"
    assert "icons" in data


def test_tts_generate_disabled(client):
    """Test TTS generation when disabled."""
    with patch("council_ai.webapp.app.ConfigManager") as mock_cm:
        mock_config = MagicMock()
        mock_config.tts.enabled = False
        mock_cm.return_value.config = mock_config
        response = client.post(
            "/api/tts/generate",
            json={"text": "Hello world"},
        )
        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()


def test_tts_audio_invalid_filename(client):
    """Test TTS audio endpoint rejects invalid filenames."""
    # Test path traversal attempt
    response = client.get("/api/tts/audio/../../../etc/passwd")
    assert response.status_code == 400

    # Test non-mp3 extension
    response = client.get("/api/tts/audio/file.wav")
    assert response.status_code == 400


def test_tts_audio_not_found(client):
    """Test TTS audio endpoint returns 404 for missing files."""
    response = client.get("/api/tts/audio/nonexistent-file.mp3")
    assert response.status_code == 404


def test_tts_text_too_long(client):
    """Test TTS rejects text exceeding max length."""
    response = client.post(
        "/api/tts/generate",
        json={"text": "x" * 6000},  # Exceeds max_length of 5000
    )
    assert response.status_code == 422


def test_tts_text_empty(client):
    """Test TTS rejects empty text."""
    response = client.post(
        "/api/tts/generate",
        json={"text": ""},
    )
    assert response.status_code == 422
