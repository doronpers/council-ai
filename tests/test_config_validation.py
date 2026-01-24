"""Tests for configuration validation utilities."""

from council_ai.cli.config_validation import display_config_warning, validate_configuration

# Test API keys used in tests are test-only and marked for detect-secrets allowlist
TEST_API_KEY = "TEST_API_KEY_NOT_SECRET"  # pragma: allowlist secret
INVALID_SHORT_KEY = "short"  # pragma: allowlist secret


def test_validate_configuration_valid():
    cfg = {
        "api.provider": "openai",
        "api.api_key": TEST_API_KEY,
        "temperature": 0.7,
        "max_tokens_per_response": 200,
    }

    ok, errors = validate_configuration(cfg)
    assert ok is True
    assert errors == []


def test_validate_configuration_invalid_provider_and_key():
    cfg = {
        "api.provider": "unknown",
        "api.api_key": INVALID_SHORT_KEY,
    }

    ok, errors = validate_configuration(cfg)
    assert ok is False
    # both provider and api key validation errors should be reported
    assert any("Invalid provider" in e for e in errors)
    assert any("API key" in e for e in errors)


def test_display_config_warning_prints(capsys):
    display_config_warning("api.provider", "unknown", "Invalid provider")
    captured = capsys.readouterr()
    assert "Configuration Warning" in captured.out or "Invalid provider" in captured.out
