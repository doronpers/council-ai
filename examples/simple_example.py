#!/usr/bin/env python3
"""
Simple example demonstrating Council AI basic usage.

To run this example:
1. Install council-ai: pip install -e .
2. Set your API key: export ANTHROPIC_API_KEY="your-key"
3. Run: python examples/simple_example.py
"""

import sys
from council_ai import Council

def main():
    # Check if API key is available
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Error: No API key found.")
        print("\nPlease set one of:")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    # Determine provider
    provider = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "openai"
    
    print("🏛️  Council AI - Simple Example")
    print("=" * 50)
    print(f"Provider: {provider}")
    print()
    
    # Create a council for business decisions
    print("Creating business strategy council...")
    council = Council.for_domain("business", api_key=api_key, provider=provider)
    
    print(f"Council members: {', '.join(m.name for m in council.list_members())}")
    print()
    
    # Ask a question
    query = "Should a B2B SaaS company expand to Europe or focus on growing US market share?"
    print(f"Query: {query}")
    print()
    print("Consulting council... (this may take a moment)")
    print()
    
    try:
        result = council.consult(query)
        
        # Print synthesis
        print("=" * 50)
        print("SYNTHESIZED RECOMMENDATION")
        print("=" * 50)
        print(result.synthesis)
        print()
        
        # Print individual responses
        print("=" * 50)
        print("INDIVIDUAL PERSPECTIVES")
        print("=" * 50)
        for response in result.responses:
            if not response.error:
                print(f"\n{response.persona.emoji} {response.persona.name} ({response.persona.title}):")
                print("-" * 50)
                print(response.content)
                print()
        
        print("✓ Consultation complete!")
        
    except Exception as e:
        print(f"❌ Error during consultation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
