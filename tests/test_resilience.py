"""
Tests for providers/resilience.py — RateLimiter, ResilienceConfig, ResilientProvider.

This module previously had only 30% test coverage.
"""

import asyncio
import time

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from council_ai.providers.resilience import (
    DEFAULT_CONFIGS,
    RateLimiter,
    ResilienceConfig,
    ResilientProvider,
    get_resilience_config,
    resilient_provider,
)


class TestResilienceConfig:
    """Tests for ResilienceConfig defaults and construction."""

    def test_default_values(self):
        config = ResilienceConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_factor == 2.0
        assert config.jitter is True
        assert config.rate_limit_rpm == 60.0
        assert config.timeout == 120.0
        assert config.retry_on_429 is True
        assert config.retry_on_500 is True
        assert config.retry_on_502 is True
        assert config.retry_on_503 is True
        assert config.retry_on_504 is True

    def test_custom_values(self):
        config = ResilienceConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            backoff_factor=3.0,
            jitter=False,
            rate_limit_rpm=30.0,
            timeout=60.0,
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.jitter is False


class TestRateLimiter:
    """Tests for the token bucket RateLimiter."""

    @pytest.mark.asyncio
    async def test_acquire_succeeds_with_available_tokens(self):
        limiter = RateLimiter(requests_per_minute=60.0, burst_size=10)
        result = await limiter.acquire()
        assert result is True

    @pytest.mark.asyncio
    async def test_acquire_depletes_tokens(self):
        limiter = RateLimiter(requests_per_minute=60.0, burst_size=2)
        assert await limiter.acquire() is True
        assert await limiter.acquire() is True
        # Third should fail (no tokens left, not enough time elapsed)
        assert await limiter.acquire() is False

    @pytest.mark.asyncio
    async def test_tokens_replenish_over_time(self):
        limiter = RateLimiter(requests_per_minute=6000.0, burst_size=1)
        assert await limiter.acquire() is True
        assert await limiter.acquire() is False
        # Wait for token replenishment (6000 RPM = 100/sec)
        await asyncio.sleep(0.02)
        assert await limiter.acquire() is True

    @pytest.mark.asyncio
    async def test_wait_for_token_succeeds(self):
        limiter = RateLimiter(requests_per_minute=6000.0, burst_size=1)
        await limiter.acquire()  # Deplete
        result = await limiter.wait_for_token(timeout=1.0)
        assert result is True

    @pytest.mark.asyncio
    async def test_wait_for_token_timeout(self):
        limiter = RateLimiter(requests_per_minute=0.1, burst_size=1)
        await limiter.acquire()  # Deplete
        result = await limiter.wait_for_token(timeout=0.2)
        assert result is False


