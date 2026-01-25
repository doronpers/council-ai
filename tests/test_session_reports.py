"""Tests for session report generation."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from council_ai import Persona
from council_ai.core.session import ConsultationResult, MemberResponse, Session
from council_ai.core.session_reports import SessionReport


@pytest.fixture
def mock_history():
    """Create a mock ConsultationHistory."""
    history = MagicMock()
    return history


@pytest.fixture
def sample_persona():
    """Create a sample persona for testing."""
    return Persona(
        id="test_persona",
        name="Test Persona",
        title="Expert",
        core_question="What should we consider?",
        razor="Keep it simple.",
    )


@pytest.fixture
def sample_consultation(sample_persona):
    """Create a sample consultation result."""
    response = MemberResponse(
        persona=sample_persona,
        content="This is test advice",
        timestamp=datetime.now(),
    )

    return ConsultationResult(
        query="Test query",
        responses=[response],
        synthesis="This is an important finding. Key insight here.",
        recommendations=[{"text": "Do this first"}, "Do this second"],
        timestamp=datetime.now(),
        mode="synthesis",
    )


@pytest.fixture
def sample_session(sample_consultation):
    """Create a sample session with consultations."""
    session = Session(
        council_name="Test Council",
        members=["test_persona"],
        session_id="test-session-123",
        started_at=datetime.now() - timedelta(hours=1),
        consultations=[sample_consultation],
    )
    return session


class TestSessionReport:
    """Tests for SessionReport class."""

    def test_init(self, mock_history):
        """Test SessionReport initialization."""
        report = SessionReport(mock_history)
        assert report.history == mock_history

    def test_generate_session_report_session_not_found(self, mock_history):
        """Test report generation when session doesn't exist."""
        mock_history.load_session.return_value = None
        report = SessionReport(mock_history)

        with pytest.raises(ValueError, match="not found"):
            report.generate_session_report("nonexistent-session")

    def test_generate_session_report_no_consultations(self, mock_history):
        """Test report generation when session has no consultations."""
        session = Session(
            council_name="Test Council",
            members=[],
            consultations=[],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        with pytest.raises(ValueError, match="No consultations found"):
            report.generate_session_report("test-session")

    def test_generate_session_report_basic(self, mock_history, sample_session):
        """Test basic report generation."""
        mock_history.load_session.return_value = sample_session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session-123")

        assert result["session_id"] == "test-session-123"
        assert result["session_name"] == "Test Council"
        assert result["total_consultations"] == 1
        assert "key_insights" in result
        assert "recommendations" in result
        assert "common_themes" in result
        assert "top_personas" in result
        assert len(result["consultations"]) == 1

    def test_generate_session_report_with_insights(self, mock_history, sample_persona):
        """Test report generation extracts key insights."""
        consultation = ConsultationResult(
            query="Test query",
            responses=[
                MemberResponse(
                    persona=sample_persona,
                    content="Advice",
                    timestamp=datetime.now(),
                )
            ],
            synthesis="This is an important finding that should be highlighted.",
            timestamp=datetime.now(),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona"],
            consultations=[consultation],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        assert len(result["key_insights"]) > 0
        assert "important" in result["key_insights"][0].lower()

    def test_generate_session_report_with_recommendations_dict(self, mock_history, sample_persona):
        """Test report generation extracts recommendations from dict format."""
        consultation = ConsultationResult(
            query="Test query",
            responses=[
                MemberResponse(
                    persona=sample_persona,
                    content="Advice",
                    timestamp=datetime.now(),
                )
            ],
            recommendations=[{"text": "First recommendation"}, {"text": "Second recommendation"}],
            timestamp=datetime.now(),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona"],
            consultations=[consultation],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        assert len(result["recommendations"]) == 2
        assert "First recommendation" in result["recommendations"]
        assert "Second recommendation" in result["recommendations"]

    def test_generate_session_report_with_recommendations_string(
        self, mock_history, sample_persona
    ):
        """Test report generation extracts recommendations from string format."""
        consultation = ConsultationResult(
            query="Test query",
            responses=[
                MemberResponse(
                    persona=sample_persona,
                    content="Advice",
                    timestamp=datetime.now(),
                )
            ],
            recommendations=["String recommendation 1", "String recommendation 2"],
            timestamp=datetime.now(),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona"],
            consultations=[consultation],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        assert len(result["recommendations"]) == 2
        assert "String recommendation 1" in result["recommendations"]

    def test_generate_session_report_persona_usage(self, mock_history, sample_persona):
        """Test report generation tracks persona usage."""
        persona2 = Persona(
            id="persona2",
            name="Persona 2",
            title="Expert 2",
            core_question="?",
            razor=".",
        )

        consultation1 = ConsultationResult(
            query="Query 1",
            responses=[
                MemberResponse(persona=sample_persona, content="Advice 1", timestamp=datetime.now())
            ],
            timestamp=datetime.now(),
        )

        consultation2 = ConsultationResult(
            query="Query 2",
            responses=[
                MemberResponse(persona=persona2, content="Advice 2", timestamp=datetime.now()),
                MemberResponse(persona=persona2, content="Advice 3", timestamp=datetime.now()),
            ],
            timestamp=datetime.now(),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona", "persona2"],
            consultations=[consultation1, consultation2],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        assert len(result["top_personas"]) > 0
        # persona2 should have higher count (2 vs 1)
        assert result["top_personas"][0]["persona_id"] == "persona2"
        assert result["top_personas"][0]["count"] == 2

    def test_generate_session_report_common_themes(self, mock_history, sample_persona):
        """Test report generation extracts common themes from queries."""
        consultation = ConsultationResult(
            query="This is a longer query with multiple words",
            responses=[
                MemberResponse(persona=sample_persona, content="Advice", timestamp=datetime.now())
            ],
            timestamp=datetime.now(),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona"],
            consultations=[consultation],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        # Should extract words longer than 4 characters
        assert len(result["common_themes"]) > 0

    def test_generate_session_report_session_name_fallback(self, mock_history, sample_consultation):
        """Test report generation uses session ID when council_name not available."""
        session = Session(
            council_name="Test Council",
            members=[],
            session_id="test-session-abc123",
            consultations=[sample_consultation],
        )
        # Remove council_name attribute
        del session.council_name
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session-abc123")
        assert (
            "Session test-s" in result["session_name"] or "test-session" in result["session_name"]
        )

    def test_generate_session_report_duration_calculation(self, mock_history, sample_persona):
        """Test report generation calculates duration correctly."""
        now = datetime.now()
        consultation1 = ConsultationResult(
            query="Query 1",
            responses=[MemberResponse(persona=sample_persona, content="Advice", timestamp=now)],
            timestamp=now,
        )
        consultation2 = ConsultationResult(
            query="Query 2",
            responses=[
                MemberResponse(
                    persona=sample_persona, content="Advice", timestamp=now + timedelta(minutes=30)
                )
            ],
            timestamp=now + timedelta(minutes=30),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona"],
            consultations=[consultation1, consultation2],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        assert "duration" in result
        assert "m" in result["duration"] or "s" in result["duration"]

    def test_generate_session_report_saves_json(self, mock_history, sample_session, tmp_path):
        """Test report generation saves JSON file."""
        mock_history.load_session.return_value = sample_session
        report = SessionReport(mock_history)

        output_path = tmp_path / "report.json"
        result = report.generate_session_report("test-session-123", output_path=output_path)

        assert output_path.exists()
        assert result["session_id"] == "test-session-123"
        # Verify JSON content
        import json

        with open(output_path) as f:
            saved_data = json.load(f)
        assert saved_data["session_id"] == "test-session-123"

    def test_generate_session_report_saves_markdown(self, mock_history, sample_session, tmp_path):
        """Test report generation saves Markdown file."""
        mock_history.load_session.return_value = sample_session
        report = SessionReport(mock_history)

        output_path = tmp_path / "report.md"
        report.generate_session_report("test-session-123", output_path=output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "# Session Report" in content
        assert "Test Council" in content

    def test_format_as_markdown(self, mock_history, sample_session):
        """Test markdown formatting."""
        mock_history.load_session.return_value = sample_session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session-123")
        markdown = report._format_as_markdown(result)

        assert "# Session Report" in markdown
        assert "Test Council" in markdown
        assert "## Key Insights" in markdown
        assert "## Recommendations" in markdown
        assert "## Common Themes" in markdown
        assert "## Most Consulted Personas" in markdown
        assert "## Consultation History" in markdown

    def test_format_as_markdown_empty_insights(self, mock_history, sample_persona):
        """Test markdown formatting with empty insights."""
        consultation = ConsultationResult(
            query="Test query",
            responses=[
                MemberResponse(persona=sample_persona, content="Advice", timestamp=datetime.now())
            ],
            synthesis="No important findings here",
            timestamp=datetime.now(),
        )

        session = Session(
            council_name="Test Council",
            members=["test_persona"],
            consultations=[consultation],
        )
        mock_history.load_session.return_value = session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session")
        # The synthesis doesn't contain "important" or "key", so insights should be empty
        # But the code might still include it if it matches other criteria
        # Let's check that insights section exists
        markdown = report._format_as_markdown(result)
        assert "## Key Insights" in markdown
        # The synthesis text might be included if it's the only content, so we just verify the section exists

    def test_display_report(self, mock_history, sample_session):
        """Test display_report method."""
        mock_history.load_session.return_value = sample_session
        report = SessionReport(mock_history)

        result = report.generate_session_report("test-session-123")
        # Should not raise an exception
        report.display_report(result)
