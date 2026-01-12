"""Tests for the Council AI web app."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from council_ai.webapp import app  # noqa: E402


def test_info_endpoint():
    client = TestClient(app)
    response = client.get("/api/info")
    assert response.status_code == 200
    payload = response.json()
    assert "providers" in payload
    assert "domains" in payload
    assert "personas" in payload


from unittest.mock import patch


def test_consult_requires_api_key():
    with patch("council_ai.webapp.app.get_api_key", return_value=None):
        client = TestClient(app)
        response = client.post(
            "/api/consult",
            json={"query": "Hello", "mode": "synthesis", "provider": "openai"},
        )
        assert response.status_code == 400
