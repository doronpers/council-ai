"""Tests for retry utilities."""

import asyncio
from unittest.mock import patch

import pytest

from council_ai.core.retry_utils import (
    RateLimitError,
    TransientAPIError,
    is_retryable_error,
    retry_async,
    retry_with_backoff,
)


class TestIsRetryableError:
    """Test error classification."""

    def test_retryable_error_instances(self):
        """Test that RetryableError subclasses are considered retryable."""
        assert is_retryable_error(RateLimitError("rate limit exceeded"))
        assert is_retryable_error(TransientAPIError("connection failed"))

    def test_rate_limit_patterns(self):
        """Test detection of rate limit errors from message."""
        assert is_retryable_error(Exception("Rate limit exceeded"))
        assert is_retryable_error(Exception("Too many requests"))
        assert is_retryable_error(Exception("429 error"))

    def test_network_error_patterns(self):
        """Test detection of network errors."""
        assert is_retryable_error(Exception("Connection timeout"))
        assert is_retryable_error(Exception("Network error"))
        assert is_retryable_error(Exception("Service unavailable 503"))

    def test_non_retryable_errors(self):
        """Test that non-retryable errors are not classified as retryable."""
        assert not is_retryable_error(Exception("Invalid API key"))
        assert not is_retryable_error(ValueError("Bad parameter"))


class TestRetryWithBackoff:
    """Test retry decorator."""

    @pytest.mark.asyncio
    async def test_successful_first_attempt(self):
        """Test that successful calls don't retry."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        async def succeeds_immediately():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await succeeds_immediately()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test retry on transient errors."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientAPIError("Temporary failure")
            return "success"

        result = await fails_twice()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that max retries is respected."""
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise RateLimitError("Rate limit")

        with pytest.raises(RateLimitError):
            await always_fails()

        assert call_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_non_retryable_error_no_retry(self):
        """Test that non-retryable errors don't trigger retries."""
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        async def fails_with_auth_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid API key")

        with pytest.raises(ValueError):
            await fails_with_auth_error()

        assert call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test that retry delays follow exponential backoff."""
        delays = []

        @retry_with_backoff(max_retries=3, base_delay=0.1, exponential_factor=2.0)
        async def track_delays():
            delays.append(asyncio.get_event_loop().time())
            raise TransientAPIError("fail")

        with pytest.raises(TransientAPIError):
            await track_delays()

        # Should have 4 attempts (1 initial + 3 retries)
        assert len(delays) == 4
        assert 0.08 < (delays[1] - delays[0]) < 0.15  # ~0.1s

    @pytest.mark.asyncio
    async def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        call_count = 0

        @retry_with_backoff(max_retries=10, base_delay=1.0, max_delay=2.0, exponential_factor=10.0)
        async def fails_many_times():
            nonlocal call_count
            call_count += 1
            if call_count < 5:
                raise TransientAPIError("fail")
            return "success"

        # Even with exponential_factor=10, delay should cap at 2.0
        with patch("asyncio.sleep") as mock_sleep:
            result = await fails_many_times()
            assert result == "success"

            # Check that no sleep was longer than max_delay
            for call_args in mock_sleep.call_args_list:
                delay = call_args[0][0]
                assert delay <= 2.0


class TestRetryAsync:
    """Test functional retry API."""

    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        """Test retry_async with successful call."""

        async def test_func(x, y):
            return x + y

        result = await retry_async(test_func, 2, 3, max_retries=3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_retry_async_with_failures(self):
        """Test retry_async with transient failures."""
        call_count = 0

        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientAPIError("fail")
            return "success"

        result = await retry_async(test_func, max_retries=3, base_delay=0.01)
        assert result == "success"
        assert call_count == 3


class TestSyncRetry:
    """Test retry with synchronous functions."""

    def test_sync_function_retry(self):
        """Test that decorator works with sync functions."""
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def sync_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientAPIError("fail")
            return "success"

        result = sync_func()
        assert result == "success"
        assert call_count == 3
