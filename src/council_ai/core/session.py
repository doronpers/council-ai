"""
Session Management - Tracks consultation history and results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .persona import Persona


@dataclass
class MemberResponse:
    """Response from a single council member."""

    persona: Persona
    content: str
    timestamp: datetime
    error: Optional[str] = None
    audio_url: Optional[str] = None  # URL to audio file if TTS is enabled

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "persona_id": self.persona.id,
            "persona_name": self.persona.name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "audio_url": self.audio_url,
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
    id: Optional[str] = field(default_factory=lambda: str(uuid4()))
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    structured_synthesis: Optional[Any] = None  # SynthesisSchema
    action_items: List[Any] = field(default_factory=list)  # List[ActionItem]
    recommendations: List[Any] = field(default_factory=list)  # List[Recommendation]
    pros_cons: Optional[Any] = None  # ProsCons
    synthesis_audio_url: Optional[str] = None  # URL to synthesis audio if TTS is enabled

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "id": self.id,
            "query": self.query,
            "context": self.context,
            "mode": self.mode,
            "timestamp": self.timestamp.isoformat(),
            "responses": [r.to_dict() for r in self.responses],
            "synthesis": self.synthesis,
            "synthesis_audio_url": self.synthesis_audio_url,
            "tags": self.tags,
            "notes": self.notes,
            "structured_synthesis": (
                self.structured_synthesis.model_dump()
                if self.structured_synthesis and hasattr(self.structured_synthesis, "model_dump")
                else (self.structured_synthesis if self.structured_synthesis else None)
            ),
            "action_items": [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in self.action_items
            ],
            "recommendations": [
                rec.model_dump() if hasattr(rec, "model_dump") else rec
                for rec in self.recommendations
            ],
            "pros_cons": (
                self.pros_cons.model_dump()
                if self.pros_cons and hasattr(self.pros_cons, "model_dump")
                else (self.pros_cons if self.pros_cons else None)
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsultationResult":
        """Create ConsultationResult from dictionary."""
        from datetime import datetime

        # Reconstruct MemberResponse objects
        responses = []
        for r_data in data.get("responses", []):
            from .persona import get_persona

            persona = get_persona(r_data.get("persona_id", ""))
            if persona:
                from .session import MemberResponse

                responses.append(
                    MemberResponse(
                        persona=persona,
                        content=r_data.get("content", ""),
                        timestamp=datetime.fromisoformat(
                            r_data.get("timestamp", datetime.now().isoformat())
                        ),
                        error=r_data.get("error"),
                        audio_url=r_data.get("audio_url"),
                    )
                )

        return cls(
            id=data.get("id"),
            query=data["query"],
            context=data.get("context"),
            mode=data.get("mode", "synthesis"),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            responses=responses,
            synthesis=data.get("synthesis"),
            synthesis_audio_url=data.get("synthesis_audio_url"),
            tags=data.get("tags", []),
            notes=data.get("notes"),
        )

    def to_markdown(self) -> str:
        """Export to markdown format."""
        lines = [
            "# Council Consultation",
            "",
            f"**Query:** {self.query}",
            "",
        ]

        if self.context:
            lines.extend(
                [
                    f"**Context:** {self.context}",
                    "",
                ]
            )

        lines.extend(
            [
                f"**Mode:** {self.mode}",
                f"**Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
            ]
        )

        # Use structured synthesis if available, otherwise use free-form
        if self.structured_synthesis:
            from .schemas import SynthesisSchema

            if isinstance(self.structured_synthesis, SynthesisSchema):
                # Format structured synthesis nicely
                if self.structured_synthesis.key_points_of_agreement:
                    lines.append("## Key Points of Agreement")
                    lines.append("")
                    for point in self.structured_synthesis.key_points_of_agreement:
                        lines.append(f"- {point}")
                    lines.append("")

                if self.structured_synthesis.key_points_of_tension:
                    lines.append("## Key Points of Tension")
                    lines.append("")
                    for point in self.structured_synthesis.key_points_of_tension:
                        lines.append(f"- {point}")
                    lines.append("")

                if self.structured_synthesis.synthesized_recommendation:
                    lines.append("## Synthesized Recommendation")
                    lines.append("")
                    lines.append(self.structured_synthesis.synthesized_recommendation)
                    lines.append("")

                if self.structured_synthesis.action_items:
                    lines.append("## Action Items")
                    lines.append("")
                    for item in self.structured_synthesis.action_items:
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            item.priority.lower(), "•"
                        )
                        owner_text = f" ({item.owner})" if item.owner else ""
                        due_text = f" - Due: {item.due_date}" if item.due_date else ""
                        lines.append(f"{priority_emoji} {item.description}{owner_text}{due_text}")
                    lines.append("")

                if self.structured_synthesis.recommendations:
                    lines.append("## Recommendations")
                    lines.append("")
                    for rec in self.structured_synthesis.recommendations:
                        conf_emoji = {"high": "✓", "medium": "~", "low": "?"}.get(
                            rec.confidence.lower(), "•"
                        )
                        lines.append(f"### {conf_emoji} {rec.title}")
                        lines.append(f"*Confidence: {rec.confidence}*")
                        lines.append("")
                        lines.append(rec.description)
                        if rec.rationale:
                            lines.append(f"*Rationale: {rec.rationale}*")
                        lines.append("")

                if self.structured_synthesis.pros_cons:
                    lines.append("## Pros and Cons")
                    lines.append("")
                    if self.structured_synthesis.pros_cons.pros:
                        lines.append("### Pros")
                        for pro in self.structured_synthesis.pros_cons.pros:
                            lines.append(f"- {pro}")
                        lines.append("")
                    if self.structured_synthesis.pros_cons.cons:
                        lines.append("### Cons")
                        for con in self.structured_synthesis.pros_cons.cons:
                            lines.append(f"- {con}")
                        lines.append("")
                    if self.structured_synthesis.pros_cons.net_assessment:
                        lines.append(
                            f"**Net Assessment:** {self.structured_synthesis.pros_cons.net_assessment}"
                        )
                        lines.append("")
        elif self.synthesis:
            lines.extend(
                [
                    "## Synthesis",
                    "",
                    self.synthesis,
                    "",
                ]
            )

        lines.extend(
            [
                "## Individual Responses",
                "",
            ]
        )

        for response in self.responses:
            lines.extend(
                [
                    f"### {response.persona.emoji} {response.persona.name}",
                    f"*{response.persona.title}*",
                    "",
                    response.content if not response.error else f"*Error: {response.error}*",
                    "",
                ]
            )

        return "\n".join(lines)


@dataclass
class Session:
    """A consultation session with history."""

    council_name: str
    members: List[str]
    session_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=datetime.now)
    consultations: List[ConsultationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_consultation(self, result: ConsultationResult) -> None:
        """Add a consultation result to the session."""
        self.consultations.append(result)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "session_id": self.session_id,
            "council_name": self.council_name,
            "members": self.members,
            "started_at": self.started_at.isoformat(),
            "consultations": [c.to_dict() for c in self.consultations],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session from dictionary."""
        consultations = [ConsultationResult.from_dict(c) for c in data.get("consultations", [])]
        return cls(
            session_id=data.get("session_id", str(uuid4())),
            council_name=data.get("council_name", "Unknown"),
            members=data.get("members", []),
            started_at=datetime.fromisoformat(
                data.get("started_at", datetime.now().isoformat())
            ),
            consultations=consultations,
            metadata=data.get("metadata", {}),
        )
