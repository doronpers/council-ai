#!/usr/bin/env python3
"""
Repository Review using Council AI Personas

This script demonstrates using Council AI to review a repository's code,
design/UX, and functionality by consulting the embedded council personas.

To run this script:
1. Install council-ai: pip install -e ".[anthropic]" (or openai/gemini)
2. Set your API key: export ANTHROPIC_API_KEY="your-key"
3. Run: python examples/review_repository.py
"""

import os
import sys
from pathlib import Path

from council_ai import Council

# Configuration constants
MAX_FILE_CONTENT_LENGTH = 5000  # Maximum characters to include from each file
EXCLUDED_DIRS = {"__pycache__", "node_modules", ".git"}  # Directories to skip


def gather_repository_context():
    """Gather context about the repository for the council to review."""
    repo_root = Path(__file__).parent.parent

    context = {
        "project_name": "Council AI",
        "description": "AI-powered advisory council system with customizable personas",
        "key_files": [],
        "structure": {},
    }

    # Key files to include in the review
    key_files = [
        "README.md",
        "pyproject.toml",
        "src/council_ai/__init__.py",
        "src/council_ai/core/council.py",
        "src/council_ai/core/persona.py",
        "src/council_ai/cli.py",
    ]

    for file_path in key_files:
        full_path = repo_root / file_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding="utf-8")
                # Limit content size for API constraints
                if len(content) > MAX_FILE_CONTENT_LENGTH:
                    content = content[:MAX_FILE_CONTENT_LENGTH] + "\n... (truncated)"
                context["key_files"].append(
                    {
                        "path": file_path,
                        "content": content,
                    }
                )
            except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as e:
                print(f"Warning: Could not read {file_path}: {e}")

    # Gather directory structure
    src_dir = repo_root / "src"
    if src_dir.exists():
        context["structure"]["src"] = list_directory_structure(src_dir, max_depth=2)

    examples_dir = repo_root / "examples"
    if examples_dir.exists():
        context["structure"]["examples"] = list_directory_structure(examples_dir)

    tests_dir = repo_root / "tests"
    if tests_dir.exists():
        context["structure"]["tests"] = list_directory_structure(tests_dir)

    return context


