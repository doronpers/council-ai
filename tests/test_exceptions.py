"""
Tests for custom exceptions.
"""

import pytest
from council_ai.core.exceptions import (
    CouncilError,
    APIKeyError,
    RateLimitError,
    TimeoutError,
    TransientAPIError,
    PersonaNotFoundError,
    ConsultationError,
    ProviderUnavailableError,
)


class TestExceptions:
    """Test custom exception types."""

    def test_base_exception(self):
        """Test that all exceptions inherit from CouncilError."""
        assert issubclass(APIKeyError, CouncilError)
        assert issubclass(RateLimitError, CouncilError)
        assert issubclass(TimeoutError, CouncilError)

    def test_api_key_error(self):
        """Test APIKeyError."""
        error = APIKeyError("anthropic")
        assert error.provider == "anthropic"
        assert "anthropic" in str(error)
        assert "api key" in str(error).lower()

        custom_error = APIKeyError("openai", "Custom message")
        assert "Custom message" in str(custom_error)

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("openai")
        assert error.provider == "openai"
        assert "rate limit" in str(error).lower()

        error_with_retry = RateLimitError("openai", retry_after=60)
        assert error_with_retry.retry_after == 60
        assert "60" in str(error_with_retry)

    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("member_response", 120.0)
        assert error.operation == "member_response"
        assert error.timeout == 120.0
        assert "timed out" in str(error).lower()
        assert "120" in str(error)

    def test_transient_api_error(self):
        """Test TransientAPIError."""
        original = Exception("Connection failed")
        error = TransientAPIError("gemini", original)
        assert error.provider == "gemini"
        assert error.original_error is original
        assert "Connection failed" in str(error)

    def test_persona_not_found_error(self):
        """Test PersonaNotFoundError."""
        error = PersonaNotFoundError("kahneman")
        assert error.persona_id == "kahneman"
        assert "kahneman" in str(error)
        assert "not found" in str(error).lower()

    def test_consultation_error(self):
        """Test ConsultationError."""
        partial = [{"response": "partial"}]
        error = ConsultationError("Failed mid-consultation", partial_responses=partial)
        assert error.partial_responses == partial
        assert "Failed mid-consultation" in str(error)

    def test_provider_unavailable_error(self):
        """Test ProviderUnavailableError."""
        providers = ["anthropic", "openai"]
        error = ProviderUnavailableError(attempted_providers=providers)
        assert error.attempted_providers == providers
        assert "anthropic" in str(error)
        assert "openai" in str(error)
