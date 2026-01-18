"""Consultation History - Persistent storage for consultations."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .session import ConsultationResult, Session

logger = logging.getLogger(__name__)


class ConsultationHistory:
    """Manages persistent storage of consultation history."""

    def __init__(self, storage_path: Optional[str] = None, use_sqlite: bool = True):
        """
        Initialize consultation history storage.

        Args:
            storage_path: Path to storage directory (defaults to config directory)
            use_sqlite: If True, use SQLite database; otherwise use JSON files (default: True)
        """
        if storage_path:
            self.storage_dir = Path(storage_path)
        else:
            # Use config directory
            options = [
                os.environ.get("COUNCIL_CONFIG_DIR"),
                Path.home() / ".config" / "council-ai",
                Path("/tmp/council-ai"),  # nosec B108
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

        self.json_dir = self.storage_dir / "json"
        self.json_dir.mkdir(parents=True, exist_ok=True)

        self.memu_service = None
        self._init_memu()

    def _init_memu(self) -> None:
        """Initialize MemU service if available.

        MemU integration is optional and can be enabled by setting the MEMU_PATH
        environment variable to the path of your memu installation.
        """
        memu_path = os.environ.get("MEMU_PATH")
        if memu_path and os.path.exists(memu_path):
            memu_src = os.path.join(memu_path, "src")
            if os.path.exists(memu_src) and memu_src not in sys.path:
                sys.path.append(memu_src)
            try:
                from memu.app import MemoryService

                self.memu_service = MemoryService(
                    database_config={
                        "metadata_store": {
                            "provider": "sqlite",
                            "path": str(self.storage_dir / "memu_metadata.db"),
                        },
                        "vector_index": {
                            "provider": "faiss",
                            "path": str(self.storage_dir / "memu_vectors"),
                        },
                    }
                )
                logger.info(f"MemU service initialized from {memu_path}")
            except ImportError as e:
                logger.debug(f"Failed to import memu from {memu_path}: {e}")
            except Exception as e:
                logger.debug(f"Failed to initialize MemU: {e}")

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consultations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
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
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                member_ids TEXT,
                started_at TEXT NOT NULL,
                metadata TEXT
            )
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_consultation_session ON consultations(session_id)
        """
        )
        # Create FTS5 virtual table for searching
        try:
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS consultations_fts USING fts5(
                    query,
                    synthesis,
                    content="consultations",
                    content_rowid="rowid"
                )
            """
            )
            # Create triggers to keep FTS index in sync
            conn.execute("DROP TRIGGER IF EXISTS consultations_ai")
            conn.execute(
                """
                CREATE TRIGGER consultations_ai AFTER INSERT ON consultations BEGIN
                  INSERT INTO consultations_fts(rowid, query, synthesis)
                  VALUES (new.rowid, new.query, new.synthesis);
                END
            """
            )
            conn.execute("DROP TRIGGER IF EXISTS consultations_ad")
            conn.execute(
                """
                CREATE TRIGGER consultations_ad AFTER DELETE ON consultations BEGIN
                  INSERT INTO consultations_fts(consultations_fts, rowid, query, synthesis)
                  VALUES('delete', old.rowid, old.query, old.synthesis);
                END
            """
            )
            conn.execute("DROP TRIGGER IF EXISTS consultations_au")
            conn.execute(
                """
                CREATE TRIGGER consultations_au AFTER UPDATE ON consultations BEGIN
                  INSERT INTO consultations_fts(consultations_fts, rowid, query, synthesis)
                  VALUES('delete', old.rowid, old.query, old.synthesis);
                  INSERT INTO consultations_fts(rowid, query, synthesis)
                  VALUES (new.rowid, new.query, new.synthesis);
                END
            """
            )
        except sqlite3.OperationalError as e:
            logger.warning(f"FTS5 not available, falling back to LIKE: {e}")

        conn.commit()
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
        # Create cost_tracking table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consultation_id TEXT,
                session_id TEXT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (consultation_id) REFERENCES consultations(id)
            )
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cost_consultation ON cost_tracking(consultation_id)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cost_session ON cost_tracking(session_id)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cost_timestamp ON cost_tracking(timestamp)
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

        data: Dict[str, Any] = {
            "id": consultation_id,
            "query": result.query,
            "context": result.context,
            "mode": result.mode,
            "timestamp": result.timestamp.isoformat(),
            "synthesis": result.synthesis,
            "responses": [r.to_dict() for r in result.responses],
            "tags": tags or [],
            "notes": notes,
            "session_id": getattr(result, "session_id", None),
            "metadata": {},
        }

        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            # Try to get session_id if it exists on the result object
            session_id = getattr(result, "session_id", None)

            conn.execute(
                """
                INSERT OR REPLACE INTO consultations
                (id, session_id, query, context, mode, timestamp, synthesis, responses, tags,
                notes, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    consultation_id,
                    session_id,
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
        # Save as JSON file
        json_path = self.json_dir / f"{consultation_id}.json"
        # Skip permission error on read-only or restricted systems
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.chmod(json_path, 0o600)
        except OSError:
            pass

        # Also memorize with MemU if available
        if self.memu_service:
            try:
                # Background memorization could be risky in sync context,
                # but for simplicity we'll just run it in a new event loop or thread if needed,
                # however council-ai usually runs in an async environment.
                # Since 'save' is often called from sync code, we use a utility.
                self._memorize_async(data)
            except Exception as e:
                logger.warning(f"MemU memorization failed: {e}")

        return consultation_id

    def _memorize_async(self, data: Dict[str, Any]) -> None:
        """Helper to run MemU memorization in a background thread or task."""
        if not self.memu_service:
            return

        def _run_memu():
            try:
                # We need an event loop to run MemU's async methods
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Format data for MemU resource
                resource_data = json.dumps(data)

                async def _task():
                    await self.memu_service.memorize(
                        resource_content=resource_data,
                        modality="conversation",
                        user={"session_id": data.get("session_id", "default")},
                    )

                loop.run_until_complete(_task())
                loop.close()
            except Exception as e:
                logger.warning(f"Background MemU memorization failed: {e}")

        import threading

        threading.Thread(target=_run_memu, daemon=True).start()

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
                "session_id": row[1],
                "query": row[2],
                "context": row[3],
                "mode": row[4],
                "timestamp": row[5],
                "synthesis": row[6],
                "responses": json.loads(row[7]),
                "tags": json.loads(row[8]) if row[8] else [],
                "notes": row[9],
                "metadata": json.loads(row[10]) if row[10] else {},
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
            query = (
                "SELECT id, query, mode, timestamp, synthesis FROM consultations "
                f"ORDER BY {order_by} {order}"  # nosec B608
            )
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
            try:
                # Try FTS5 search first
                cursor = conn.execute(
                    """
                    SELECT c.* FROM consultations c
                    JOIN consultations_fts f ON c.rowid = f.rowid
                    WHERE consultations_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """,
                    (query, limit or 50),
                )
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                # Fallback to LIKE search
                cursor = conn.execute(
                    """
                    SELECT * FROM consultations
                    WHERE query LIKE ? OR synthesis LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (f"%{query}%", f"%{query}%", limit or 50),
                )
                rows = cursor.fetchall()

            conn.close()
            return [
                {
                    "id": row[0],
                    "session_id": row[1],
                    "query": row[2],
                    "context": row[3],
                    "mode": row[4],
                    "timestamp": row[5],
                    "synthesis": row[6],
                    "responses": json.loads(row[7]),
                    "tags": json.loads(row[8]) if row[8] else [],
                    "notes": row[9],
                    "metadata": json.loads(row[10]) if row[10] else {},
                }
                for row in rows
            ]

        # If SQLite search didn't return enough or if we want to augment with MemU
        if self.memu_service:
            try:
                import asyncio

                # This is tricky because search() is sync.
                # In a real app, search() should be async.
                # For now, we'll try to run retrieve in a one-off loop if possible.
                loop = asyncio.new_event_loop()

                async def _retrieve_task():
                    # We use the query directly for semantic search
                    return await self.memu_service.retrieve(
                        queries=[{"role": "user", "content": {"text": query}}], method="rag"
                    )

                memu_result = loop.run_until_complete(_retrieve_task())
                loop.close()

                # Add MemU findings to results
                for item in memu_result.get("items", []):
                    results.append(
                        {
                            "id": f"memu_{item.get('id')}",
                            "query": f"[MemU] {item.get('summary')}",
                            "mode": "semantic",
                            "timestamp": datetime.now().isoformat(),
                            "synthesis": item.get("content", ""),
                            "metadata": {"type": "memu_item"},
                        }
                    )
            except Exception as e:
                logger.debug(f"MemU retrieval failed during search: {e}")

        # List JSON files (fallback for non-sqlite)
        if not self.use_sqlite:
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

    def save_session(self, session: Session) -> None:
        """Save session metadata."""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """
                INSERT OR REPLACE INTO sessions
                (id, name, member_ids, started_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    session.session_id,
                    session.council_name,
                    json.dumps(session.members),
                    session.started_at.isoformat(),
                    json.dumps(session.metadata),
                ),
            )
            conn.commit()
            conn.close()
        else:
            # Sessions in JSON could be a separate directory or just metadata files
            session_dir = self.storage_dir / "sessions"
            session_dir.mkdir(parents=True, exist_ok=True)
            json_path = session_dir / f"{session.session_id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID."""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None

            session = Session(
                session_id=row[0],
                council_name=row[1],
                members=json.loads(row[2]),
                started_at=datetime.fromisoformat(row[3]),
                metadata=json.loads(row[4]) if row[4] else {},
            )

            # Load consultations for this session
            cursor = conn.execute(
                "SELECT id FROM consultations WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            )
            consult_ids = [r[0] for r in cursor.fetchall()]
            conn.close()

            for cid in consult_ids:
                data = self.load(cid)
                if data:
                    from .session import ConsultationResult

                    session.add_consultation(ConsultationResult.from_dict(data))

            return session
        else:
            session_dir = self.storage_dir / "sessions"
            json_path = session_dir / f"{session_id}.json"
            if not json_path.exists():
                return None
            with open(json_path, "r", encoding="utf-8") as f:
                return Session.from_dict(json.load(f))

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions."""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "SELECT id, name, member_ids, started_at FROM sessions "
                "ORDER BY started_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "members": json.loads(row[2]),
                    "started_at": row[3],
                }
                for row in rows
            ]
        else:
            session_dir = self.storage_dir / "sessions"
            if not session_dir.exists():
                return []
            files = sorted(
                session_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )[:limit]

            results = []
            for f in files:
                try:
                    with open(f, "r", encoding="utf-8") as sfile:
                        data = json.load(sfile)
                        results.append(
                            {
                                "id": data.get("session_id"),
                                "name": data.get("council_name"),
                                "members": data.get("members", []),
                                "started_at": data.get("started_at"),
                            }
                        )
                except Exception:
                    continue
            return results

    def get_recent_context(self, session_id: str, last_n: int = 5) -> str:
        """Get summarized context from recent consultations in a session."""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                """
                SELECT query, synthesis FROM consultations
                WHERE session_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """,
                (session_id, last_n),
            )
            rows = cursor.fetchall()
            conn.close()

            context_parts = []
            for row in reversed(rows):
                query, synthesis = row
                part = f"User: {query}"
                if synthesis:
                    part += f"\nCouncil: {synthesis}"
                context_parts.append(part)

            return "\n\n".join(context_parts)
        return ""

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

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its consultations.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if deleted, False if not found
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            # Delete consultations first
            conn.execute("DELETE FROM consultations WHERE session_id = ?", (session_id,))
            # Delete session metadata
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return deleted
        else:
            session_dir = self.storage_dir / "sessions"
            json_path = session_dir / f"{session_id}.json"

            # Load session to find associated consultations if we wanted to delete them too
            # For JSON, they are just files in the json/ dir.
            # We'd need to grep or load them all to find which belong to this session.
            # For now, let's at least delete the session file.
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

    def save_cost(
        self,
        consultation_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Save cost tracking record.

        Args:
            consultation_id: ID of the consultation
            provider: Provider name
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cost_usd: Cost in USD
            session_id: Optional session ID
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """
                INSERT INTO cost_tracking
                (consultation_id, session_id, provider, model, input_tokens, output_tokens, cost_usd, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    consultation_id,
                    session_id,
                    provider,
                    model,
                    input_tokens,
                    output_tokens,
                    cost_usd,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()

    def get_consultation_costs(self, consultation_id: str) -> List[Dict[str, Any]]:
        """
        Get cost records for a consultation.

        Args:
            consultation_id: ID of the consultation

        Returns:
            List of cost records
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                """
                SELECT provider, model, input_tokens, output_tokens, cost_usd, timestamp
                FROM cost_tracking
                WHERE consultation_id = ?
                ORDER BY timestamp
            """,
                (consultation_id,),
            )
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "provider": row[0],
                    "model": row[1],
                    "input_tokens": row[2],
                    "output_tokens": row[3],
                    "cost_usd": row[4],
                    "timestamp": row[5],
                }
                for row in rows
            ]
        return []

    def get_session_costs(self, session_id: str) -> Dict[str, Any]:
        """
        Get cost summary for a session.

        Args:
            session_id: ID of the session

        Returns:
            Dictionary with total cost and breakdown
        """
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                """
                SELECT
                    COUNT(DISTINCT consultation_id) as consultation_count,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(cost_usd) as total_cost
                FROM cost_tracking
                WHERE session_id = ?
            """,
                (session_id,),
            )
            row = cursor.fetchone()
            conn.close()

            if row and row[3]:  # total_cost is not None
                return {
                    "consultation_count": row[0] or 0,
                    "total_input_tokens": row[1] or 0,
                    "total_output_tokens": row[2] or 0,
                    "total_cost_usd": row[3] or 0.0,
                }
        return {
            "consultation_count": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
        }
