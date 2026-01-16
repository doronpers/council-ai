"""
Tests for Review Staging API.
"""
import pytest
from fastapi.testclient import TestClient
from council_ai.webapp.app import app

client = TestClient(app)

def test_staging_workflow():
    # 1. Stage a review
    payload = {
        "question": "What is the meaning of life?",
        "responses": [
            {"persona_name": "Plato", "content": "To seek truth."},
            {"persona_name": "Nietzsche", "content": "To become who you are."}
        ]
    }
    response = client.post("/api/reviewer/stage", json=payload)
    assert response.status_code == 200, f"Stage failed: {response.text}"
    data = response.json()
    assert "staging_id" in data
    staging_id = data["staging_id"]
    
    # 2. Retrieve staged review
    response = client.get(f"/api/reviewer/stage/{staging_id}")
    assert response.status_code == 200
    review_data = response.json()
    
    assert review_data["question"] == "What is the meaning of life?"
    assert len(review_data["responses"]) == 2
    assert review_data["responses"][0]["source"] == "Plato"
    assert review_data["responses"][0]["content"] == "To seek truth."
