#!/usr/bin/env python3
"""
Repository Review using Council AI Personas

This script demonstrates using the Council AI `RepositoryReviewer` tool
programmatically to audit a codebase.

To run this script:
1. Install council-ai: pip install -e ".[anthropic]" (or openai/gemini)
2. Set your API key: export ANTHROPIC_API_KEY="your-key"
3. Run: python examples/review_repository.py
"""

import os
import sys
from pathlib import Path

from council_ai import Council
from council_ai.tools.reviewer import RepositoryReviewer


def main():
    print(
        """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🏛️  Council AI - Repository Review Example         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    )

    # 1. Setup API configuration
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
        sys.exit(1)

    print(f"Provider: {provider}")

    # 2. Initialize Council with expert personas
    print("👥 Assembling Council...")
    council = Council(api_key=api_key, provider=provider)
    try:
        council.add_member("rams")      # Design
        council.add_member("kahneman")  # Cognitive Load
        council.add_member("holman")    # Security
        council.add_member("taleb")     # Risk
    except ValueError as e:
        print(f"Warning: {e}")

    # 3. Initialize Reviewer Tool
    reviewer = RepositoryReviewer(council)
    repo_path = Path(__file__).parent.parent

    # 4. Gather Context
    print(f"📁 Scanning repository: {repo_path.name}...")
    context = reviewer.gather_context(repo_path)
    context_str = reviewer.format_context(context)
    print(f"✓ Context gathered ({len(context['key_files'])} key files)")

    # 5. Run Reviews
    print("\n🔍 Reviewing Code Quality...")
    code_result = reviewer.review_code_quality(context_str)
    print(code_result.synthesis)

    print("\n🎨 Reviewing Design & UX...")
    design_result = reviewer.review_design_ux(context_str)
    print(design_result.synthesis)

    print("\n🛡️ Auditing Security...")
    sec_result = reviewer.review_security(context_str)
    print(sec_result.synthesis)

    print("\n✨ Done! (See 'council review --help' for the CLI version)")


if __name__ == "__main__":
    main()
