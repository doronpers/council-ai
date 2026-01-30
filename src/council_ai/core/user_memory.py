"""User Memory and Personalization for Council AI.

Tracks user preferences, past interactions, and provides personalized experiences.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .session import ConsultationResult

logger = logging.getLogger(__name__)


class UserMemory:
    """Manages user memory and personalization across sessions."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize user memory storage."""
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Use same location as history
            from .config import ConfigManager

            config_manager = ConfigManager()
            # ConfigManager stores the full path to the config file in .path
            config_dir = config_manager.path.parent
            self.storage_path = config_dir / "user_memory"

        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.storage_path / "memory.json"
        self._memory: Dict[str, Any] = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load user memory from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load user memory: {e}")

        return {
            "user_id": str(uuid4()),
            "total_consultations": 0,
            "total_sessions": 0,
            "preferred_domains": [],
            "preferred_personas": [],
            "common_topics": [],
            "session_history": [],
            "last_session_date": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save_memory(self) -> None:
        """Save user memory to disk."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self._memory, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save user memory: {e}")

    def record_consultation(self, result: ConsultationResult) -> None:
        """Record a consultation in user memory."""
        self._memory["total_consultations"] = self._memory.get("total_consultations", 0) + 1

        # Track preferred personas
        persona_ids = [r.persona.id for r in result.responses]
        persona_counts = self._memory.get("persona_counts", {})
        for pid in persona_ids:
            persona_counts[pid] = persona_counts.get(pid, 0) + 1

        # Update preferred personas (top 5)
        self._memory["preferred_personas"] = sorted(
            persona_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        self._memory["persona_counts"] = persona_counts

        # Track topics (simple keyword extraction from query)
        query_lower = result.query.lower()
        words = [w for w in query_lower.split() if len(w) > 4]
        topic_counts = self._memory.get("topic_counts", {})
        for word in words[:5]:  # Limit to first 5 words
            topic_counts[word] = topic_counts.get(word, 0) + 1

        # Update common topics (top 10)
        self._memory["common_topics"] = sorted(
            topic_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        self._memory["topic_counts"] = topic_counts

        self._save_memory()

    def record_session(self, session_id: str, domain: Optional[str] = None) -> None:
        """Record a session in user memory."""
        self._memory["total_sessions"] = self._memory.get("total_sessions", 0) + 1
        self._memory["last_session_date"] = datetime.now(timezone.utc).isoformat()

        # Track preferred domains
        if domain:
            domain_counts = self._memory.get("domain_counts", {})
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            self._memory["preferred_domains"] = sorted(
                domain_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            self._memory["domain_counts"] = domain_counts

        # Add to session history (keep last 20)
        session_entry = {
            "session_id": session_id,
            "domain": domain,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        session_history = self._memory.get("session_history", [])
        session_history.append(session_entry)
        self._memory["session_history"] = session_history[-20:]  # Keep last 20

        self._save_memory()

    def get_personalized_greeting(self) -> str:
        """Get personalized greeting based on user history."""
        total = self._memory.get("total_consultations", 0)
        last_date = self._memory.get("last_session_date")

        if total == 0:
            return "Welcome to Council AI! Ready for your first consultation?"
        elif total == 1:
            return "Welcome back! You've completed 1 consultation. Ready for another?"
        else:
            if last_date:
                return f"Welcome back! You've completed {total} consultations. Last session: {last_date[:10]}"
            return f"Welcome back! You've completed {total} consultations."

    def get_personalized_insights(self) -> List[str]:
        """Get personalized insights based on user history."""
        insights = []

        preferred_personas = self._memory.get("preferred_personas", [])
        if preferred_personas:
            top_persona = preferred_personas[0][0]
            insights.append(f"You frequently consult with: {top_persona}")

        preferred_domains = self._memory.get("preferred_domains", [])
        if preferred_domains:
            top_domain = preferred_domains[0][0]
            insights.append(f"Your preferred domain: {top_domain}")

        common_topics = self._memory.get("common_topics", [])
        if common_topics:
            top_topic = common_topics[0][0]
            insights.append(f"Recent focus: {top_topic}")

        return insights

    def get_personalized_recommendations(self) -> List[str]:
        """Get personalized recommendations based on user history."""
        recommendations = []

        total = self._memory.get("total_consultations", 0)

        if total == 0:
            recommendations.append("Try different consultation modes to see which works best")
            recommendations.append("Explore different domains to get diverse perspectives")
        elif total < 3:
            recommendations.append(
                "Continue building your consultation history for better insights"
            )
        else:
            preferred_personas = self._memory.get("preferred_personas", [])
            if len(preferred_personas) < 3:
                recommendations.append(
                    "Try consulting with different personas for diverse perspectives"
                )

            preferred_domains = self._memory.get("preferred_domains", [])
            if len(preferred_domains) < 2:
                recommendations.append("Explore different domains to broaden your insights")

        return recommendations

    def get_user_profile(self) -> Dict[str, Any]:
        """Get complete user profile."""
        return {
            "user_id": self._memory.get("user_id"),
            "total_consultations": self._memory.get("total_consultations", 0),
            "total_sessions": self._memory.get("total_sessions", 0),
            "preferred_domains": [d[0] for d in self._memory.get("preferred_domains", [])],
            "preferred_personas": [p[0] for p in self._memory.get("preferred_personas", [])],
            "common_topics": [t[0] for t in self._memory.get("common_topics", [])],
            "last_session_date": self._memory.get("last_session_date"),
        }


# Global user memory instance
_global_user_memory: Optional[UserMemory] = None


def get_user_memory() -> UserMemory:
    """Get the global user memory instance."""
    global _global_user_memory
    if _global_user_memory is None:
        _global_user_memory = UserMemory()
    return _global_user_memory