def list_directory_structure(path, max_depth=1, current_depth=0):
    """List directory structure up to a certain depth."""
    if current_depth >= max_depth:
        return []

    structure = []
    try:
        for item in sorted(path.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_file():
                structure.append(item.name)
            elif item.is_dir() and item.name not in EXCLUDED_DIRS:
                sub_items = list_directory_structure(item, max_depth, current_depth + 1)
                structure.append({item.name: sub_items})
    except (PermissionError, OSError) as e:
        # Skip directories we can't access
        print(f"Warning: Could not list directory {path}: {e}", file=sys.stderr)

    return structure


def format_context_for_review(context):
    """Format the repository context into a readable string for the council."""
    lines = [
        "# Repository Review Context",
        "",
        f"**Project**: {context['project_name']}",
        f"**Description**: {context['description']}",
        "",
        "## Repository Structure",
        "",
    ]

    for section, structure in context["structure"].items():
        lines.append(f"### {section}/")
        lines.append(format_structure(structure, indent=1))
        lines.append("")

    lines.append("## Key Files")
    lines.append("")

    for file_info in context["key_files"]:
        lines.append(f"### {file_info['path']}")
        lines.append("```")
        lines.append(file_info["content"])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def format_structure(structure, indent=0):
    """Format directory structure for display."""
    lines = []
    prefix = "  " * indent

    for item in structure:
        if isinstance(item, dict):
            for key, value in item.items():
                lines.append(f"{prefix}- {key}/")
                if value:
                    lines.append(format_structure(value, indent + 1))
        else:
            lines.append(f"{prefix}- {item}")

    return "\n".join(lines)


def review_code_quality(council, context_str):
    """Review code quality and architecture."""
    print("\n" + "=" * 60)
    print("📝 REVIEWING: Code Quality & Architecture")
    print("=" * 60)
    print("Council Members: Rams (Design), Holman (Security), Kahneman (UX)")
    print()

    query = """
Please review the code quality and architecture of this repository.

Focus on:
1. **Code Organization**: Is the project well-structured and maintainable?
2. **Design Patterns**: Are appropriate patterns used? Is the code elegant?
3. **Security**: What are potential security concerns or vulnerabilities?
4. **Cognitive Load**: Is the code easy to understand and use?
5. **Best Practices**: Does it follow Python best practices?

Provide constructive feedback with specific examples where possible.
"""

    result = council.consult(query, context=context_str)
    return result


def review_design_ux(council, context_str):
    """Review design and user experience."""
    print("\n" + "=" * 60)
    print("🎨 REVIEWING: Design & User Experience")
    print("=" * 60)
    print("Council Members: Rams (Simplicity), Kahneman (Cognition), Treasure (Communication)")
    print()

    query = """
Please review the design and user experience of this repository.

Focus on:
1. **API Design**: Is the Python API intuitive and well-designed?
2. **CLI Design**: Is the command-line interface easy to use?
3. **Documentation**: Is the README clear and comprehensive?
4. **Developer Experience**: How easy is it for developers to use this library?
5. **Communication**: Are concepts explained clearly?
6. **Simplicity**: Is the interface as simple as possible?

Provide recommendations for improving the user experience.
"""

    result = council.consult(query, context=context_str)
    return result


def review_functionality_robustness(council, context_str):
    """Review functionality and robustness."""
    print("\n" + "=" * 60)
    print("🛡️ REVIEWING: Functionality & Robustness")
    print("=" * 60)
    print("Council Members: Taleb (Risk), Grove (Strategy), Holman (Breaking)")
    print()

    query = """
Please review the functionality and robustness of this repository.

Focus on:
1. **Risk Assessment**: What could break or fail? What are edge cases?
2. **Strategic Position**: How does this compare to alternatives?
3. **Attack Surface**: How could someone misuse or break this?
4. **Resilience**: How well does it handle errors and edge cases?
5. **Completeness**: What features or safeguards are missing?
6. **Competitive Advantage**: What makes this unique or valuable?

Provide critical analysis and identify potential weaknesses.
"""

    result = council.consult(query, context=context_str)
    return result


def print_review_result(result, section_title):
    """Print a formatted review result."""
    print(f"\n{'─' * 60}")
    print(f"📊 {section_title}")
    print(f"{'─' * 60}\n")

    if result.synthesis:
        print("🎯 SYNTHESIZED REVIEW")
        print("=" * 60)
        print(result.synthesis)
        print()

    print("\n" + "=" * 60)
    print("💭 INDIVIDUAL PERSPECTIVES")
    print("=" * 60)

    for response in result.responses:
        if not response.error:
            print(f"\n{response.persona.emoji} {response.persona.name} ({response.persona.title})")
            print("-" * 60)
            print(response.content)
            print()


def main():
    """Run the repository review."""
    print(
        """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🏛️  Council AI - Repository Review                 ║
║                                                           ║
║   Using embedded personas to review code, design & UX     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    )

    # Check for API key
    api_key = None
    provider = None

    if os.environ.get("ANTHROPIC_API_KEY"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        provider = "anthropic"
    elif os.environ.get("OPENAI_API_KEY"):
        api_key = os.environ.get("OPENAI_API_KEY")
        provider = "openai"
    elif os.environ.get("GEMINI_API_KEY"):
        api_key = os.environ.get("GEMINI_API_KEY")
        provider = "gemini"

    if not api_key:
        print("❌ Error: No API key found.")
        print("\nPlease set one of:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  export OPENAI_API_KEY='your-key'")
        print("  export GEMINI_API_KEY='your-key'")
        sys.exit(1)

    print(f"Provider: {provider}")
    print()

    # Gather repository context
    print("📁 Gathering repository context...")
    context = gather_repository_context()
    context_str = format_context_for_review(context)
    print(f"✓ Context gathered ({len(context['key_files'])} key files)")
    print()

    # Review 1: Code Quality & Architecture
    print("🔍 Creating council for code quality review...")
    code_council = Council(api_key=api_key, provider=provider)
    code_council.add_member("rams")  # Design & Simplicity
    code_council.add_member("holman")  # Security
    code_council.add_member("kahneman")  # Cognitive Load

    try:
        code_result = review_code_quality(code_council, context_str)
        print_review_result(code_result, "Code Quality & Architecture Review")
    except Exception as e:
        print(f"❌ Error during code quality review: {e}")

    # Review 2: Design & UX
    print("\n🔍 Creating council for design/UX review...")
    design_council = Council(api_key=api_key, provider=provider)
    design_council.add_member("rams")  # Simplicity
    design_council.add_member("kahneman")  # Human Cognition
    design_council.add_member("treasure")  # Communication

    try:
        design_result = review_design_ux(design_council, context_str)
        print_review_result(design_result, "Design & User Experience Review")
    except Exception as e:
        print(f"❌ Error during design/UX review: {e}")

    # Review 3: Functionality & Robustness
    print("\n🔍 Creating council for functionality review...")
    func_council = Council(api_key=api_key, provider=provider)
    func_council.add_member("taleb")  # Risk & Antifragility
    func_council.add_member("grove")  # Strategic Position
    func_council.add_member("holman")  # Breaking Things

    try:
        func_result = review_functionality_robustness(func_council, context_str)
        print_review_result(func_result, "Functionality & Robustness Review")
    except Exception as e:
        print(f"❌ Error during functionality review: {e}")

    # Final summary
    print("\n" + "=" * 60)
    print("✅ REPOSITORY REVIEW COMPLETE")
    print("=" * 60)
    print(
        """
The council has provided comprehensive feedback on:
- Code quality and architecture
- Design and user experience
- Functionality and robustness

Use these insights to improve the repository!
"""
    )


if __name__ == "__main__":
    main()
