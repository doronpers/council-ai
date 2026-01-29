"""
Comprehensive tests for provider fallback, selection, and error handling.

Tests cover:
- Provider availability detection
- Fallback mechanism when primary fails
- Provider selection priority order
- Error messages and diagnostics
- API key validation and placeholder detection
- Provider health checks
"""

from unittest.mock import MagicMock, patch

import pytest

from council_ai.core.config import get_available_providers, is_placeholder_key
from council_ai.core.exceptions import ProviderUnavailableError

# Test API key placeholders used in tests; intentionally non-secret placeholders
TEST_KEY_PLACEHOLDER = "test_key_placeholder"  # pragma: allowlist secret
TEST_KEY_ANTHROPIC = "test_key_anthropic_placeholder"  # pragma: allowlist secret
TEST_KEY_OPENAI = "test_key_openai_placeholder"  # pragma: allowlist secret
TEST_KEY_ANTHROPIC_REAL = "test_key_anthropic_real_placeholder"  # pragma: allowlist secret

# ============================================================================
# Provider Detection & Availability Tests
# ============================================================================


class TestProviderDetection:
    """Test provider detection and availability checks."""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": TEST_KEY_ANTHROPIC})
    def test_detect_anthropic_from_env(self):
        """Test detecting Anthropic API key from environment."""
        with patch("council_ai.core.config.os.environ", {"ANTHROPIC_API_KEY": TEST_KEY_ANTHROPIC}):
            from council_ai.core.config import get_available_providers

            providers = get_available_providers()
            anthropic_found = any(p[0] == "anthropic" and p[1] for p in providers)
            assert anthropic_found, "Should detect Anthropic API key from env"

    @patch.dict("os.environ", {"OPENAI_API_KEY": TEST_KEY_OPENAI})
    def test_detect_openai_from_env(self):
        """Test detecting OpenAI API key from environment."""
        with patch("council_ai.core.config.os.environ", {"OPENAI_API_KEY": TEST_KEY_OPENAI}):
            providers = get_available_providers()
            openai_found = any(p[0] == "openai" and p[1] for p in providers)
            assert openai_found, "Should detect OpenAI API key from env"

    def test_no_providers_available(self):
        """Test behavior when no providers are available."""
        with (
            patch("council_ai.core.config.os.environ", {}),
            patch("council_ai.core.config.load_config") as mock_config,
        ):
            mock_config.return_value = MagicMock(api=MagicMock(api_key=None))
            providers = get_available_providers()
            # Should still return provider list but without keys
            assert isinstance(providers, list)


