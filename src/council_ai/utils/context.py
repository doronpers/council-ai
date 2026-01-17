"""
Context loading utilities for Council AI.

These utilities help load and format files (markdown, code, images, etc.)
for injection into Council AI consultations.
"""

import base64
import mimetypes
from pathlib import Path
from typing import List, Optional, Sequence


def load_markdown_files(
    file_paths: Sequence[str | Path],
    max_length: Optional[int] = None,
    truncate_message: str = "... (truncated)",
) -> str:
    """
    Load one or more markdown files and format them for context.

    Args:
        file_paths: List of paths to markdown files
        max_length: Maximum total length (None = no limit)
        truncate_message: Message to append when truncating

    Returns:
        Formatted string with all markdown content

    Example:
        >>> context = load_markdown_files(["README.md", "CHANGELOG.md"])
        >>> result = council.consult("Review docs", context=context)
    """
    sections = []
    total_length = 0

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8")
            section = f"# {path.name}\n\n{content}"
            sections.append(section)
            total_length += len(section)

            if max_length and total_length > max_length:
                # Truncate the last section
                remaining = max_length - (total_length - len(section))
                sections[-1] = sections[-1][:remaining] + f"\n\n{truncate_message}"
                break
        except Exception as e:
            sections.append(f"# {path.name}\n\n[Error reading file: {e}]")

    return "\n\n---\n\n".join(sections)


def load_code_files(
    file_paths: Sequence[str | Path],
    max_length: Optional[int] = None,
    truncate_message: str = "... (truncated)",
) -> str:
    """
    Load one or more code files and format them with syntax highlighting.

    Args:
        file_paths: List of paths to code files
        max_length: Maximum total length (None = no limit)
        truncate_message: Message to append when truncating

    Returns:
        Formatted string with code blocks

    Example:
        >>> context = load_code_files(["src/main.py", "src/utils.py"])
        >>> result = council.consult("Review code", context=context)
    """
    sections = []
    total_length = 0

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8")
            # Detect language from extension
            lang = _detect_language(path)
            section = f"## {path}\n\n```{lang}\n{content}\n```"
            sections.append(section)
            total_length += len(section)

            if max_length and total_length > max_length:
                # Truncate the last section
                remaining = max_length - (total_length - len(section))
                sections[-1] = sections[-1][:remaining] + f"\n{truncate_message}\n```"
                break
        except Exception as e:
            sections.append(f"## {path}\n\n[Error reading file: {e}]")

    return "\n\n".join(sections)


def load_text_files(
    file_paths: Sequence[str | Path],
    max_length: Optional[int] = None,
    truncate_message: str = "... (truncated)",
) -> str:
    """
    Load one or more text files (any format).

    Args:
        file_paths: List of paths to text files
        max_length: Maximum total length (None = no limit)
        truncate_message: Message to append when truncating

    Returns:
        Formatted string with file contents
    """
    sections = []
    total_length = 0

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8")
            section = f"## {path.name}\n\n{content}"
            sections.append(section)
            total_length += len(section)

            if max_length and total_length > max_length:
                remaining = max_length - (total_length - len(section))
                sections[-1] = sections[-1][:remaining] + f"\n\n{truncate_message}"
                break
        except Exception as e:
            sections.append(f"## {path.name}\n\n[Error reading file: {e}]")

    return "\n\n---\n\n".join(sections)


