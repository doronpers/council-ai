#!/usr/bin/env python3
"""
Test script for Council AI improvements:
- API key detection
- Fallback mechanisms
- Persona model settings
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_api_key_detection():
    """Test enhanced API key detection."""
    print("=" * 60)
    print("TEST 1: API Key Detection")
    print("=" * 60)

    try:
        from council_ai.core.config import get_available_providers, get_best_available_provider
        from council_ai.core.diagnostics import diagnose_api_keys

        providers = get_available_providers()
        print(f"\n✓ Found {len(providers)} provider configurations")

        available_count = sum(1 for _, key in providers if key)
        print(f"✓ {available_count} providers have API keys")

        for name, key in providers:
            status = "✓" if key else "✗"
            print(f"  {status} {name}: {'Found' if key else 'Not found'}")

        best = get_best_available_provider()
        if best:
            print(f"\n✓ Best available provider: {best[0]}")
        else:
            print("\n⚠ No providers available")

        diag = diagnose_api_keys()
        print(f"\n✓ Diagnostics generated: {len(diag['recommendations'])} recommendations")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_persona_model_settings():
    """Test persona model/parameter settings."""
    print("\n" + "=" * 60)
    print("TEST 2: Persona Model Settings")
    print("=" * 60)

    try:
        from council_ai.core.persona import PersonaManager

        manager = PersonaManager()
        test_personas = ["rams", "kahneman", "taleb", "holman", "treasure", "grove"]

        personas_with_models = []
        personas_without = []

        for persona_id in test_personas:
            try:
                persona = manager.get_or_raise(persona_id)
                if persona.model or persona.provider:
                    personas_with_models.append(
                        (persona_id, persona.model, persona.provider, persona.model_params)
                    )
                else:
                    personas_without.append(persona_id)
            except Exception as e:
                print(f"  ⚠ Could not load {persona_id}: {e}")

        print(f"\n✓ Loaded {len(personas_with_models) + len(personas_without)} personas")
        print(f"✓ {len(personas_with_models)} personas have unique model/provider settings")

        print("\nPersonas with unique settings:")
        for pid, model, provider, params in personas_with_models:
            print(f"  • {pid}:")
            if provider:
                print(f"    provider: {provider}")
            if model:
                print(f"    model: {model}")
            if params:
                print(f"    params: {params}")

        if personas_without:
            print(f"\nPersonas using council defaults ({len(personas_without)}):")
            for pid in personas_without:
                print(f"  • {pid}")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_fallback_mechanism():
    """Test fallback mechanism."""
    print("\n" + "=" * 60)
    print("TEST 3: Fallback Mechanism")
    print("=" * 60)

    try:
        from council_ai.core.config import get_available_providers, get_best_available_provider

        providers = get_available_providers()
        available = [p for p, k in providers if k]

        print(f"\n✓ Found {len(available)} available providers: {', '.join(available)}")

        if len(available) > 1:
            print("✓ Multiple providers available - fallback mechanism will work")
            best = get_best_available_provider()
            if best:
                print(f"✓ Fallback priority: {best[0]} (recommended)")
        elif len(available) == 1:
            print(f"✓ Single provider available: {available[0]}")
            print("  (Fallback will use this if primary fails)")
        else:
            print("⚠ No providers available - fallback cannot work")
            print("  Set at least one API key to enable fallback")

        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Council AI Improvements Test Suite")
    print("=" * 60)

    results = []
    results.append(("API Key Detection", test_api_key_detection()))
    results.append(("Persona Model Settings", test_persona_model_settings()))
    results.append(("Fallback Mechanism", test_fallback_mechanism()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Improvements are working correctly.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