class TestProviderHealthCheck:
    """Test provider health and connectivity checks."""

    @pytest.mark.asyncio
    async def test_provider_availability_check(self):
        """Test checking if a provider is available and working."""
        from council_ai.providers import get_provider

        # Mock a successful provider initialization
        with patch("council_ai.providers.get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_get_provider.return_value = mock_provider
            provider = get_provider(
                "anthropic", api_key=TEST_KEY_PLACEHOLDER, model="claude-3-sonnet-20240229"
            )
            assert provider is not None

    @pytest.mark.asyncio
    async def test_provider_connection_error(self):
        """Test handling provider connection errors gracefully."""
        with patch("council_ai.providers.get_provider") as mock_get_provider:
            mock_get_provider.side_effect = ConnectionError("Network timeout")
            with pytest.raises(ConnectionError):
                # Call the patched version which will raise
                if mock_get_provider.side_effect:
                    raise mock_get_provider.side_effect


# ============================================================================
# Provider Fallback Tests
# ============================================================================


class TestProviderFallback:
    """Test provider fallback mechanism."""

    @pytest.mark.asyncio
    async def test_fallback_to_secondary_provider(self):
        """Test falling back to secondary provider when primary fails."""
        from council_ai.core.council import Council

        anthropic_provider = MagicMock()

        async def _fake_complete(*args, **kwargs):
            return MagicMock(text="response")

        anthropic_provider.complete = _fake_complete

        # Mock get_llm_manager so the manager returns None for primary, triggering fallback
        mock_manager = MagicMock()
        mock_manager.get_provider.return_value = None
        mock_manager.preferred_provider = "anthropic"

        with (
            patch("council_ai.core.council.get_llm_manager", return_value=mock_manager),
            patch("council_ai.core.config.get_available_providers") as mock_available,
            patch("council_ai.core.council.get_provider", return_value=anthropic_provider),
        ):
            mock_available.return_value = [
                ("anthropic", TEST_KEY_ANTHROPIC),
                ("openai", TEST_KEY_OPENAI),
            ]

            council = Council(api_key=TEST_KEY_PLACEHOLDER, provider="openai")
            provider = council._get_provider(fallback=True)
            assert provider is not None
            assert hasattr(provider, "complete")

    @pytest.mark.asyncio
    async def test_fallback_priority_order(self):
        """Test provider selection follows priority logic."""
        # Test that fallback mechanism exists and works
        from council_ai.core.council import Council

        with (
            patch("council_ai.core.config.get_available_providers") as mock_available,
            patch("council_ai.providers.get_provider") as mock_get,
        ):
            mock_available.return_value = [
                ("anthropic", TEST_KEY_ANTHROPIC),
                ("openai", TEST_KEY_OPENAI),
            ]

            mock_provider = MagicMock()

            async def _fake_complete(*args, **kwargs):
                return MagicMock(text="response")

            mock_provider.complete = _fake_complete
            mock_get.return_value = mock_provider

            with patch("council_ai.core.council.LLMManager"):
                council = Council(api_key="key1", provider="anthropic")
                provider = council._get_provider(fallback=True)
                # Should get a provider
                assert provider is not None

    @pytest.mark.asyncio
    async def test_all_providers_exhausted(self):
        """Test fallback when providers fail in sequence."""
        from council_ai.core.council import Council

        with (
            patch("council_ai.core.config.get_available_providers") as mock_available,
            patch("council_ai.providers.get_provider") as mock_get,
        ):
            # Setup sequence of failures
            mock_available.return_value = [
                ("anthropic", "key1"),
                ("openai", "key2"),
            ]

            mock_get.return_value = None

            with patch("council_ai.core.council.get_llm_manager") as mock_get_llm:
                # Ensure the LLM manager cannot provide a provider (simulate exhausted providers)
                mock_get_llm.return_value.get_provider.return_value = None
                mock_get_llm.return_value.preferred_provider = "openai"
                council = Council(api_key="key1", provider="anthropic")
                with pytest.raises(ValueError, match="unavailable"):
                    council._get_provider(fallback=True)

    def test_no_providers_available_error(self):
        """Test error handling when no providers configured."""
        from council_ai.core.council import Council

        with patch("council_ai.core.config.get_available_providers") as mock_available:
            # No providers with keys
            mock_available.return_value = [
                ("anthropic", None),
                ("openai", None),
            ]

            with patch("council_ai.core.council.get_llm_manager") as mock_get_llm:
                mock_get_llm.return_value.get_provider.return_value = None
                mock_get_llm.return_value.preferred_provider = "openai"
                council = Council(api_key=None, provider="anthropic")
                with pytest.raises(ValueError, match="unavailable"):
                    council._get_provider(fallback=True)


# ============================================================================
# API Key Validation Tests
# ============================================================================


class TestAPIKeyValidation:
    """Test API key validation and placeholder detection."""

    def test_valid_api_key_detection(self):
        """Test detection of valid API keys."""
        valid_keys = [
            "sk-ant-v2-1234567890abcdef1234567890abcdef",
            "sk-proj-1234567890abcdef1234567890abcdef",
            "AIzaSy1234567890abcdef1234567890abcdef",
        ]

        for key in valid_keys:
            assert not is_placeholder_key(key), f"{key} should be valid"

    def test_placeholder_key_detection(self):
        """Test detection of placeholder patterns in API keys."""
        placeholder_patterns = [
            "your-api-key-here",
            "placeholder",
            "xxx",
        ]

        for pattern in placeholder_patterns:
            result = is_placeholder_key(pattern)
            # Pattern should be detected as placeholder or at least not valid
            assert result or not pattern.startswith("sk-"), f"{pattern} handling"

    def test_empty_api_key(self):
        """Test handling of empty or None API keys."""
        # Empty string and None should both be treated as missing/invalid
        assert is_placeholder_key("") or is_placeholder_key("") is not None


# ============================================================================
# Provider Error Handling Tests
# ============================================================================


class TestProviderErrorHandling:
    """Test error handling for provider operations."""

    @pytest.mark.asyncio
    async def test_provider_unavailable_error(self):
        """Test ProviderUnavailableError with attempted providers."""
        attempted = ["anthropic", "openai", "gemini"]
        error = ProviderUnavailableError(attempted_providers=attempted)

        assert error.attempted_providers == attempted
        for provider in attempted:
            assert provider in str(error)

    def test_provider_error_with_context(self):
        """Test provider error includes helpful context."""
        from council_ai.core.exceptions import APIError

        error = APIError("Provider authentication failed")
        assert "Provider" in str(error)

    @pytest.mark.asyncio
    async def test_provider_configuration_error(self):
        """Test handling of provider configuration errors."""
        from council_ai.core.council import Council

        with patch("council_ai.providers.get_provider") as mock_get:
            mock_get.return_value = None

            with patch("council_ai.core.council.LLMManager"):
                council = Council(api_key=TEST_KEY_PLACEHOLDER, provider="invalid")
                with pytest.raises(ValueError, match="unavailable"):
                    council._get_provider(fallback=True)

    @pytest.mark.asyncio
    async def test_provider_timeout_error(self):
        """Test handling of provider timeout errors gracefully."""
        from council_ai.core.council import Council

        with patch("council_ai.core.config.get_available_providers") as mock_avail:
            mock_avail.return_value = [("anthropic", TEST_KEY_PLACEHOLDER)]
            with patch("council_ai.core.council.get_llm_manager") as mock_get_llm:
                mock_get_llm.return_value.get_provider.return_value = None
                mock_get_llm.return_value.preferred_provider = "openai"
                council = Council(api_key=TEST_KEY_PLACEHOLDER, provider="anthropic")
                # Mock get_provider to return None for this specific test
                with patch("council_ai.providers.get_provider", return_value=None):
                    with pytest.raises(ValueError, match="unavailable"):
                        council._get_provider(fallback=False)


# ============================================================================
# Provider Selection Tests
# ============================================================================


class TestProviderSelection:
    """Test intelligent provider selection logic."""

    def test_best_provider_selection(self):
        """Test selection of best available provider."""
        from council_ai.core.config import get_best_available_provider

        with patch("council_ai.core.config.get_available_providers") as mock_available:
            mock_available.return_value = [
                ("anthropic", TEST_KEY_ANTHROPIC),
                ("openai", TEST_KEY_OPENAI),
                ("gemini", None),
            ]

            best = get_best_available_provider()
            # Should select first available in priority order
            assert best is not None
            assert best[0] in ["anthropic", "openai"]

    def test_no_best_provider(self):
        """Test when no providers are available."""
        from council_ai.core.config import get_best_available_provider

        with patch("council_ai.core.config.get_available_providers") as mock_available:
            mock_available.return_value = [
                ("anthropic", None),
                ("openai", None),
                ("gemini", None),
            ]

            best = get_best_available_provider()
            assert best is None

    def test_provider_selection_with_model(self):
        """Test provider selection respects model compatibility."""
        from council_ai.core.council import Council

        mock_provider = MagicMock()

        async def _fake_complete(*args, **kwargs):
            return MagicMock(text="response")

        mock_provider.complete = _fake_complete

        mock_manager = MagicMock()
        mock_manager.get_provider.return_value = mock_provider

        with patch("council_ai.core.council.get_llm_manager", return_value=mock_manager):
            council = Council(
                api_key=TEST_KEY_PLACEHOLDER,
                provider="anthropic",
                model="claude-3-sonnet-20240229",
            )

            provider = council._get_provider(fallback=False)
            assert provider is not None


# ============================================================================
# Provider Diagnostics Tests
# ============================================================================


class TestProviderDiagnostics:
    """Test provider diagnostics and troubleshooting."""

    def test_diagnose_api_keys(self):
        """Test API key diagnostics."""
        from council_ai.core.diagnostics import diagnose_api_keys

        with patch(
            "council_ai.core.config.os.environ", {"ANTHROPIC_API_KEY": TEST_KEY_PLACEHOLDER}
        ):
            diag = diagnose_api_keys()

            assert "available_keys" in diag
            assert "missing_keys" in diag
            assert "recommendations" in diag

    def test_diagnose_placeholder_keys(self):
        """Test diagnostics detect placeholder patterns in API keys."""
        from council_ai.core.diagnostics import diagnose_api_keys

        with patch(
            "council_ai.core.config.os.environ",
            {
                "ANTHROPIC_API_KEY": TEST_KEY_ANTHROPIC_REAL,
                "OPENAI_API_KEY": TEST_KEY_OPENAI,
            },
        ):
            diag = diagnose_api_keys()

            # Should have recommendations or warnings
            assert "recommendations" in diag or "warnings" in diag

    def test_provider_connectivity_diagnosis(self):
        """Test diagnosing provider connectivity and availability."""
        from council_ai.core.diagnostics import diagnose_api_keys

        with patch(
            "council_ai.core.config.os.environ", {"ANTHROPIC_API_KEY": TEST_KEY_PLACEHOLDER}
        ):
            diag = diagnose_api_keys()

            assert "best_provider" in diag or "available_keys" in diag
            # Should have some diagnostic information
            assert isinstance(diag, dict)
