"""Tests for custom exceptions."""

from council_ai.core.exceptions import (
    APIKeyError,
    ConsultationError,
    CouncilError,
    PersonaNotFoundError,
    ProviderUnavailableError,
    RateLimitError,
    TimeoutError,
    TransientAPIError,
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
        # Test default None value
        assert error.retry_after is None

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
        error = PersonaNotFoundError("DK")
        assert error.persona_id == "DK"
        assert "DK" in str(error)
        assert "not found" in str(error).lower()

    def test_consultation_error(self):
        """Test ConsultationError."""
        # Test with provided partial_responses
        partial = [{"response": "partial"}]
        error = ConsultationError("Failed mid-consultation", partial_responses=partial)
        assert error.partial_responses == partial
        assert "Failed mid-consultation" in str(error)

        # Test default None value (should be converted to empty list)
        error_default = ConsultationError("Failed without partial responses")
        assert error_default.partial_responses == []
        assert "Failed without partial responses" in str(error_default)

    def test_provider_unavailable_error(self):
        """Test ProviderUnavailableError."""
        # Test with provided attempted_providers
        providers = ["anthropic", "openai"]
        error = ProviderUnavailableError(attempted_providers=providers)
        assert error.attempted_providers == providers
        assert "anthropic" in str(error)
        assert "openai" in str(error)

        # Test default None value (should be converted to empty list)
        error_default = ProviderUnavailableError()
        assert error_default.attempted_providers == []
        assert "No available providers" in str(error_default)
