"""
Session Report Generation for Council AI.

Generates comprehensive session reports with insights and recommendations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from .history import ConsultationHistory

console = Console()


class SessionReport:
    """Generates session reports from consultation history."""

    def __init__(self, history: ConsultationHistory):
        """Initialize session report generator."""
        self.history = history

    def generate_session_report(
        self, session_id: str, output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive session report."""
        # Load session data (which includes consultations)
        session = self.history.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Get all consultations from the session object
        consultations = session.consultations

        if not consultations:
            raise ValueError(f"No consultations found for session {session_id}")

        # Calculate statistics
        total_consultations = len(consultations)
        if total_consultations == 0:
            raise ValueError(f"No consultations found for session {session_id}")

        start_time = min(c.timestamp for c in consultations)
        end_time = max(c.timestamp for c in consultations)
        duration = (end_time - start_time).total_seconds()
        duration_str = f"{int(duration // 60)}m {int(duration % 60)}s"

        # Get session name
        session_name = (
            session.council_name
            if hasattr(session, "council_name")
            else f"Session {session_id[:8]}"
        )

        # Extract insights
        key_insights: List[str] = []
        recommendations: List[str] = []
        common_themes: List[str] = []
        persona_usage: Dict[str, int] = {}

        for consultation in consultations:
            # Extract key findings from synthesis
            if consultation.synthesis:
                # Simple extraction - look for key phrases
                synthesis_lower = consultation.synthesis.lower()
                if "important" in synthesis_lower or "key" in synthesis_lower:
                    # Extract sentence containing key phrase
                    sentences = consultation.synthesis.split(".")
                    for sentence in sentences:
                        if "important" in sentence.lower() or "key" in sentence.lower():
                            key_insights.append(sentence.strip()[:200])  # Limit length
                            break

            # Extract recommendations
            if consultation.recommendations:
                for rec in consultation.recommendations:
                    if isinstance(rec, dict) and "text" in rec:
                        recommendations.append(rec["text"])
                    elif isinstance(rec, str):
                        recommendations.append(rec)

            # Track persona usage
            for response in consultation.responses:
                persona_id = response.persona.id
                persona_usage[persona_id] = persona_usage.get(persona_id, 0) + 1

            # Extract themes from queries
            query_words = consultation.query.lower().split()
            common_themes.extend([w for w in query_words if len(w) > 4][:3])

        # Deduplicate and limit
        key_insights = list(dict.fromkeys(key_insights))[:5]
        recommendations = list(dict.fromkeys(recommendations))[:5]
        common_themes = list(dict.fromkeys(common_themes))[:5]

        # Most consulted personas
        top_personas = sorted(persona_usage.items(), key=lambda x: x[1], reverse=True)[:5]

        report_data = {
            "session_id": session_id,
            "session_name": session_name,
            "date": start_time.strftime("%Y-%m-%d"),
            "duration": duration_str,
            "total_consultations": total_consultations,
            "key_insights": key_insights,
            "recommendations": recommendations,
            "common_themes": common_themes,
            "top_personas": [{"persona_id": pid, "count": count} for pid, count in top_personas],
            "consultations": [
                {
                    "id": c.id,
                    "query": c.query,
                    "timestamp": c.timestamp.isoformat(),
                    "mode": c.mode,
                    "persona_count": len(c.responses),
                }
                for c in consultations
            ],
        }

        # Save to file if requested
        if output_path:
            self._save_report(report_data, output_path)

        return report_data

    def _save_report(self, report_data: Dict[str, Any], output_path: Path) -> None:
        """Save report to file."""
        if output_path.suffix == ".json":
            with open(output_path, "w") as f:
                json.dump(report_data, f, indent=2, default=str)
        else:
            # Markdown format
            markdown = self._format_as_markdown(report_data)
            with open(output_path, "w") as f:
                f.write(markdown)

    def _format_as_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format report as Markdown."""
        lines = [
            f"# Session Report: {report_data['session_name']}",
            "",
            f"**Session ID:** {report_data['session_id']}",
            f"**Date:** {report_data['date']}",
            f"**Duration:** {report_data['duration']}",
            f"**Total Consultations:** {report_data['total_consultations']}",
            "",
            "## Key Insights",
            "",
        ]

        if report_data["key_insights"]:
            for insight in report_data["key_insights"]:
                lines.append(f"- {insight}")
        else:
            lines.append("*No insights available*")

        lines.extend(["", "## Recommendations", ""])

        if report_data["recommendations"]:
            for rec in report_data["recommendations"]:
                lines.append(f"- {rec}")
        else:
            lines.append("*No recommendations available*")

        lines.extend(["", "## Common Themes", ""])

        if report_data["common_themes"]:
            for theme in report_data["common_themes"]:
                lines.append(f"- {theme}")
        else:
            lines.append("*No themes identified*")

        lines.extend(["", "## Most Consulted Personas", ""])

        if report_data["top_personas"]:
            for persona in report_data["top_personas"]:
                lines.append(f"- {persona['persona_id']}: {persona['count']} consultations")
        else:
            lines.append("*No persona data available*")

        lines.extend(["", "## Consultation History", ""])

        for i, consultation in enumerate(report_data["consultations"], 1):
            lines.extend(
                [
                    f"### Consultation {i}",
                    "",
                    f"- **Query:** {consultation['query']}",
                    f"- **Mode:** {consultation['mode']}",
                    f"- **Personas:** {consultation['persona_count']}",
                    f"- **Time:** {consultation['timestamp'][:19]}",
                    "",
                ]
            )

        return "\n".join(lines)

    def display_report(self, report_data: Dict[str, Any]) -> None:
        """Display report in terminal."""
        console.print(f"\n[bold cyan]Session Report: {report_data['session_name']}[/bold cyan]")
        console.print(
            f"[dim]Date: {report_data['date']} | Duration: {report_data['duration']}[/dim]"
        )
        console.print(f"[dim]Total Consultations: {report_data['total_consultations']}[/dim]\n")

        if report_data["key_insights"]:
            console.print("[bold]Key Insights:[/bold]")
            for insight in report_data["key_insights"]:
                console.print(f"  • {insight}")
            console.print()

        if report_data["recommendations"]:
            console.print("[bold]Recommendations:[/bold]")
            for rec in report_data["recommendations"]:
                console.print(f"  • [yellow]{rec}[/yellow]")
            console.print()

        if report_data["top_personas"]:
            console.print("[bold]Most Consulted Personas:[/bold]")
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Persona", style="cyan")
            table.add_column("Consultations", justify="right")
            for persona in report_data["top_personas"]:
                table.add_row(persona["persona_id"], str(persona["count"]))
            console.print(table)
            console.print()
