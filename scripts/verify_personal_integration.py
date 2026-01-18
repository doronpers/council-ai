#!/usr/bin/env python3
"""
Verification script for council-ai-personal integration.

This script verifies that personal integration is working correctly by:
- Checking if council-ai-personal is detected
- Verifying integration status
- Testing config loading
- Verifying personas are accessible
- Testing domain loading
"""

import sys
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from council_ai.core.config import ConfigManager  # noqa: E402
from council_ai.core.persona import PersonaManager  # noqa: E402
from council_ai.core.personal_integration import (  # noqa: E402
    detect_personal_repo,
    is_personal_configured,
    verify_personal_integration,
)
from council_ai.domains import get_domain, list_domains  # noqa: E402


def print_header(text: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f" {text}")
    print(f"{'=' * 60}")


def print_result(check: str, passed: bool, details: str = ""):
    """Print a verification result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {check}")
    if details:
        print(f"      {details}")


def main():
    """Run verification checks."""
    print_header("Council AI Personal Integration Verification")

    all_passed = True

    # Check 1: Repository Detection
    print_header("1. Repository Detection")
    repo_path = detect_personal_repo()
    if repo_path:
        print_result("Repository detected", True, f"Found at: {repo_path}")
    else:
        print_result("Repository detected", False, "Not found in standard locations")
        all_passed = False
        print("\n  Note: This is optional. Integration will work without it.")
        return 0  # Not a failure, just not configured

    # Check 2: Integration Status
    print_header("2. Integration Status")
    configured = is_personal_configured()
    print_result("Integration configured", configured, "Configs copied to ~/.config/council-ai/")
    if not configured:
        all_passed = False
        print("\n  Run 'council personal integrate' to configure integration.")

    # Check 3: Verification
    print_header("3. Detailed Verification")
    verification = verify_personal_integration()

    detected = verification.get("detected", False)
    print_result("Repository detected", detected, verification.get("repo_path", "N/A"))

    configured = verification.get("configured", False)
    print_result(
        "Configuration status", configured, "Integrated" if configured else "Not integrated"
    )

    configs_loaded = verification.get("configs_loaded", False)
    print_result("Configs loaded", configs_loaded, "Config file accessible")

    personas_available = verification.get("personas_available", False)
    persona_count = verification.get("persona_count", 0)
    print_result(
        "Personas available",
        personas_available,
        f"{persona_count} personas found" if personas_available else "No personas found",
    )

    issues = verification.get("issues", [])
    if issues:
        print("\n  Issues found:")
        for issue in issues:
            print(f"    ⚠️  {issue}")
        all_passed = False

    # Check 4: Config Loading
    print_header("4. Config Loading")
    try:
        config_manager = ConfigManager()
        config = config_manager.config
        print_result("Config loaded", True, f"Config path: {config_manager.path}")
        print(f"      Default domain: {config.default_domain}")
        print(f"      Default mode: {config.default_mode}")
    except Exception as e:
        print_result("Config loaded", False, f"Error: {e}")
        all_passed = False

    # Check 5: Persona Loading
    print_header("5. Persona Loading")
    try:
        persona_manager = PersonaManager()
        all_personas = persona_manager.list()
        print_result("Personas loaded", True, f"Total personas: {len(all_personas)}")

        # Check for personal personas (if configured)
        if configured:
            # Try to identify personal personas (they might have specific IDs or categories)
            personal_personas = [p for p in all_personas if p.category.value == "custom"]
            if personal_personas:
                print(f"      Custom/personal personas: {len(personal_personas)}")
                for persona in personal_personas[:5]:  # Show first 5
                    print(f"        • {persona.id}: {persona.name}")
    except Exception as e:
        print_result("Personas loaded", False, f"Error: {e}")
        all_passed = False

    # Check 6: Domain Loading
    print_header("6. Domain Loading")
    try:
        all_domains = list_domains()
        print_result("Domains loaded", True, f"Total domains: {len(all_domains)}")

        # Try to load a domain
        test_domain = get_domain("general")
        print(f"      Test domain 'general': {test_domain.name}")
        print(f"      Default personas: {', '.join(test_domain.default_personas[:3])}...")
    except Exception as e:
        print_result("Domains loaded", False, f"Error: {e}")
        all_passed = False

    # Summary
    print_header("Verification Summary")
    if all_passed:
        print("✅ All checks passed! Personal integration is working correctly.")
        return 0
    else:
        print("❌ Some checks failed. Review the issues above.")
        print("\n  Next steps:")
        print("    • Run 'council personal status' for detailed status")
        print("    • Run 'council personal integrate' to set up integration")
        print("    • Run 'council personal verify' for CLI verification")
        return 1


if __name__ == "__main__":
    sys.exit(main())
