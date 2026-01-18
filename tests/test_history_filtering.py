import json
import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

from council_ai.core.history import ConsultationHistory


@pytest.fixture
def history():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Force SQLite usage
        hist = ConsultationHistory(storage_path=str(temp_dir), use_sqlite=True)
        yield hist


def create_entry(history, query, timestamp, domain=None, mode="synthesis"):
    # Manually insert into DB or use save (if save supports timestamp override?)
    # history.save() uses datetime.now().
    # So we might need to manually insert for specific timestamps or mock datetime.
    # It's easier to manually insert into SQLite for testing specific timestamps.

    # We need to ensure the schema is created first.
    # Accessing history.db_path should verify init.

    conn = sqlite3.connect(history.db_path)
    metadata = {"domain": domain} if domain else {}

    # We need to know the schema.
    # Based on history.py:
    # CREATE TABLE IF NOT EXISTS consultations (
    #     id TEXT PRIMARY KEY,
    #     session_id TEXT,
    #     query TEXT,
    #     context TEXT,
    #     mode TEXT,
    #     timestamp TIMESTAMP,
    #     synthesis TEXT,
    #     responses TEXT,
    #     tags TEXT,
    #     notes TEXT,
    #     metadata TEXT
    # )

    conn.execute(
        """
        INSERT INTO consultations
        (id, session_id, query, context, mode, timestamp, synthesis, responses, tags, notes, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"id_{query}",
            "sess_1",
            query,
            "ctx",
            mode,
            timestamp.isoformat(),
            "synth",
            "[]",
            "[]",
            "",
            json.dumps(metadata),
        ),
    )
    conn.commit()
    conn.close()


def test_filter_by_domain(history):
    create_entry(history, "q1", datetime.now(), domain="coding")
    create_entry(history, "q2", datetime.now(), domain="cooking")
    create_entry(history, "q3", datetime.now(), domain="coding")

    results = history.list(domain="coding")
    assert len(results) == 2
    assert all(r["metadata"]["domain"] == "coding" for r in results)


def test_filter_by_mode(history):
    create_entry(history, "q1", datetime.now(), mode="synthesis")
    create_entry(history, "q2", datetime.now(), mode="debate")

    results = history.list(mode="debate")
    assert len(results) == 1
    assert results[0]["mode"] == "debate"


def test_filter_by_date(history):
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)

    create_entry(history, "today", now)
    create_entry(history, "yesterday", yesterday)
    create_entry(history, "last_week", last_week)

    # Filter for last 2 days
    date_from = (now - timedelta(days=2)).isoformat()
    results = history.list(date_from=date_from)
    assert len(results) == 2  # today and yesterday

    # Filter for specific day range (yesterday only)
    date_from = (yesterday - timedelta(hours=1)).isoformat()
    date_to = (yesterday + timedelta(hours=1)).isoformat()
    results = history.list(date_from=date_from, date_to=date_to)
    assert len(results) == 1
    assert results[0]["query"] == "yesterday"


def test_combined_filters(history):
    now = datetime.now()
    create_entry(history, "match", now, domain="coding", mode="synthesis")
    create_entry(history, "wrong_domain", now, domain="cooking", mode="synthesis")
    create_entry(history, "wrong_mode", now, domain="coding", mode="debate")
    create_entry(history, "wrong_time", now - timedelta(days=10), domain="coding", mode="synthesis")

    results = history.list(
        domain="coding", mode="synthesis", date_from=(now - timedelta(days=1)).isoformat()
    )
    assert len(results) == 1
    assert results[0]["query"] == "match"
