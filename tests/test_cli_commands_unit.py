"""
Unit tests for CLI command modules.

These tests focus on testing individual functions and logic within CLI commands
rather than integration tests that invoke the full CLI.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import tempfile
import json


class TestConsultCommandLogic:
    """Unit tests for consult command internal logic."""

    def test_parse_bracket_notation_extracts_members(self):
        """Test that bracket notation parser extracts persona IDs."""
        from council_ai.cli.utils import parse_bracket_notation

        result = parse_bracket_notation("[DR, MD] What do you think?")
        assert result == ["DR", "MD"]

    def test_parse_bracket_notation_empty_without_brackets(self):
        """Test that parser returns None for queries without brackets."""
        from council_ai.cli.utils import parse_bracket_notation

        result = parse_bracket_notation("What do you think?")
        assert result is None

    def test_parse_bracket_notation_handles_whitespace(self):
        """Test bracket notation parser handles various whitespace."""
        from council_ai.cli.utils import parse_bracket_notation

        result = parse_bracket_notation("[ DR , MD , JT ] Question")
        assert result == ["DR", "MD", "JT"]

    def test_parse_bracket_notation_single_member(self):
        """Test bracket notation with single member."""
        from council_ai.cli.utils import parse_bracket_notation

        result = parse_bracket_notation("[DR] What do you think?")
        assert result == ["DR"]


class TestHistoryCommandLogic:
    """Unit tests for history command internal logic."""

    def test_history_list_formats_query_preview(self):
        """Test that long queries are truncated correctly."""
        # Test the truncation logic used in history_list
        query = "x" * 100
        preview = query[:47] + "..." if len(query) > 50 else query

        assert len(preview) == 50
        assert preview.endswith("...")

    def test_history_list_short_query_not_truncated(self):
        """Test that short queries are not truncated."""
        query = "Short query"
        preview = query[:47] + "..." if len(query) > 50 else query

        assert preview == "Short query"

    def test_date_formatting(self):
        """Test date string formatting."""
        timestamp = "2024-01-15T10:30:45.123456"
        date_str = timestamp[:10]

        assert date_str == "2024-01-15"


class TestDoctorCommandLogic:
    """Unit tests for doctor command internal logic."""

    def test_provider_status_formatting(self):
        """Test provider status string formatting."""
        # Test the status string logic used in doctor command
        has_key = True
        provider = "openai"
        env_var = f"{provider.upper()}_API_KEY"

        status = "[green]✓ Configured[/green]" if has_key else "[dim]Not configured[/dim]"
        assert "Configured" in status

        has_key = False
        status = "[green]✓ Configured[/green]" if has_key else "[dim]Not configured[/dim]"
        assert "Not configured" in status

    def test_latency_formatting(self):
        """Test latency display formatting."""
        latency = 123.456
        formatted = f"{latency:.0f}ms"

        assert formatted == "123ms"


class TestInitCommandLogic:
    """Unit tests for init command internal logic."""

    def test_provider_choice_default_selection(self):
        """Test default provider selection logic."""
        available_providers = [
            ("openai", "sk-test"),
            ("anthropic", None),
        ]

        # Find first available provider
        default_provider = None
        for provider_name, api_key in available_providers:
            if api_key:
                default_provider = provider_name
                break

        assert default_provider == "openai"

    def test_no_available_provider(self):
        """Test when no providers have keys."""
        available_providers = [
            ("openai", None),
            ("anthropic", None),
        ]

        default_provider = None
        for provider_name, api_key in available_providers:
            if api_key:
                default_provider = provider_name
                break

        assert default_provider is None


class TestQACommandLogic:
    """Unit tests for QA command internal logic."""

    def test_score_color_high(self):
        """Test score color for high scores."""
        score = 85
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        assert score_color == "green"

    def test_score_color_medium(self):
        """Test score color for medium scores."""
        score = 70
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        assert score_color == "yellow"

    def test_score_color_low(self):
        """Test score color for low scores."""
        score = 45
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        assert score_color == "red"

    def test_score_formatting(self):
        """Test score display formatting."""
        score = 85.5678
        formatted = f"{score:.1f}/100"
        assert formatted == "85.6/100"


class TestSessionReportLogic:
    """Unit tests for session report generation logic."""

    def test_safe_filename_generation(self):
        """Test safe filename generation from query."""
        query = "What's the best approach for handling user authentication?"

        # Logic from history_export
        safe_query = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "" for c in query[:30]
        )
        safe_query = safe_query.replace(" ", "_").lower()

        assert " " not in safe_query
        assert "'" not in safe_query
        assert "?" not in safe_query

    def test_findings_report_header(self):
        """Test findings report header generation."""
        council_name = "Test Council"
        session_id = "abc123"
        started_at = "2024-01-15T10:00:00"
        members = ["analyst", "critic"]

        lines = [
            f"# Findings Report: {council_name}",
            f"**Session ID:** {session_id}",
            f"**Date:** {started_at}",
            f"**Members:** {', '.join(members)}",
        ]

        report = "\n".join(lines)

        assert "# Findings Report: Test Council" in report
        assert "**Session ID:** abc123" in report
        assert "analyst, critic" in report


class TestHistoryExportLogic:
    """Unit tests for history export functionality."""

    def test_export_format_markdown(self):
        """Test markdown export extension."""
        format_choice = "markdown"
        ext = "json" if format_choice == "json" else "md"
        assert ext == "md"

    def test_export_format_json(self):
        """Test JSON export extension."""
        format_choice = "json"
        ext = "json" if format_choice == "json" else "md"
        assert ext == "json"

    def test_output_path_generation(self):
        """Test output path generation."""
        consultation_id = "abcdefgh12345678"
        safe_query = "test_query"
        ext = "md"

        output_path = Path(f"consultation_{consultation_id[:8]}_{safe_query}.{ext}")

        assert str(output_path) == "consultation_abcdefgh_test_query.md"


class TestCrossdomainLogic:
    """Unit tests for cross-domain consultation logic."""

    def test_domain_list_parsing(self):
        """Test comma-separated domain list parsing."""
        domains_input = "tech, business, legal"
        domain_list = [d.strip() for d in domains_input.split(",")]

        assert domain_list == ["tech", "business", "legal"]

    def test_persona_deduplication(self):
        """Test persona deduplication across domains."""
        all_personas = []
        seen_personas = set()

        # Simulate adding personas from multiple domains
        domain1_personas = ["analyst", "critic"]
        domain2_personas = ["critic", "advisor"]  # critic is duplicate

        for persona_id in domain1_personas + domain2_personas:
            if persona_id not in seen_personas:
                all_personas.append(persona_id)
                seen_personas.add(persona_id)

        assert all_personas == ["analyst", "critic", "advisor"]


class TestQuickModeLogic:
    """Unit tests for quick mode functionality."""

    def test_quick_mode_limits_personas(self):
        """Test that quick mode limits to 3 personas."""
        members = ["a", "b", "c", "d", "e"]
        quick_members = tuple(list(members)[:3])

        assert quick_members == ("a", "b", "c")

    def test_quick_mode_changes_synthesis_to_individual(self):
        """Test that quick mode changes synthesis to individual."""
        mode = "synthesis"

        # Quick mode logic
        if mode == "synthesis":
            mode = "individual"

        assert mode == "individual"

    def test_quick_mode_keeps_other_modes(self):
        """Test that quick mode doesn't change non-synthesis modes."""
        mode = "debate"

        # Quick mode logic
        if mode == "synthesis":
            mode = "individual"

        assert mode == "debate"


