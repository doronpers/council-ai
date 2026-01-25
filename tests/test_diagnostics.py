"""Tests for diagnostic utilities."""

import os
from unittest.mock import MagicMock, patch

import pytest

# Import with alias to avoid pytest collecting it as a test
from council_ai.core.diagnostics import (
    check_provider_connectivity,
    check_tts_connectivity,
    diagnose_api_keys,
)
from council_ai.core.diagnostics import test_api_key as validate_api_key


class TestDiagnoseAPIKeys:
    """Tests for diagnose_api_keys function."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("council_ai.core.diagnostics.load_config")
    def test_diagnose_api_keys_no_keys(self, mock_load_config):
        """Test diagnostics when no API keys are present."""
        mock_load_config.side_effect = Exception("No config")
        result = diagnose_api_keys()

        assert "available_keys" in result
        assert "missing_keys" in result
        assert "recommendations" in result
        assert "provider_status" in result
        assert "best_provider" in result

        # Should have no available keys
        available = [p for p, has_key in result["available_keys"].items() if has_key]
        assert len(available) == 0

        # Should have recommendations
        assert len(result["recommendations"]) > 0
        assert "No API keys found" in result["recommendations"][0]

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789"})  # pragma: allowlist secret
    @patch("council_ai.core.diagnostics.load_config")
    @patch("council_ai.core.config.get_best_available_provider")
    def test_diagnose_api_keys_with_openai(self, mock_best, mock_load_config):
        """Test diagnostics with OpenAI key present."""
        mock_load_config.return_value.api.api_key = None
        mock_best.return_value = ("openai", True)

        result = diagnose_api_keys()

        assert result["available_keys"]["openai"] is True
        assert "openai" not in result["missing_keys"]
        assert result["provider_status"]["openai"]["has_key"] is True
        assert result["best_provider"] is not None

    @patch.dict(
        os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test123456789"}  # pragma: allowlist secret
    )
    @patch("council_ai.core.diagnostics.load_config")
    @patch("council_ai.core.config.get_best_available_provider")
    def test_diagnose_api_keys_with_anthropic(self, mock_best, mock_load_config):
        """Test diagnostics with Anthropic key present."""
        mock_load_config.return_value.api.api_key = None
        mock_best.return_value = ("anthropic", True)

        result = diagnose_api_keys()

        assert result["available_keys"]["anthropic"] is True
        assert result["provider_status"]["anthropic"]["has_key"] is True

    @patch.dict(os.environ, {"AI_GATEWAY_API_KEY": "test-key-123"})  # pragma: allowlist secret
    @patch("council_ai.core.diagnostics.load_config")
    def test_diagnose_api_keys_with_gateway(self, mock_load_config):
        """Test diagnostics with AI Gateway key."""
        mock_load_config.return_value.api.api_key = None

        result = diagnose_api_keys()

        assert result["available_keys"]["vercel"] is True
        assert result["provider_status"]["vercel"]["has_key"] is True

    @patch.dict(os.environ, {"COUNCIL_API_KEY": "test-key-123"})  # pragma: allowlist secret
    @patch("council_ai.core.diagnostics.load_config")
    def test_diagnose_api_keys_with_generic(self, mock_load_config):
        """Test diagnostics with generic Council API key."""
        mock_load_config.return_value.api.api_key = None

        result = diagnose_api_keys()

        assert result["available_keys"]["generic"] is True

    @patch.dict(os.environ, {"OPENAI_API_KEY": "placeholder-key"})  # pragma: allowlist secret
    @patch("council_ai.core.diagnostics.load_config")
    @patch("council_ai.core.config.is_placeholder_key", return_value=True)
    @patch("council_ai.core.config.get_api_key", return_value="placeholder-key")
    def test_diagnose_api_keys_placeholder_detection(
        self, mock_get_key, mock_is_placeholder, mock_load_config
    ):
        """Test that placeholder keys are detected."""
        mock_load_config.return_value.api.api_key = None

        result = diagnose_api_keys()

        # Placeholder keys should be in missing_keys
        assert "openai" in result["missing_keys"] or result["available_keys"]["openai"] is False
        status = result["provider_status"]["openai"]
        # Status should indicate placeholder or missing
        assert status["has_key"] is False or "placeholder" in status.get("note", "").lower()

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test-key"})  # pragma: allowlist secret
    @patch("council_ai.core.diagnostics.load_config")
    def test_diagnose_api_keys_elevenlabs(self, mock_load_config):
        """Test diagnostics includes ElevenLabs TTS key."""
        mock_load_config.return_value.api.api_key = None

        result = diagnose_api_keys()

        assert result["available_keys"].get("elevenlabs") is True
        assert "elevenlabs" in result["provider_status"]


class TestTestAPIKey:
    """Tests for validate_api_key function."""

    def test_validate_api_key_no_key(self):
        """Test API key validation when no key is provided."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value=None):
            success, message = validate_api_key("openai")
            assert success is False
            assert "No API key found" in message

    def test_validate_api_key_placeholder(self):
        """Test API key validation detects placeholder keys."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="placeholder-key"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=True):
                success, message = validate_api_key("openai")
                assert success is False
                assert "Placeholder" in message

    def test_validate_api_key_too_short(self):
        """Test API key validation rejects keys that are too short."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="short"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("openai")
                assert success is False
                assert "too short" in message

    def test_validate_api_key_openai_valid(self):
        """Test OpenAI API key format validation."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="sk-test123456789"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("openai")
                assert success is True
                assert "valid" in message.lower()

    def test_validate_api_key_openai_invalid_prefix(self):
        """Test OpenAI API key validation rejects wrong prefix."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="invalid-prefix-123"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("openai")
                assert success is False
                assert "should start with 'sk-'" in message

    def test_validate_api_key_anthropic_valid(self):
        """Test Anthropic API key format validation."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="sk-ant-test123456789"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("anthropic")
                assert success is True

    def test_validate_api_key_anthropic_invalid_prefix(self):
        """Test Anthropic API key validation rejects wrong prefix."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="sk-test123456789"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("anthropic")
                assert success is False
                assert "should start with 'sk-ant-'" in message

    def test_validate_api_key_gemini_valid(self):
        """Test Gemini API key validation."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="a" * 30):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("gemini")
                assert success is True

    def test_validate_api_key_gemini_too_short(self):
        """Test Gemini API key validation rejects short keys."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="short"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("gemini")
                assert success is False
                assert "too short" in message

    def test_validate_api_key_unknown_provider(self):
        """Test API key validation for unknown providers."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="test-key-123456789"):
            with patch("council_ai.core.diagnostics.is_placeholder_key", return_value=False):
                success, message = validate_api_key("unknown_provider")
                assert success is True
                assert "basic check" in message


class TestCheckProviderConnectivity:
    """Tests for check_provider_connectivity function."""

    @pytest.mark.asyncio
    async def test_check_provider_connectivity_no_key(self):
        """Test connectivity check when no API key is available."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value=None):
            success, message, latency = await check_provider_connectivity("openai")
            assert success is False
            assert "No API key" in message
            assert latency == 0.0

    @pytest.mark.asyncio
    async def test_check_provider_connectivity_lmstudio_not_available(self):
        """Test connectivity check for LM Studio when not available."""
        with patch("council_ai.core.config.is_lmstudio_available", return_value=False):
            success, message, latency = await check_provider_connectivity("lmstudio")
            assert success is False
            assert "not detected" in message.lower()

    @pytest.mark.asyncio
    async def test_check_provider_connectivity_success(self):
        """Test successful connectivity check."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Pong"

        # Make complete an async function
        async def async_complete(*args, **kwargs):
            return mock_response

        mock_provider.complete = async_complete

        with patch("council_ai.core.diagnostics.get_api_key", return_value="test-key"):
            with patch("council_ai.providers.get_provider", return_value=mock_provider):
                success, message, latency = await check_provider_connectivity("openai")
                assert success is True
                assert "Success" in message
                assert latency >= 0

    @pytest.mark.asyncio
    async def test_check_provider_connectivity_empty_response(self):
        """Test connectivity check with empty response."""
        mock_provider = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""

        # Make complete an async function
        async def async_complete(*args, **kwargs):
            return mock_response

        mock_provider.complete = async_complete

        with patch("council_ai.core.diagnostics.get_api_key", return_value="test-key"):
            with patch("council_ai.providers.get_provider", return_value=mock_provider):
                success, message, latency = await check_provider_connectivity("openai")
                assert success is False
                assert "Empty response" in message

    @pytest.mark.asyncio
    async def test_check_provider_connectivity_exception(self):
        """Test connectivity check handles exceptions."""
        with patch("council_ai.core.diagnostics.get_api_key", return_value="test-key"):
            with patch(
                "council_ai.providers.get_provider", side_effect=Exception("Connection error")
            ):
                success, message, latency = await check_provider_connectivity("openai")
                assert success is False
                assert "Connection error" in message
                assert latency == 0.0


class TestCheckTTSConnectivity:
    """Tests for check_tts_connectivity function."""

    @patch.dict(os.environ, {}, clear=True)
    def test_check_tts_connectivity_no_key(self):
        """Test TTS connectivity check when no key is present."""
        result = check_tts_connectivity()
        assert result == {}

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test-key"})  # pragma: allowlist secret
    @patch("requests.get")
    def test_check_tts_connectivity_elevenlabs_success(self, mock_get):
        """Test successful ElevenLabs connectivity check."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = check_tts_connectivity()
        assert "elevenlabs" in result
        assert result["elevenlabs"]["ok"] is True
        assert "Connected" in result["elevenlabs"]["msg"]

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test-key"})  # pragma: allowlist secret
    @patch("requests.get")
    def test_check_tts_connectivity_elevenlabs_failure(self, mock_get):
        """Test ElevenLabs connectivity check with HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = check_tts_connectivity()
        assert "elevenlabs" in result
        assert result["elevenlabs"]["ok"] is False
        assert "http 401" in result["elevenlabs"]["msg"]

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test-key"})  # pragma: allowlist secret
    @patch("requests.get")
    def test_check_tts_connectivity_elevenlabs_exception(self, mock_get):
        """Test ElevenLabs connectivity check handles exceptions."""
        mock_get.side_effect = Exception("Network error")

        result = check_tts_connectivity()
        assert "elevenlabs" in result
        assert result["elevenlabs"]["ok"] is False
        assert "Network error" in result["elevenlabs"]["msg"]
