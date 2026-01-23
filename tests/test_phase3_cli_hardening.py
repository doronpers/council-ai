"""
Tests for Phase 3 CLI Hardening improvements
"""

import pytest

from council_ai.cli.config_validation import ConfigValidator, validate_configuration
from council_ai.cli.error_handling import (
    APIKeyError,
    ProviderError,
    StorageError,
    StreamingError,
    ValidationError,
    suggest_command_fixes,
)
from council_ai.cli.help_system import COMMAND_DOCS, suggest_command


class TestErrorHandling:
    """Test enhanced error handling utilities"""

    def test_api_key_error_message(self):
        """Test API key error displays helpful message"""
        error = APIKeyError("openai", "Not configured")
        assert "No API key found for openai" in error.message
        assert "council config set openai_key" in error.suggestion

    def test_provider_error_message(self):
        """Test provider error suggests diagnostics"""
        error = ProviderError("openai", "Connection timeout")
        assert "council doctor" in error.suggestion

    def test_streaming_error_suggests_fallback(self):
        """Test streaming error suggests fallback options"""
        error = StreamingError("Connection lost")
        assert "non-streaming mode" in error.suggestion

    def test_storage_error_suggests_fixes(self):
        """Test storage error suggests troubleshooting"""
        error = StorageError("save consultation", "Disk full")
        assert "disk space" in error.suggestion

    def test_command_fixes_suggests_corrections(self):
        """Test command fix suggestions"""
        suggestion = suggest_command_fixes("consult", "typo")
        assert suggestion  # Should have a suggestion


class TestConfigValidation:
    """Test configuration validation"""

    def test_validate_valid_provider(self):
        """Test validation of valid provider"""
        error = ConfigValidator.validate_value("api.provider", "openai")
        assert error is None

    def test_validate_invalid_provider(self):
        """Test validation catches invalid provider"""
        error = ConfigValidator.validate_value("api.provider", "invalid_provider")
        assert error is not None
        assert "Invalid provider" in error

    def test_validate_valid_mode(self):
        """Test validation of valid consultation mode"""
        error = ConfigValidator.validate_value("default_mode", "synthesis")
        assert error is None

    def test_validate_invalid_mode(self):
        """Test validation catches invalid mode"""
        error = ConfigValidator.validate_value("default_mode", "invalid_mode")
        assert error is not None

    def test_validate_temperature_in_range(self):
        """Test temperature validation accepts valid range"""
        assert ConfigValidator.validate_value("temperature", 0.7) is None
        assert ConfigValidator.validate_value("temperature", 0.0) is None
        assert ConfigValidator.validate_value("temperature", 2.0) is None

    def test_validate_temperature_out_of_range(self):
        """Test temperature validation rejects out-of-range"""
        error = ConfigValidator.validate_value("temperature", 3.0)
        assert error is not None
        assert "between 0 and 2" in error

    def test_validate_api_key_placeholder(self):
        """Test API key validation rejects placeholders"""
        error = ConfigValidator.validate_value("api.api_key", "your-api-key-here")
        assert error is not None
        assert "placeholder" in error.lower()

    def test_validate_full_configuration(self):
        """Test validation of complete config"""
        config = {
            "api.provider": "openai",
            "api.api_key": "sk-1234567890abcdefghij",  # pragma: allowlist secret
            "default_mode": "synthesis",
            "temperature": 0.8,
            "max_tokens_per_response": 1000,
        }
        is_valid, errors = validate_configuration(config)
        assert is_valid
        assert len(errors) == 0

    def test_validate_configuration_with_errors(self):
        """Test validation detects multiple errors"""
        config = {
            "api.provider": "invalid",
            "default_mode": "invalid",
            "temperature": 5.0,
        }
        is_valid, errors = validate_configuration(config)
        assert not is_valid
        assert len(errors) > 0


class TestHelpSystem:
    """Test help and documentation system"""

    def test_command_docs_exist(self):
        """Test that documentation exists for main commands"""
        expected_commands = ["consult", "interactive", "tui", "history", "doctor", "config"]
        for command in expected_commands:
            assert command in COMMAND_DOCS
            doc = COMMAND_DOCS[command]
            assert "description" in doc
            assert "usage" in doc
            assert "examples" in doc

    def test_suggest_command_works(self):
        """Test command suggestion based on keywords"""
        # Test various query patterns
        assert suggest_command("ask a question") == "consult"
        assert suggest_command("start a chat") == "interactive"
        assert suggest_command("view history") == "history"
        assert suggest_command("diagnose problem") == "doctor"

    def test_command_docs_have_examples(self):
        """Test all commands have at least one example"""
        for command, doc in COMMAND_DOCS.items():
            assert "examples" in doc
            assert len(doc["examples"]) > 0


class TestIntegration:
    """Integration tests for CLI hardening"""

    def test_error_chain_api_key_missing(self):
        """Test error chain when API key is missing"""
        error = APIKeyError("anthropic")
        assert "anthropic" in error.message.lower()
        assert error.suggestion is not None
        assert "council config set" in error.suggestion

    def test_error_chain_provider_connectivity(self):
        """Test error chain for provider connectivity"""
        error = ProviderError("google", "DNS resolution failed")
        assert error.message
        assert error.suggestion
        assert "check internet" in error.suggestion.lower() or "doctor" in error.suggestion

    def test_validation_error_chain(self):
        """Test validation error with suggestion"""
        error = ValidationError("query", "too short", "Queries must be at least 5 characters")
        assert error.message
        assert error.suggestion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
