"""
Consultation History - Persistent storage for consultations.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .session import ConsultationResult

logger = logging.getLogger(__name__)


class ConsultationHistory:
    """Manages persistent storage of consultation history."""

    def __init__(self, storage_path: Optional[str] = None, use_sqlite: bool = False):
        """
        Initialize consultation history storage.

        Args:
            storage_path: Path to storage directory (defaults to config directory)
            use_sqlite: If True, use SQLite database; otherwise use JSON files
        """
        if storage_path:
            self.storage_dir = Path(storage_path)
        else:
            # Use config directory
            options = [
                os.environ.get("COUNCIL_CONFIG_DIR"),
                Path.home() / ".config" / "council-ai",
                Path("/tmp/council-ai"),
            ]

            for option in options:
                if not option:
                    continue
                path = Path(option)
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.storage_dir = path / "history"
                    self.storage_dir.mkdir(parents=True, exist_ok=True)
                    break
                except OSError:
                    continue
            else:
                # Fallback
                self.storage_dir = Path.home() / ".council-ai" / "history"
                self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.use_sqlite = use_sqlite
        if use_sqlite:
            self.db_path = self.storage_dir / "consultations.db"
            self._init_db()
        else:
            self.json_dir = self.storage_dir / "json"
            self.json_dir.mkdir(parents=True, exist_ok=True)

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultations (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                context TEXT,
                mode TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                synthesis TEXT,
                responses TEXT NOT NULL,
                tags TEXT,
                notes TEXT,
                metadata TEXT
            )
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON consultations(timestamp)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_query ON consultations(query)
        """
        )
        conn.commit()
        conn.close()

    def save(
        self,
        result: ConsultationResult,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> str:
        """
        Save a consultation result.

        Args:
            result: ConsultationResult to save
            tags: Optional tags for organization
            notes: Optional notes about the consultation

        Returns:
            ID of the saved consultation
        """
        # Generate ID if not present
        if not hasattr(result, "id") or result.id is None:
            consultation_id = str(uuid4())
        else:
            consultation_id = result.id

        data = {
            "id": consultation_id,
            "query": result.query,
            "context": result.context,
            "mode": result.mode,
            "timestamp": result.timestamp.isoformat(),
            "synthesis": result.synthesis,
            "responses": [r.to_dict() for r in result.responses],
            "tags": tags or [],
            "notes": notes,
            "metadata": {},
        }

        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """
                INSERT OR REPLACE INTO consultations
                (id, query, context, mode, timestamp, synthesis, responses, tags, notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    consultation_id,
                    data["query"],
                    data["context"],
                    data["mode"],
                    data["timestamp"],
                    data["synthesis"],
                    json.dumps(data["responses"]),
                    json.dumps(data["tags"]),
                    data["notes"],
                    json.dumps(data["metadata"]),
                ),
            )
            conn.commit()
            conn.close()
        else:
            # Save as JSON file
            json_path = self.json_dir / f"{consultation_id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # Set file permissions
            try:
                os.chmod(json_path, 0o600)
            except OSError:
                pass

        return consultation_id

    def load(self, consultation_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a consultation by ID.

        Args:
            consultation_id: ID of the consultation

        Returns:
            Consultation data dictionary or None if not found
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT * FROM consultations WHERE id = ?", (consultation_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return {
                "id": row[0],
                "query": row[1],
                "context": row[2],
                "mode": row[3],
                "timestamp": row[4],
                "synthesis": row[5],
                "responses": json.loads(row[6]),
                "tags": json.loads(row[7]) if row[7] else [],
                "notes": row[8],
                "metadata": json.loads(row[9]) if row[9] else {},
            }
        else:
            json_path = self.json_dir / f"{consultation_id}.json"
            if not json_path.exists():
                return None

            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def list(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "timestamp",
        reverse: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        List consultations.

        Args:
            limit: Maximum number of results
            offset: Skip N results
            order_by: Field to sort by (timestamp, query)
            reverse: If True, sort descending

        Returns:
            List of consultation summaries
        """
        if self.use_sqlite:
            # Validate order_by to prevent SQL injection
            allowed_order_by = ["timestamp", "query", "mode", "id"]
            if order_by not in allowed_order_by:
                raise ValueError(
                    f"Invalid order_by value: {order_by}. Must be one of {allowed_order_by}"
                )

            conn = sqlite3.connect(self.db_path)
            order = "DESC" if reverse else "ASC"
            query = f"SELECT id, query, mode, timestamp, synthesis FROM consultations ORDER BY {order_by} {order}"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "id": row[0],
                    "query": row[1],
                    "mode": row[2],
                    "timestamp": row[3],
                    "synthesis": row[4],
                }
                for row in rows
            ]
        else:
            # List JSON files
            files = sorted(
                self.json_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=reverse,
            )

            if offset:
                files = files[offset:]
            if limit:
                files = files[:limit]

            results = []
            for json_path in files:
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        results.append(
                            {
                                "id": data.get("id", json_path.stem),
                                "query": data.get("query", ""),
                                "mode": data.get("mode", ""),
                                "timestamp": data.get("timestamp", ""),
                                "synthesis": data.get("synthesis"),
                            }
                        )
                except Exception as e:
                    logger.debug(f"Failed to read consultation file {json_path}: {e}")
                    continue

            return results

    def search(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search consultations by query text.

        Args:
            query: Search query (searches in query, context, synthesis, responses)
            limit: Maximum number of results

        Returns:
            List of matching consultations
        """
        query_lower = query.lower()
        results = []

        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT * FROM consultations")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                # Search in query, context, synthesis, responses
                searchable = f"{row[1]} {row[2] or ''} {row[5] or ''} {row[6]}".lower()
                if query_lower in searchable:
                    results.append(
                        {
                            "id": row[0],
                            "query": row[1],
                            "mode": row[3],
                            "timestamp": row[4],
                            "synthesis": row[5],
                        }
                    )
                    if limit and len(results) >= limit:
                        break
        else:
            for json_path in self.json_dir.glob("*.json"):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Search in query, context, synthesis, responses
                        searchable = (
                            f"{data.get('query', '')} "
                            f"{data.get('context', '')} "
                            f"{data.get('synthesis', '')} "
                            f"{json.dumps(data.get('responses', []))}"
                        ).lower()
                        if query_lower in searchable:
                            results.append(
                                {
                                    "id": data.get("id", json_path.stem),
                                    "query": data.get("query", ""),
                                    "mode": data.get("mode", ""),
                                    "timestamp": data.get("timestamp", ""),
                                    "synthesis": data.get("synthesis"),
                                }
                            )
                            if limit and len(results) >= limit:
                                break
                except Exception as e:
                    logger.debug(f"Failed to read consultation file {json_path}: {e}")
                    continue

        return results

    def delete(self, consultation_id: str) -> bool:
        """
        Delete a consultation.

        Args:
            consultation_id: ID of the consultation to delete

        Returns:
            True if deleted, False if not found
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("DELETE FROM consultations WHERE id = ?", (consultation_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return deleted
        else:
            json_path = self.json_dir / f"{consultation_id}.json"
            if json_path.exists():
                json_path.unlink()
                return True
            return False

    def update_metadata(
        self, consultation_id: str, tags: Optional[List[str]] = None, notes: Optional[str] = None
    ) -> bool:
        """
        Update tags and notes for a consultation.

        Args:
            consultation_id: ID of the consultation
            tags: New tags (None to keep existing)
            notes: New notes (None to keep existing)

        Returns:
            True if updated, False if not found
        """
        consultation = self.load(consultation_id)
        if not consultation:
            return False

        if tags is not None:
            consultation["tags"] = tags
        if notes is not None:
            consultation["notes"] = notes

        # Re-save with updated metadata
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "UPDATE consultations SET tags = ?, notes = ? WHERE id = ?",
                (json.dumps(consultation["tags"]), consultation["notes"], consultation_id),
            )
            conn.commit()
            conn.close()
        else:
            json_path = self.json_dir / f"{consultation_id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(consultation, f, indent=2, ensure_ascii=False)

        return True
