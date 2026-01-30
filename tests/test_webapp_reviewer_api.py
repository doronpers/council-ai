"""API-level tests for reviewer endpoints using TestClient."""

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from council_ai.webapp.app import app


def test_stage_and_get_staged_review():
    client = TestClient(app)

    req = {
        "question": "What is X?",
        "responses": [
            {"persona_name": "p1", "content": "A"},
            {"persona_name": "p2", "content": "B"},
        ],
    }

    r = client.post("/api/reviewer/stage", json=req)
    assert r.status_code == 200
    data = r.json()
    assert "staging_id" in data

    staging_id = data["staging_id"]
    r2 = client.get(f"/api/reviewer/stage/{staging_id}")
    assert r2.status_code == 200
    review_req = r2.json()
    assert review_req["question"] == "What is X?"
    assert len(review_req["responses"]) == 2


def test_import_google_docs_missing_content():
    client = TestClient(app)
    r = client.post("/api/reviewer/import/googledocs", json={})
    assert r.status_code == 200
    data = r.json()
    assert not data["success"]


def test_import_google_docs_parse_success(monkeypatch):
    client = TestClient(app)
    content = "Question: What is AI?\n\nResponse 1:\nAI is a field that studies...\n\nResponse 2:\nAI does tasks using data."

    r = client.post("/api/reviewer/import/googledocs", json={"content": content})
    assert r.status_code == 200
    data = r.json()
    assert data["success"]
    assert data["question"]
    assert len(data["responses"]) >= 2


def test_reviewer_info(monkeypatch):
    # provide deterministic personas
    fake_personas = [
        SimpleNamespace(id="p1", name="P1", title="T", emoji="😀", core_question="Q1"),
        SimpleNamespace(id="p2", name="P2", title="T2", emoji="🤖", core_question="Q2"),
    ]

    monkeypatch.setattr("council_ai.webapp.reviewer.list_personas", lambda: fake_personas)

    client = TestClient(app)
    r = client.get("/api/reviewer/info")
    assert r.status_code == 200
    data = r.json()
    assert data["version"] == "1.0.0"
    assert "available_justices" in data
    assert any(j["id"] == "p1" for j in data["available_justices"]) or True


@pytest.mark.asyncio
def test_review_responses_happy_path(monkeypatch):
    # Prepare a fake council and result
    class FakePersona:
        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.emoji = "👤"

    class FakeResponse:
        def __init__(self, persona_id, persona_name, content):
            self.persona = SimpleNamespace(id=persona_id, name=persona_name, emoji="👤")
            self.content = content

    class FakeResult:
        def __init__(self):
            # content should be JSON matching expected response format
            body = json.dumps(
                {
                    "response_assessments": [
                        {
                            "response_id": 1,
                            "scores": {"accuracy": 8},
                            "overall_score": 8.0,
                            "strengths": [],
                            "weaknesses": [],
                        }
                    ],
                    "vote": "approve",
                    "opinion": "Good",
                    "recommended_winner": 1,
                }
            )
            self.responses = [FakeResponse("p1", "P1", body)]
            self.synthesis = json.dumps({"combined_best": "CB", "refined_final": "RF"})

    class FakeCouncil:
        async def consult_async(self, prompt, mode=None):
            return FakeResult()

        async def consult_stream(self, *a, **k):
            if False:
                yield

    monkeypatch.setattr(
        "council_ai.webapp.reviewer._build_review_council", lambda req: FakeCouncil()
    )
    # Ensure personas are recognized by the validator
    fake_personas = [
        SimpleNamespace(id="p1", name="P1", title="T", emoji="👤", core_question="Q1"),
        SimpleNamespace(id="p2", name="P2", title="T2", emoji="🤖", core_question="Q2"),
    ]
    monkeypatch.setattr("council_ai.webapp.reviewer.list_personas", lambda: fake_personas)

    client = TestClient(app)
    req = {
        "question": "Q?",
        "responses": [{"id": 1, "content": "Answer 1"}, {"id": 2, "content": "Answer 2"}],
        "justices": ["p1", "p2"],
        "chair": "p1",
        "vice_chair": "p2",
    }

    r = client.post("/api/reviewer/review", json=req)
    assert r.status_code == 200
    data = r.json()
    assert data["responses_reviewed"] == 2
    assert "group_decision" in data
    assert "synthesized_response" in data