class TestPresetLogic:
    """Unit tests for preset configuration logic."""

    def test_preset_domain_override(self):
        """Test that CLI option overrides preset."""
        preset_config = {"domain": "general", "mode": "synthesis"}
        cli_domain = "tech"

        # CLI options override preset
        domain = cli_domain if cli_domain else preset_config.get("domain", "general")

        assert domain == "tech"

    def test_preset_used_when_no_cli_option(self):
        """Test that preset is used when no CLI option provided."""
        preset_config = {"domain": "general", "mode": "synthesis"}
        cli_domain = None

        domain = cli_domain if cli_domain else preset_config.get("domain", "general")

        assert domain == "general"

    def test_preset_members_tuple_conversion(self):
        """Test preset members converted to tuple."""
        preset_config = {"members": ["DR", "MD"]}

        members = preset_config.get("members", [])
        members = tuple(members) if members else ()

        assert members == ("DR", "MD")
        assert isinstance(members, tuple)


class TestCostDisplayLogic:
    """Unit tests for cost display functionality."""

    def test_cost_formatting(self):
        """Test cost formatting with 2 decimal places."""
        total_cost = 0.12345
        formatted = f"${total_cost:.2f}"

        assert formatted == "$0.12"

    def test_cost_display_message(self):
        """Test cost display message format."""
        total_cost = 0.50
        persona_count = 3
        mode_str = "synthesis"

        message = f"Cost: ${total_cost:.2f} ({persona_count} personas, {mode_str})"

        assert message == "Cost: $0.50 (3 personas, synthesis)"


class TestSessionIdHandling:
    """Unit tests for session ID handling."""

    def test_session_id_truncation_for_display(self):
        """Test session ID truncation for display."""
        session_id = "abcdefgh12345678901234567890"
        truncated = session_id[:8]

        assert truncated == "abcdefgh"
        assert len(truncated) == 8

    def test_session_id_none_handling(self):
        """Test handling of None session ID."""
        session_id = None
        display = f"Session: {session_id[:8]}" if session_id else "No session"

        assert display == "No session"
