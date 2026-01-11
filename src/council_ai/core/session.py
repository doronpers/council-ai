"""
Session Management - Tracks consultation history and results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .persona import Persona


@dataclass
class MemberResponse:
    """Response from a single council member."""
    persona: Persona
    content: str
    timestamp: datetime
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "persona_id": self.persona.id,
            "persona_name": self.persona.name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
        }


@dataclass
class ConsultationResult:
    """Result of a council consultation."""
    query: str
    responses: List[MemberResponse]
    synthesis: Optional[str] = None
    context: Optional[str] = None
    mode: str = "synthesis"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "query": self.query,
            "context": self.context,
            "mode": self.mode,
            "timestamp": self.timestamp.isoformat(),
            "responses": [r.to_dict() for r in self.responses],
            "synthesis": self.synthesis,
        }
    
    def to_markdown(self) -> str:
        """Export to markdown format."""
        lines = [
            f"# Council Consultation",
            f"",
            f"**Query:** {self.query}",
            f"",
        ]
        
        if self.context:
            lines.extend([
                f"**Context:** {self.context}",
                f"",
            ])
        
        lines.extend([
            f"**Mode:** {self.mode}",
            f"**Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
        ])
        
        if self.synthesis:
            lines.extend([
                f"## Synthesis",
                f"",
                self.synthesis,
                f"",
            ])
        
        lines.extend([
            f"## Individual Responses",
            f"",
        ])
        
        for response in self.responses:
            lines.extend([
                f"### {response.persona.emoji} {response.persona.name}",
                f"*{response.persona.title}*",
                f"",
                response.content if not response.error else f"*Error: {response.error}*",
                f"",
            ])
        
        return "\n".join(lines)


@dataclass
class Session:
    """A consultation session with history."""
    council_name: str
    members: List[str]
    started_at: datetime = field(default_factory=datetime.now)
    consultations: List[ConsultationResult] = field(default_factory=list)
    
    def add_consultation(self, result: ConsultationResult) -> None:
        """Add a consultation result to the session."""
        self.consultations.append(result)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "council_name": self.council_name,
            "members": self.members,
            "started_at": self.started_at.isoformat(),
            "consultations": [c.to_dict() for c in self.consultations],
        }
