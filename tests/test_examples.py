import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add examples to path
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
sys.path.append(str(EXAMPLES_DIR))


def test_quickstart():
    """Test that quickstart.py runs without error."""
    # Import dynamically to avoid top-level import errors if deps missing
    import quickstart

    # Mock print to suppress output
    with patch("builtins.print"):
        quickstart.main()


def test_simple_example():
    """Test successful run of simple_example.py."""
    import simple_example

    # Mock environment variables
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "fake-key"}):
        # Mock Council to avoid actual API calls
        with patch("simple_example.Council") as mock_council_class:
            # Setup mock return
            mock_instance = mock_council_class.for_domain.return_value
            mock_result = MagicMock()
            mock_result.synthesis = "Test synthesis"
            mock_result.responses = []
            mock_instance.consult.return_value = mock_result

            # Mock list_members to return empty or specific list
            mock_member = MagicMock()
            mock_member.name = "Test Persona"
            mock_instance.list_members.return_value = [mock_member]

            with patch("builtins.print"):
                simple_example.main()


def test_simple_example_no_key():
    """Test simple_example.py handles missing API key."""
    import simple_example

    # Ensure no keys
    with patch.dict("os.environ", {}, clear=True):
        with patch("sys.exit") as mock_exit:
            with patch("builtins.print"):
                simple_example.main()
                mock_exit.assert_called_with(1)


def test_review_repository():
    """Test review_repository.py example."""
    import review_repository

    # Mock mocks
    with (
        patch.dict("os.environ", {"ANTHROPIC_API_KEY": "fake-key"}),
        patch("review_repository.Council") as mock_council_class,
        patch("review_repository.RepositoryReviewer") as mock_reviewer_class,
        patch("builtins.print"),
    ):
        # Setup mocks
        # We don't use mock_council_class widely here, but ensuring it's patched prevents real calls
        _ = mock_council_class

        mock_reviewer_instance = mock_reviewer_class.return_value
        mock_reviewer_instance.gather_context.return_value = {
            "files": [],
            "key_files": [],
            "project_name": "test-repo",
        }
        mock_reviewer_instance.format_context.return_value = "Context"

        mock_result = MagicMock()
        mock_result.to_markdown.return_value = "Markdown Report"
        mock_reviewer_instance.review_code_quality.return_value = mock_result
        mock_reviewer_instance.review_design_ux.return_value = mock_result
        mock_reviewer_instance.review_security.return_value = mock_result

        # Run main
        review_repository.main()
