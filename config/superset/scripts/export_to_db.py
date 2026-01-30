#!/usr/bin/env python3
"""
Export council-ai consultation data to a database for Superset visualization.

This script reads consultation data from ConsultationHistory (SQLite or JSON files)
and exports them to a SQL database (SQLite or PostgreSQL) where they can be
queried by Apache Superset.

Usage:
    # Export to SQLite (default)
    python export_to_db.py --format sqlite

    # Export to PostgreSQL
    python export_to_db.py --format postgresql --db-uri "postgresql://user:pass@localhost/db"

    # Export from specific storage path
    python export_to_db.py --storage-path ~/.config/council-ai/history --format sqlite
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from council_ai.core.history import ConsultationHistory  # noqa: E402

# Add database directory to path for imports
database_dir = Path(__file__).parent.parent / "database"
sys.path.insert(0, str(database_dir))

from models import Consultation  # noqa: E402
from models import MemberResponse as DBMemberResponse  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ConsultationExporter:
    """Export consultation data to SQL database."""

    def __init__(self, db_uri: str):
        """Initialize exporter with database URI.

        Args:
            db_uri: SQLAlchemy database URI
        """
        self.db_uri = db_uri
        self.engine = create_engine(db_uri, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables if they don't exist."""
        logger.info("Creating database tables...")
        from models import Base

        Base.metadata.create_all(self.engine)
        logger.info("✓ Tables created successfully")

    def load_consultations_from_history(
        self, storage_path: Optional[Path] = None, use_sqlite: bool = True
    ) -> List[Dict[str, Any]]:
        """Load consultations from ConsultationHistory.

        Args:
            storage_path: Optional path to history storage directory
            use_sqlite: Whether history uses SQLite (True) or JSON (False)

        Returns:
            List of consultation data dictionaries
        """
        logger.info("Loading consultations from history...")
        consultations = []

        # Initialize history
        if storage_path:
            history = ConsultationHistory(storage_path=str(storage_path), use_sqlite=use_sqlite)
        else:
            history = ConsultationHistory(use_sqlite=use_sqlite)

        # List all consultations
        try:
            consultation_list = history.list(limit=None)
            for consultation_summary in consultation_list:
                consultation_id = consultation_summary.get("id")
                if consultation_id:
                    full_consultation = history.load(consultation_id)
                    if full_consultation:
                        consultations.append(full_consultation)
        except Exception as e:
            logger.warning(f"Error loading consultations: {e}")

        logger.info(f"Loaded {len(consultations)} consultations from history")
        return consultations

    def export_consultation(self, consultation_data: Dict[str, Any], session) -> bool:
        """Export a single consultation to database.

        Args:
            consultation_data: Consultation data dictionary
            session: SQLAlchemy session

        Returns:
            True if successful
        """
        try:
            consultation_id = consultation_data.get("id")
            if not consultation_id:
                logger.warning("Consultation missing ID, skipping")
                return False

            # Parse timestamp
            timestamp_str = consultation_data.get("timestamp")
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                timestamp = datetime.utcnow()

            # Get responses
            responses_data = consultation_data.get("responses", [])
            if isinstance(responses_data, str):
                responses_data = json.loads(responses_data)

            # Create consultation record
            consultation = Consultation(
                consultation_id=consultation_id,
                query=consultation_data.get("query", ""),
                context=consultation_data.get("context"),
                mode=consultation_data.get("mode", "synthesis"),
                timestamp=timestamp,
                synthesis=consultation_data.get("synthesis"),
                synthesis_length=len(consultation_data.get("synthesis", ""))
                if consultation_data.get("synthesis")
                else 0,
                tags=consultation_data.get("tags", []),
                notes=consultation_data.get("notes"),
                metadata=consultation_data.get("metadata", {}),
                response_count=len(responses_data),
            )
            session.add(consultation)

            # Export member responses
            for response_data in responses_data:
                if isinstance(response_data, dict):
                    member_name = response_data.get("member_name") or response_data.get(
                        "member", "unknown"
                    )
                    persona_name = response_data.get("persona_name") or response_data.get(
                        "persona", ""
                    )
                    response_text = response_data.get("response") or response_data.get("text", "")
                else:
                    # Handle MemberResponse object if serialized differently
                    member_name = getattr(response_data, "member_name", "unknown")
                    persona_name = getattr(response_data, "persona_name", "")
                    response_text = getattr(response_data, "response", "")

                db_response = DBMemberResponse(
                    consultation_id=consultation_id,
                    member_name=member_name,
                    persona_name=persona_name,
                    response_text=response_text,
                    response_length=len(response_text),
                    timestamp=timestamp,
                    metadata=response_data if isinstance(response_data, dict) else {},
                )
                session.add(db_response)

            return True

        except Exception as e:
            logger.error(
                f"Error exporting consultation {consultation_data.get('id', 'unknown')}: {e}"
            )
            return False

    def export_all(self, storage_path: Optional[Path] = None, use_sqlite: bool = True) -> int:
        """Export all consultations to database.

        Args:
            storage_path: Optional path to history storage directory
            use_sqlite: Whether history uses SQLite (True) or JSON (False)

        Returns:
            Number of consultations exported
        """
        consultations = self.load_consultations_from_history(storage_path, use_sqlite)
        if not consultations:
            logger.warning("No consultations found to export")
            return 0

        session = self.Session()
        exported = 0

        try:
            for consultation_data in consultations:
                if self.export_consultation(consultation_data, session):
                    exported += 1

            session.commit()
            logger.info(f"✓ Exported {exported}/{len(consultations)} consultations successfully")

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

        return exported


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Export council-ai consultations to database")
    parser.add_argument(
        "--format",
        choices=["sqlite", "postgresql"],
        default="sqlite",
        help="Database format (default: sqlite)",
    )
    parser.add_argument(
        "--db-uri",
        help="Database URI (e.g., postgresql://user:pass@localhost/db)",
    )
    parser.add_argument(
        "--storage-path",
        type=Path,
        help="Path to consultation history storage directory",
    )
    parser.add_argument(
        "--use-sqlite-history",
        action="store_true",
        help="Use SQLite for reading history (default: JSON files)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./council_ai_consultations.db"),
        help="Output SQLite database path (default: ./council_ai_consultations.db)",
    )

    args = parser.parse_args()

    # Determine database URI
    if args.db_uri:
        db_uri = args.db_uri
    elif args.format == "sqlite":
        db_uri = f"sqlite:///{args.output.absolute()}"
    else:
        logger.error("--db-uri required for PostgreSQL")
        return 1

    # Create exporter
    exporter = ConsultationExporter(db_uri)
    exporter.create_tables()

    # Export consultations
    exported = exporter.export_all(args.storage_path, args.use_sqlite_history)

    if exported > 0:
        logger.info(f"✓ Successfully exported {exported} consultations to {db_uri}")
        logger.info("You can now connect Superset to this database")
    else:
        logger.warning("No consultations were exported")

    return 0


if __name__ == "__main__":
    sys.exit(main())
