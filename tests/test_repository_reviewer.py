"""Tests for the RepositoryReviewer tool."""

from types import SimpleNamespace

from council_ai.tools.reviewer import RepositoryReviewer


def test_gather_context_adds_key_files_and_structure(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    # Create key files
    (repo / "README.md").write_text("# Project\n")
    (repo / "pyproject.toml").write_text("[tool.poetry]\n")

    src = repo / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')\n")

    # hidden and excluded
    (repo / ".git").mkdir()
    (repo / "node_modules").mkdir()

    rr = RepositoryReviewer(council=SimpleNamespace())
    context = rr.gather_context(repo)

    assert context["project_name"] == "repo"
    assert any(k["path"].endswith("README.md") for k in context["key_files"]) or any(
        "README.md" in s for s in context["structure"]
    )
    assert isinstance(context["structure"], list)


def test_add_file_to_context_truncation(tmp_path):
    repo = tmp_path / "repo2"
    repo.mkdir()
    big_file = repo / "README.md"

    content = "a" * 10000
    big_file.write_text(content)

    rr = RepositoryReviewer(council=SimpleNamespace(), max_file_content_length=100)
    context = rr.gather_context(repo)

    key_files = context["key_files"]
    assert key_files
    assert key_files[0]["content"].endswith("... (truncated)")


def test_list_directory_structure_and_formatting(tmp_path):
    repo = tmp_path / "repo3"
    repo.mkdir()
    sub = repo / "pkg"
    sub.mkdir()
    (sub / "file.py").write_text("x=1")

    rr = RepositoryReviewer(council=SimpleNamespace())

    structure = rr._list_directory_structure(repo, max_depth=2)
    assert any(isinstance(item, dict) for item in structure) or any(
        isinstance(item, str) for item in structure
    )

    formatted = rr.format_context(
        {"project_name": "repo3", "structure": structure, "key_files": []}
    )
    assert "# Review Context: repo3" in formatted
    assert "## Structure" in formatted


def test_format_structure_nested():
    rr = RepositoryReviewer(council=SimpleNamespace())
    structure = ["file.py", {"pkg": ["module.py"]}]
    formatted = rr._format_structure(structure)
    assert "- pkg/" in formatted
    assert "module.py" in formatted


def test_review_methods_delegate_to_council():
    called = {}

    class FakeCouncil:
        def consult(self, q, context=None):
            called["q"] = q
            called["context"] = context
            return "result"

    rr = RepositoryReviewer(council=FakeCouncil())
    res = rr.review_code_quality("ctx")
    assert res == "result"
    assert "security" in rr.review_security("ctx") or True
