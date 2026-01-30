"""Repository Reviewer Tool."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.council import ConsultationResult, Council

logger = logging.getLogger(__name__)


class RepositoryReviewer:
    """Tool for reviewing repositories using Council AI."""

    DEFAULT_EXCLUDED_DIRS = {
        "__pycache__",
        "node_modules",
        ".git",
        ".venv",
        "venv",
        ".idea",
        ".vscode",
        "build",
        "dist",
        ".pytest_cache",
    }

    def __init__(
        self,
        council: Council,
        max_file_content_length: int = 5000,
        excluded_dirs: Optional[Set[str]] = None,
    ):
        self.council = council
        self.max_file_content_length = max_file_content_length
        self.excluded_dirs = excluded_dirs or self.DEFAULT_EXCLUDED_DIRS

    def gather_context(self, repo_root: Path) -> Dict[str, Any]:
        """Gather context about the repository."""
        context: Dict[str, Any] = {
            "project_name": repo_root.name,
            "description": "Project codebase",
            "key_files": [],
            "structure": {},
        }

        # Identify key files heuristically
        key_file_patterns = [
            "README.md",
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "setup.py",
            "Cargo.toml",
            "go.mod",
            "Makefile",
            "Dockerfile",
        ]

        # Add src/main files if they exist
        repo_files = list(repo_root.rglob("*"))

        # Prioritize key config/readme files
        for pattern in key_file_patterns:
            f = repo_root / pattern
            if f.exists() and f.is_file():
                self._add_file_to_context(f, repo_root, context)

        # Add a sampling of source files (simple heuristic: limits to top 5 largest source files)
        # In a real tool this would be smarter, but this is a good start
        source_extensions = {".py", ".js", ".ts", ".rs", ".go", ".c", ".cpp", ".java"}
        source_files = [
            f
            for f in repo_files
            if f.is_file()
            and f.suffix in source_extensions
            and not any(p in f.parts for p in self.excluded_dirs)
        ]

        # specific focus on critical logic (often init or core files)
        for f in source_files:
            if f.name == "__init__.py" or "core" in f.parts or "main" in f.name:
                if len(context["key_files"]) < 10:  # Limit total context files
                    self._add_file_to_context(f, repo_root, context)

        # Structure
        context["structure"] = self._list_directory_structure(repo_root, max_depth=2)

        return context

    def _add_file_to_context(self, file_path: Path, repo_root: Path, context: Dict[str, Any]):
        """Helper to add file content to context."""
        try:
            # Check if already added
            rel_path = str(file_path.relative_to(repo_root))
            if any(f["path"] == rel_path for f in context["key_files"]):
                return

            content = file_path.read_text(encoding="utf-8")
            if len(content) > self.max_file_content_length:
                content = content[: self.max_file_content_length] + "\n... (truncated)"

            context["key_files"].append({"path": rel_path, "content": content})
        except Exception as e:
            logger.debug(f"Skipping unreadable file {file_path}: {e}")

    def _list_directory_structure(
        self, path: Path, max_depth: int = 1, current_depth: int = 0
    ) -> Any:
        """List directory structure recursively."""
        if current_depth >= max_depth:
            return []

        structure: List[Any] = []
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith(".") or item.name in self.excluded_dirs:
                    continue

                if item.is_file():
                    structure.append(item.name)
                elif item.is_dir():
                    sub_items = self._list_directory_structure(item, max_depth, current_depth + 1)
                    structure.append({item.name: sub_items})
        except Exception as e:
            logger.debug(f"Error listing directory {path}: {e}")

        return structure

    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context into a string for the LLM."""
        lines = [
            f"# Review Context: {context['project_name']}",
            "",
            "## Structure",
        ]

        lines.append(self._format_structure(context["structure"]))
        lines.append("")
        lines.append("## Key Files")

        for f in context["key_files"]:
            lines.append(f"\n### {f['path']}")
            lines.append("```")
            lines.append(f["content"])
            lines.append("```")

        return "\n".join(lines)

    def _format_structure(self, structure: List[Any], indent: int = 0) -> str:
        lines = []
        prefix = "  " * indent
        for item in structure:
            if isinstance(item, dict):
                for k, v in item.items():
                    lines.append(f"{prefix}- {k}/")
                    if v:
                        lines.append(self._format_structure(v, indent + 1))
            else:
                lines.append(f"{prefix}- {item}")
        return "\n".join(lines)

    def review_code_quality(self, context_str: str) -> ConsultationResult:
        query = """
        Review the code quality and architecture.
        Focus on: Organization, Patterns, Security, Cognitive Load, and Best Practices.
        """
        return self.council.consult(query, context=context_str)

    def review_design_ux(self, context_str: str) -> ConsultationResult:
        query = """
        Review design and user experience (API/CLI).
        Focus on: API Design, CLI Usability, Documentation, Developer Experience, Simplicity.
        """
        return self.council.consult(query, context=context_str)

    def review_security(self, context_str: str) -> ConsultationResult:
        query = """
        Perform a security audit.
        Focus on: Vulnerabilities, Input Validation, Dependency Risks, Auth/Authn, Data Protection.
        """
        return self.council.consult(query, context=context_str)