def load_images(
    file_paths: Sequence[str | Path],
    include_base64: bool = True,
) -> str:
    """
    Load images and prepare them for context injection.

    Note: Image support varies by LLM provider. Some providers require
    images to be passed via their specific API rather than in context text.

    Args:
        file_paths: List of paths to image files
        include_base64: Whether to include base64-encoded data

    Returns:
        Formatted string describing images (base64 data if requested)

    Example:
        >>> context = load_images(["diagram.png", "screenshot.jpg"])
        >>> # Note: For actual image support, use provider's image API
    """
    sections = []

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        try:
            mime_type, _ = mimetypes.guess_type(str(path))
            section = f"## Image: {path.name}\n"
            section += f"Type: {mime_type or 'unknown'}\n"
            section += f"Size: {path.stat().st_size} bytes\n"

            if include_base64:
                with open(path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                section += f"\nBase64 Data:\n```\n{image_data[:100]}...\n```\n"
                section += (
                    "\n*Note: Full base64 data available. "
                    "Use provider's image API for actual image support.*"
                )

            sections.append(section)
        except Exception as e:
            sections.append(f"## {path.name}\n\n[Error reading image: {e}]")

    return "\n\n---\n\n".join(sections)


def load_context_from_files(
    file_paths: Sequence[str | Path],
    max_length: Optional[int] = None,
    truncate_message: str = "... (truncated)",
) -> str:
    """
    Automatically detect file types and load them appropriately.

    Supports:
    - Markdown files (.md, .markdown)
    - Code files (.py, .js, .ts, .rs, .go, .java, .cpp, .c, .h, etc.)
    - Text files (.txt, .yaml, .yml, .json, .toml, .ini, .cfg)
    - Images (.png, .jpg, .jpeg, .gif, .webp)

    Args:
        file_paths: List of paths to files
        max_length: Maximum total length (None = no limit)
        truncate_message: Message to append when truncating

    Returns:
        Formatted string with all file contents

    Example:
        >>> context = load_context_from_files([
        ...     "README.md",
        ...     "src/main.py",
        ...     "config.yaml"
        ... ])
        >>> result = council.consult("Review project", context=context)
    """
    markdown_files: List[Path] = []
    code_files: List[Path] = []
    text_files: List[Path] = []
    image_files: List[Path] = []

    # Categorize files
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        suffix = path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            markdown_files.append(path)
        elif suffix in {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".rs",
            ".go",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".scala",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
        }:
            code_files.append(path)
        elif suffix in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".svg",
            ".bmp",
        }:
            image_files.append(path)
        else:
            # Treat as text file (yaml, json, toml, etc.)
            text_files.append(path)

    # Load each category
    sections = []

    if markdown_files:
        sections.append("## Documentation Files\n")
        sections.append(load_markdown_files(markdown_files, max_length, truncate_message))

    if code_files:
        sections.append("\n## Code Files\n")
        sections.append(load_code_files(code_files, max_length, truncate_message))

    if text_files:
        sections.append("\n## Configuration & Text Files\n")
        sections.append(load_text_files(text_files, max_length, truncate_message))

    if image_files:
        sections.append("\n## Images\n")
        sections.append(load_images(image_files, include_base64=False))
        sections.append(
            "\n*Note: For actual image support, use your LLM provider's image API. "
            "Most providers (Claude 3, GPT-4 Vision) support images via their API."
        )

    return "\n\n".join(sections)


def format_code_context(
    file_path: str | Path,
    content: str,
    language: Optional[str] = None,
) -> str:
    """
    Format code content with language tag.

    Args:
        file_path: Path to the code file
        content: Code content
        language: Programming language (auto-detected if None)

    Returns:
        Formatted code block
    """
    path = Path(file_path)
    lang = language or _detect_language(path)
    return f"## {path}\n\n```{lang}\n{content}\n```"


def format_file_context(
    file_path: str | Path,
    content: str,
    file_type: Optional[str] = None,
) -> str:
    """
    Format file content with metadata.

    Args:
        file_path: Path to the file
        content: File content
        file_type: File type description (auto-detected if None)

    Returns:
        Formatted file section
    """
    path = Path(file_path)
    ftype = file_type or path.suffix
    return f"## {path.name} ({ftype})\n\n{content}"


def _detect_language(path: Path) -> str:
    """Detect programming language from file extension."""
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".fish": "fish",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".toml": "toml",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".r": "r",
        ".m": "matlab",
        ".jl": "julia",
    }

    suffix = path.suffix.lower()
    return extension_map.get(suffix, "text")
