#!/usr/bin/env python3
"""
Package validation script - ensures Council AI is properly installed and working.
"""

import sys


def test_imports():
    """Test that all major imports work."""
    print("Testing imports...")
    try:
        from council_ai import (
            ConsultationMode,
            Council,
            Persona,
            PersonaCategory,
            get_domain,
            get_persona,
            list_domains,
            list_personas,
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_personas():
    """Test persona loading."""
    print("\nTesting persona loading...")
    try:
        from council_ai import get_persona, list_personas

        personas = list_personas()
        if len(personas) < 7:
            print(f"✗ Expected at least 7 personas, got {len(personas)}")
            return False

        # Test getting specific personas
        required_personas = ["rams", "kahneman", "grove", "taleb", "holman", "dempsey", "treasure"]
        for pid in required_personas:
            persona = get_persona(pid)
            if not persona:
                print(f"✗ Persona '{pid}' not found")
                return False

        print(f"✓ All {len(personas)} personas loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Persona loading failed: {e}")
        return False


def test_domains():
    """Test domain loading."""
    print("\nTesting domain loading...")
    try:
        from council_ai import get_domain, list_domains

        domains = list_domains()
        if len(domains) < 12:
            print(f"✗ Expected at least 12 domains, got {len(domains)}")
            return False

        # Test getting specific domains
        required_domains = ["coding", "business", "startup", "product", "leadership",
                          "creative", "writing", "career", "decisions", "devops", "data", "general"]
        for did in required_domains:
            domain = get_domain(did)
            if not domain:
                print(f"✗ Domain '{did}' not found")
                return False

        print(f"✓ All {len(domains)} domains loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Domain loading failed: {e}")
        return False


def test_council_creation():
    """Test council creation."""
    print("\nTesting council creation...")
    try:
        from council_ai import Council

        # Create empty council
        council1 = Council(api_key="test-key")
        if len(council1.list_members()) != 0:
            print("✗ Empty council should have no members")
            return False

        # Create domain-based council
        council2 = Council.for_domain("business", api_key="test-key")
        if len(council2.list_members()) == 0:
            print("✗ Business council should have members")
            return False

        print("✓ Council creation successful")
        return True
    except Exception as e:
        print(f"✗ Council creation failed: {e}")
        return False


def test_cli():
    """Test CLI availability."""
    print("\nTesting CLI...")
    try:
        import subprocess
        result = subprocess.run(
            ["council", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ CLI is available and working")
            return True
        else:
            print(f"✗ CLI returned error code {result.returncode}")
            return False
    except FileNotFoundError:
        print("✗ CLI command 'council' not found in PATH")
        return False
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("  Council AI - Package Validation")
    print("=" * 60)

    tests = [
        test_imports,
        test_personas,
        test_domains,
        test_council_creation,
        test_cli,
    ]

    results = []
    for test in tests:
        results.append(test())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All {total} validation tests passed!")
        print("\nCouncil AI is properly installed and ready to use.")
        print("\nNext steps:")
        print("  1. Run: python examples/quickstart.py")
        print("  2. Set API key: export ANTHROPIC_API_KEY='your-key'")
        print("  3. Try: python examples/simple_example.py")
        print("  4. Explore: council --help")
        return 0
    else:
        print(f"✗ {total - passed} of {total} tests failed")
        print("\nPlease check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
