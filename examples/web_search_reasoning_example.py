#!/usr/bin/env python3
"""
Web Search and Reasoning Modes Example

Demonstrates how to use web search and reasoning modes in Council AI.

To run:
1. Install: pip install -e ".[anthropic]"
2. Set API keys:
   - export ANTHROPIC_API_KEY="your-key"
   - export TAVILY_API_KEY="your-key" (optional, for web search)
3. Run: python examples/web_search_reasoning_example.py
"""

import os
import sys

from council_ai import Council, CouncilConfig
from council_ai.core.persona import get_persona


def example_1_web_search():
    """Example 1: Using web search for current information."""
    print("\n" + "=" * 60)
    print("Example 1: Web Search")
    print("=" * 60)

    # Check if web search is configured
    if not os.environ.get("TAVILY_API_KEY") and not os.environ.get("SERPER_API_KEY"):
        print("⚠️  Web search not configured. Set TAVILY_API_KEY or SERPER_API_KEY")
        print("   Skipping web search example...")
        return

    config = CouncilConfig(enable_web_search=True)
    council = Council(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        provider="anthropic",
        config=config,
    )
    council.add_member("rams")

    result = council.consult(
        "What are the latest trends in API design in 2024?",
    )

    print("\nSynthesis:")
    print(result.synthesis)
    print("\n" + "-" * 60)


def example_2_chain_of_thought():
    """Example 2: Chain-of-thought reasoning."""
    print("\n" + "=" * 60)
    print("Example 2: Chain-of-Thought Reasoning")
    print("=" * 60)

    config = CouncilConfig(reasoning_mode="chain_of_thought")
    council = Council(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        provider="anthropic",
        config=config,
    )
    council.add_member("rams")

    result = council.consult(
        "Should we implement rate limiting at the API gateway or application level?",
    )

    print("\nResponse (with step-by-step reasoning):")
    for response in result.responses:
        print(f"\n{response.persona.emoji} {response.persona.name}:")
        print(response.content)
    print("\n" + "-" * 60)


def example_3_tree_of_thought():
    """Example 3: Tree-of-thought reasoning."""
    print("\n" + "=" * 60)
    print("Example 3: Tree-of-Thought Reasoning")
    print("=" * 60)

    config = CouncilConfig(reasoning_mode="tree_of_thought")
    council = Council(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        provider="anthropic",
        config=config,
    )
    council.add_member("rams")
    council.add_member("kahneman")

    result = council.consult(
        "Should we adopt microservices architecture?",
    )

    print("\nResponses (exploring multiple reasoning paths):")
    for response in result.responses:
        print(f"\n{response.persona.emoji} {response.persona.name}:")
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
    print("\n" + "-" * 60)


def example_4_persona_specific():
    """Example 4: Persona-specific reasoning modes."""
    print("\n" + "=" * 60)
    print("Example 4: Persona-Specific Reasoning Modes")
    print("=" * 60)

    council = Council(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        provider="anthropic",
    )

    # Different reasoning modes for different personas
    rams_analytical = get_persona("rams").clone(
        new_id="rams_analytical",
        reasoning_mode="analytical",
    )

    kahneman_reflective = get_persona("kahneman").clone(
        new_id="kahneman_reflective",
        reasoning_mode="reflective",
    )

    council.add_member(rams_analytical)
    council.add_member(kahneman_reflective)

    result = council.consult(
        "Review our API design for simplicity and cognitive load",
    )

    print("\nResponses:")
    for response in result.responses:
        mode_str = response.persona.reasoning_mode or "standard"
        print(f"\n{response.persona.emoji} {response.persona.name} ({mode_str}):")
        content = (
            response.content[:400] + "..." if len(response.content) > 400 else response.content
        )
        print(content)
    print("\n" + "-" * 60)


def example_5_combined():
    """Example 5: Combined web search + reasoning."""
    print("\n" + "=" * 60)
    print("Example 5: Combined Web Search + Reasoning")
    print("=" * 60)

    # Check if web search is configured
    if not os.environ.get("TAVILY_API_KEY") and not os.environ.get("SERPER_API_KEY"):
        print("⚠️  Web search not configured. Set TAVILY_API_KEY or SERPER_API_KEY")
        print("   Showing reasoning mode only...")
        config = CouncilConfig(reasoning_mode="analytical")
    else:
        config = CouncilConfig(
            enable_web_search=True,
            reasoning_mode="analytical",
        )

    council = Council(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        provider="anthropic",
        config=config,
    )

    # Persona with web search enabled
    researcher = get_persona("rams").clone(
        new_id="researcher",
        enable_web_search=True,
        reasoning_mode="analytical",
    )

    council.add_member(researcher)

    result = council.consult(
        "What are current best practices for API rate limiting in 2024?",
    )

    print("\nResponse (with web search + analytical reasoning):")
    for response in result.responses:
        print(f"\n{response.persona.emoji} {response.persona.name}:")
        print(response.content[:600] + "..." if len(response.content) > 600 else response.content)
    print("\n" + "-" * 60)


def main():
    """Run all examples."""
    print(
        """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🏛️  Council AI - Web Search & Reasoning Examples       ║
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
        example_1_web_search()
        example_2_chain_of_thought()
        example_3_tree_of_thought()
        example_4_persona_specific()
        example_5_combined()

        print("\n✅ All examples completed!")
        print("\nFor more details, see: documentation/WEB_SEARCH_AND_REASONING.md")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