class TestResilientProvider:
    """Tests for ResilientProvider retry and resilience logic."""

    def _make_provider(self, config=None):
        mock_provider = MagicMock()
        return ResilientProvider(
            provider=mock_provider,
            config=config or ResilienceConfig(max_retries=2, base_delay=0.01, jitter=False),
            provider_name="test",
        )

    def test_initial_stats(self):
        rp = self._make_provider()
        stats = rp.get_stats()
        assert stats["requests"] == 0
        assert stats["successes"] == 0
        assert stats["failures"] == 0
        assert stats["retries"] == 0

    def test_reset_stats(self):
        rp = self._make_provider()
        rp._stats["requests"] = 10
        rp._stats["failures"] = 3
        rp.reset_stats()
        assert rp._stats["requests"] == 0
        assert rp._stats["failures"] == 0

    def test_should_retry_on_connection_error(self):
        rp = self._make_provider()
        error = Exception("connection refused")
        assert rp._should_retry(error, attempt=0) is True

    def test_should_retry_on_429(self):
        rp = self._make_provider()
        error = Exception("HTTP 429 Too Many Requests")
        assert rp._should_retry(error, attempt=0) is True
        assert rp._stats["rate_limits"] == 1

    def test_should_retry_on_500(self):
        rp = self._make_provider()
        error = Exception("HTTP 500 Internal Server Error")
        assert rp._should_retry(error, attempt=0) is True

    def test_should_retry_on_rate_limit_text(self):
        rp = self._make_provider()
        error = Exception("rate limit exceeded")
        assert rp._should_retry(error, attempt=0) is True

    def test_should_not_retry_on_auth_error(self):
        rp = self._make_provider()
        error = Exception("Invalid API key")
        assert rp._should_retry(error, attempt=0) is False

    def test_should_not_retry_when_max_attempts_reached(self):
        rp = self._make_provider()
        error = Exception("connection timeout")
        assert rp._should_retry(error, attempt=2) is False  # max_retries=2

    def test_calculate_delay_exponential_backoff(self):
        config = ResilienceConfig(base_delay=1.0, backoff_factor=2.0, jitter=False, max_delay=60.0)
        rp = self._make_provider(config)
        assert rp._calculate_delay(0) == 1.0
        assert rp._calculate_delay(1) == 2.0
        assert rp._calculate_delay(2) == 4.0

    def test_calculate_delay_capped_at_max(self):
        config = ResilienceConfig(base_delay=1.0, backoff_factor=10.0, jitter=False, max_delay=5.0)
        rp = self._make_provider(config)
        assert rp._calculate_delay(5) == 5.0

    def test_calculate_delay_with_jitter(self):
        config = ResilienceConfig(base_delay=1.0, backoff_factor=2.0, jitter=True)
        rp = self._make_provider(config)
        delay = rp._calculate_delay(0)
        # With jitter, delay should be between 0.5 and 1.0
        assert 0.5 <= delay <= 1.0

    @pytest.mark.asyncio
    async def test_execute_with_retry_succeeds_first_try(self):
        rp = self._make_provider()
        mock_func = AsyncMock(return_value="success")
        result = await rp._execute_with_retry("test_op", mock_func)
        assert result == "success"
        assert rp._stats["successes"] == 1
        assert rp._stats["retries"] == 0

    @pytest.mark.asyncio
    async def test_execute_with_retry_retries_on_failure(self):
        config = ResilienceConfig(max_retries=2, base_delay=0.01, jitter=False)
        rp = self._make_provider(config)
        mock_func = AsyncMock(
            side_effect=[Exception("connection timeout"), "success"]
        )
        result = await rp._execute_with_retry("test_op", mock_func)
        assert result == "success"
        assert rp._stats["retries"] == 1

    @pytest.mark.asyncio
    async def test_execute_with_retry_raises_after_exhaustion(self):
        config = ResilienceConfig(max_retries=1, base_delay=0.01, jitter=False)
        rp = self._make_provider(config)
        mock_func = AsyncMock(side_effect=Exception("auth error"))
        with pytest.raises(Exception, match="auth error"):
            await rp._execute_with_retry("test_op", mock_func)

    @pytest.mark.asyncio
    async def test_complete_delegates_to_provider(self):
        rp = self._make_provider()
        mock_response = MagicMock(text="hello")
        rp.provider.complete = AsyncMock(return_value=mock_response)
        result = await rp.complete("system", "user")
        assert result.text == "hello"

    @pytest.mark.asyncio
    async def test_stream_complete_yields_chunks(self):
        rp = self._make_provider()

        async def mock_stream(*args, **kwargs):
            yield "chunk1"
            yield "chunk2"

        rp.provider.stream_complete = mock_stream

        chunks = []
        async for chunk in rp.stream_complete("system", "user"):
            chunks.append(chunk)
        assert chunks == ["chunk1", "chunk2"]

    @pytest.mark.asyncio
    async def test_stream_complete_raises_on_error(self):
        rp = self._make_provider()

        async def mock_stream(*args, **kwargs):
            yield "chunk1"
            raise Exception("stream failed")

        rp.provider.stream_complete = mock_stream

        with pytest.raises(Exception, match="stream failed"):
            async for _ in rp.stream_complete("system", "user"):
                pass


class TestResilientProviderContextManager:
    """Tests for the resilient_provider context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_yields_resilient_provider(self):
        mock_provider = MagicMock()
        async with resilient_provider(mock_provider, provider_name="test") as rp:
            assert isinstance(rp, ResilientProvider)
            assert rp.provider_name == "test"


class TestGetResilienceConfig:
    """Tests for get_resilience_config factory."""

    def test_known_provider_returns_specific_config(self):
        config = get_resilience_config("anthropic")
        assert config.rate_limit_rpm == 50.0

    def test_unknown_provider_returns_default(self):
        config = get_resilience_config("unknown_provider")
        assert config is DEFAULT_CONFIGS["default"]

    def test_all_default_configs_exist(self):
        for name in ["anthropic", "openai", "gemini", "http", "default"]:
            assert name in DEFAULT_CONFIGS
            assert isinstance(DEFAULT_CONFIGS[name], ResilienceConfig)
