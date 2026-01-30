#!/usr/bin/env python3
"""
Context Injection Examples for Council AI

This script demonstrates various ways to inject context, code, images,
and markdown files into Council AI consultations.

To run:
1. Install: pip install -e ".[anthropic]"
2. Set API key: export ANTHROPIC_API_KEY="your-key"
3. Run: python examples/context_injection_example.py
"""

import os
import sys
from pathlib import Path

from council_ai import Council
from council_ai.utils.context import load_code_files, load_context_from_files, load_markdown_files


def example_1_basic_context():
    """Example 1: Basic string context injection."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Context Injection")
    print("=" * 60)

    council = Council(api_key=os.environ.get("ANTHROPIC_API_KEY"), provider="anthropic")
    council.add_member("rams")

    context = """
    Project Background:
    - Building a REST API for user management
    - Using FastAPI framework
    - Target: High performance, low latency
    - Team: 5 engineers, 2 designers
    - Launch target: Q2 2024
    """

    result = council.consult(
        "Should we use async/await for all endpoints?",
        context=context,
    )

    print("\nSynthesis:")
    print(result.synthesis)
    print("\n" + "-" * 60)


def example_2_markdown_files():
    """Example 2: Loading markdown files."""
    print("\n" + "=" * 60)
    print("Example 2: Loading Markdown Files")
    print("=" * 60)

    council = Council(api_key=os.environ.get("ANTHROPIC_API_KEY"), provider="anthropic")
    council.add_member("rams")

    # Check if README exists
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / "README.md"

    if readme_path.exists():
        context = load_markdown_files([readme_path])
        result = council.consult(
            "Summarize the key features and goals of this project",
            context=context,
        )
        print("\nSynthesis:")
        print(result.synthesis)
    else:
        print(f"README.md not found at {readme_path}")

    print("\n" + "-" * 60)


def example_3_code_files():
    """Example 3: Loading code files."""
    print("\n" + "=" * 60)
    print("Example 3: Loading Code Files")
    print("=" * 60)

    council = Council(api_key=os.environ.get("ANTHROPIC_API_KEY"), provider="anthropic")
    council.add_member("rams")
    council.add_member("kahneman")

    # Load some code files from the project
    repo_root = Path(__file__).parent.parent
    code_files = [
        repo_root / "src" / "council_ai" / "core" / "council.py",
        repo_root / "src" / "council_ai" / "core" / "persona.py",
    ]

    # Filter to only existing files
    existing_files = [f for f in code_files if f.exists()]

    if existing_files:
        context = load_code_files(existing_files, max_length=10000)
        result = council.consult(
            "Review this code for design simplicity and cognitive load",
            context=context,
        )
        print("\nSynthesis:")
        print(result.synthesis)
    else:
        print("Code files not found")

    print("\n" + "-" * 60)


def example_4_multiple_files():
    """Example 4: Loading multiple files of different types."""
    print("\n" + "=" * 60)
    print("Example 4: Loading Multiple Files")
    print("=" * 60)

    council = Council(api_key=os.environ.get("ANTHROPIC_API_KEY"), provider="anthropic")
    council.add_member("rams")
    council.add_member("kahneman")
    council.add_member("holman")

    repo_root = Path(__file__).parent.parent
    files = [
        repo_root / "README.md",
        repo_root / "pyproject.toml",
        repo_root / "src" / "council_ai" / "__init__.py",
    ]

    # Filter to only existing files
    existing_files = [f for f in files if f.exists()]

    if existing_files:
        context = load_context_from_files(existing_files, max_length=15000)
        result = council.consult(
            "Provide a comprehensive project review focusing on: "
            "1. Design simplicity (Rams perspective) "
            "2. Cognitive load (Kahneman perspective) "
            "3. Security considerations (Holman perspective)",
            context=context,
        )
        print("\nSynthesis:")
        print(result.synthesis)
    else:
        print("Files not found")

    print("\n" + "-" * 60)


def example_5_persona_context():
    """Example 5: Injecting context at persona level."""
    print("\n" + "=" * 60)
    print("Example 5: Persona-Level Context")
    print("=" * 60)

    from council_ai.core.persona import get_persona

    council = Council(api_key=os.environ.get("ANTHROPIC_API_KEY"), provider="anthropic")

    # Clone a persona with custom context
    base_persona = get_persona("rams")
    custom_persona = base_persona.clone(
        new_id="rams_project_context",
        prompt_prefix="""
        Project Context:
        - Building a design system for a SaaS platform
        - Target users: Enterprise customers
        - Team: 10 designers, 5 frontend engineers
        - Design principles: Minimalism, accessibility, performance

        When responding, consider this project context.
        """,
    )

    council.add_member(custom_persona)

    result = council.consult(
        "Should we use a component library like Material-UI or build custom components?",
    )

    print("\nSynthesis:")
    print(result.synthesis)
    print("\n" + "-" * 60)


def main():
    """Run all examples."""
    print(
        """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🏛️  Council AI - Context Injection Examples        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    )

    # Check API key
    api_key = (
        os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
    )

    if not api_key:
        print("❌ Error: No API key found.")
        print("\nPlease set one of:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  export OPENAI_API_KEY='your-key'")
        print("  export GEMINI_API_KEY='your-key'")
        sys.exit(1)

    try:
        # Run examples
        example_1_basic_context()
        example_2_markdown_files()
        example_3_code_files()
        example_4_multiple_files()
        example_5_persona_context()

        print("\n✅ All examples completed!")
        print("\nFor more details, see: documentation/CONTEXT_INJECTION_GUIDE.md")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
