#!/usr/bin/env python3
"""
Council AI - Quickstart Demo

This script demonstrates the core features of Council AI without requiring
an API key - perfect for understanding the system before diving in.
"""

from council_ai import (
    Council,
    Persona,
    PersonaCategory,
    list_personas,
    list_domains,
    get_persona,
    get_domain,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def demo_personas():
    """Show available personas."""
    print_section("Available Personas")
    
    personas = list_personas()
    print(f"\nCouncil AI includes {len(personas)} built-in expert personas:\n")
    
    for persona in personas:
        print(f"{persona.emoji} {persona.name} ({persona.category.value})")
        print(f"   {persona.title}")
        print(f"   Core Question: \"{persona.core_question}\"")
        print(f"   Razor: \"{persona.razor}\"")
        print()


def demo_domains():
    """Show available domains."""
    print_section("Available Domains")
    
    domains = list_domains()
    print(f"\nCouncil AI includes {len(domains)} domain presets:\n")
    
    for domain in domains:
        personas_str = ", ".join(domain.default_personas[:3])
        if len(domain.default_personas) > 3:
            personas_str += "..."
        print(f"📁 {domain.id}: {domain.name}")
        print(f"   {domain.description}")
        print(f"   Default personas: {personas_str}")
        print()


def demo_persona_details():
    """Show detailed persona information."""
    print_section("Persona Deep Dive: Dieter Rams")
    
    rams = get_persona("rams")
    print(f"\n{rams.emoji} {rams.name} - {rams.title}\n")
    print(f"Category: {rams.category.value}")
    print(f"Core Question: \"{rams.core_question}\"")
    print(f"Razor: \"{rams.razor}\"\n")
    
    print("Focus Areas:")
    for area in rams.focus_areas:
        print(f"  • {area}")
    
    print("\nKey Traits:")
    for trait in rams.traits:
        print(f"  • {trait.name} (weight: {trait.weight})")
        print(f"    {trait.description}")


def demo_domain_details():
    """Show detailed domain information."""
    print_section("Domain Deep Dive: Business Strategy")
    
    business = get_domain("business")
    print(f"\n📁 {business.name}\n")
    print(f"Description: {business.description}")
    print(f"Category: {business.category.value}")
    print(f"Recommended mode: {business.recommended_mode}\n")
    
    print("Default Personas:")
    for persona_id in business.default_personas:
        try:
            p = get_persona(persona_id)
            print(f"  {p.emoji} {p.name} - {p.title}")
        except ValueError:
            print(f"  • {persona_id}")
    
    print("\nExample Queries:")
    for query in business.example_queries:
        print(f"  • {query}")


def demo_council_setup():
    """Show how to set up a council."""
    print_section("Setting Up a Council (No API Key Required)")
    
    print("\nMethod 1: Use a domain preset")
    print("─" * 40)
    print("""
council = Council.for_domain("business", api_key="your-key")
# Automatically includes: grove, taleb, dempsey, kahneman
""")
    
    # Actually create it to show it works
    try:
        council = Council.for_domain("business", api_key="demo-key")
        members = council.list_members()
        print(f"✓ Council created with {len(members)} members:")
        for m in members:
            print(f"  {m.emoji} {m.name}")
    except Exception as e:
        print(f"Note: {e}")
    
    print("\nMethod 2: Build a custom council")
    print("─" * 40)
    print("""
council = Council(api_key="your-key")
council.add_member("rams")      # Design perspective
council.add_member("holman")    # Security perspective
council.add_member("grove")     # Strategy perspective
""")


def demo_consultation_modes():
    """Explain consultation modes."""
    print_section("Consultation Modes")
    
    modes = {
        "INDIVIDUAL": "Each member responds separately",
        "SYNTHESIS": "Individual responses + synthesized summary (default)",
        "SEQUENTIAL": "Members respond in order, seeing previous responses",
        "DEBATE": "Multiple rounds of discussion",
        "VOTE": "Members vote on a decision",
    }
    
    print("\nCouncil AI supports 5 consultation modes:\n")
    for mode, description in modes.items():
        print(f"  • {mode}")
        print(f"    {description}\n")


def demo_usage_example():
    """Show a usage example."""
    print_section("Usage Example")
    
    print("""
# 1. Set your API key
export ANTHROPIC_API_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"

# 2. Use the CLI
council consult "Should I take this job offer?"
council consult --domain startup "Should we pivot?"
council interactive

# 3. Or use the Python API
from council_ai import Council

council = Council.for_domain("business", api_key="your-key")
result = council.consult("Should we expand to Europe?")

# Access the synthesis
print(result.synthesis)

# Access individual responses
for response in result.responses:
    print(f"{response.persona.emoji} {response.persona.name}:")
    print(response.content)
""")


def main():
    """Run the quickstart demo."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🏛️  Council AI - Quickstart Demo                 ║
║                                                           ║
║   Explore features without an API key                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Run demos
    demo_personas()
    demo_domains()
    demo_persona_details()
    demo_domain_details()
    demo_council_setup()
    demo_consultation_modes()
    demo_usage_example()
    
    # Final message
    print_section("Next Steps")
    print("""
1. Get an API key from Anthropic (https://anthropic.com) or OpenAI
2. Install Council AI with a provider:
   pip install -e .[anthropic]
   
3. Set your API key:
   export ANTHROPIC_API_KEY="your-key"
   
4. Try the simple example:
   python examples/simple_example.py
   
5. Explore the CLI:
   council --help
   council persona list
   council domain list

6. Check the documentation:
   - README.md for full documentation
   - examples/README.md for more examples
   - CONTRIBUTING.md to contribute

Happy consulting! 🏛️
""")


if __name__ == "__main__":
    main()
