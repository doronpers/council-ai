"""Resilience layer for LLM providers with retry logic, rate limiting, and error handling."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Optional

from shared_ai_utils.llm import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, requests_per_minute: float = 60.0, burst_size: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens = float(burst_size)
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire a token. Returns True if successful, False if rate limited."""
        async with self._lock:
            now = time.time()
            # Add tokens based on time elapsed
            elapsed = now - self.last_update
            self.tokens = min(
                self.burst_size, self.tokens + elapsed * (self.requests_per_minute / 60.0)
            )
            self.last_update = now

            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

    async def wait_for_token(self, timeout: float = 60.0) -> bool:
        """Wait for a token to become available. Returns False if timeout exceeded."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if await self.acquire():
                return True
            await asyncio.sleep(0.1)
        return False


class ResilienceConfig:
    """Configuration for provider resilience."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        rate_limit_rpm: float = 60.0,
        timeout: float = 120.0,
        retry_on_429: bool = True,
        retry_on_500: bool = True,
        retry_on_502: bool = True,
        retry_on_503: bool = True,
        retry_on_504: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.rate_limit_rpm = rate_limit_rpm
        self.timeout = timeout
        self.retry_on_429 = retry_on_429
        self.retry_on_500 = retry_on_500
        self.retry_on_502 = retry_on_502
        self.retry_on_503 = retry_on_503
        self.retry_on_504 = retry_on_504


class ResilientProvider:
    """Wrapper for LLM providers with resilience features."""

    def __init__(
        self,
        provider: LLMProvider,
        config: Optional[ResilienceConfig] = None,
        provider_name: str = "unknown",
    ):
        self.provider = provider
        self.config = config or ResilienceConfig()
        self.provider_name = provider_name
        self.rate_limiter = RateLimiter(requests_per_minute=self.config.rate_limit_rpm)
        self._stats = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "retries": 0,
            "rate_limits": 0,
            "timeouts": 0,
        }

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if an error should trigger a retry."""
        if attempt >= self.config.max_retries:
            return False

        error_str = str(error).lower()

        # Network and connection errors
        if any(
            keyword in error_str
            for keyword in ["connection", "network", "timeout", "reset", "broken pipe"]
        ):
            return True

        # HTTP status codes (if we can detect them)
        if "429" in error_str and self.config.retry_on_429:
            self._stats["rate_limits"] += 1
            return True
        if any(
            code in error_str
            for code in ["500", "502", "503", "504"]
            if getattr(self.config, f"retry_on_{code}")
        ):
            return True

        # Provider-specific errors
        if any(
            keyword in error_str
            for keyword in ["rate limit", "quota exceeded", "server error", "service unavailable"]
        ):
            return True

        return False

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry using exponential backoff with jitter."""
        delay = min(
            self.config.base_delay * (self.config.backoff_factor**attempt), self.config.max_delay
        )

        if self.config.jitter:
            delay *= 0.5 + random.random() * 0.5  # Add up to 50% jitter

        return delay

    async def _execute_with_retry(
        self, operation: str, func: Any, *args: Any, **kwargs: Any  # Using Any or Callable
    ) -> Any:
        """Execute a function with retry logic."""
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                self._stats["requests"] += 1

                # Wait for rate limit token
                if not await self.rate_limiter.wait_for_token(timeout=10.0):
                    raise Exception("Rate limit timeout")

                # Execute with timeout
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)

                self._stats["successes"] += 1
                return result

            except Exception as e:
                last_error = e
                self._stats["failures"] += 1

                if self._should_retry(e, attempt):
                    self._stats["retries"] += 1
                    delay = self._calculate_delay(attempt)

                    logger.warning(
                        f"{self.provider_name} {operation} failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    await asyncio.sleep(delay)
                else:
                    break

        # All retries exhausted
        logger.error(
            f"{self.provider_name} {operation} failed after {self.config.max_retries + 1} attempts: {last_error}"
        )
        if last_error:
            raise last_error
        raise Exception(f"{operation} failed with unknown error")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion with resilience features."""
        return await self._execute_with_retry(
            "completion",
            self.provider.complete,
            system_prompt,
            user_prompt,
            max_tokens,
            temperature,
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion with resilience features."""
        # For streaming, we apply resilience to the initial request but let streaming continue
        # Streaming failures are harder to retry mid-stream
        try:
            async for chunk in self.provider.stream_complete(
                system_prompt, user_prompt, max_tokens, temperature
            ):
                yield chunk
        except Exception as e:
            logger.error(f"{self.provider_name} streaming failed: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get resilience statistics."""
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        for key in self._stats:
            self._stats[key] = 0


@asynccontextmanager
async def resilient_provider(
    provider: LLMProvider, config: Optional[ResilienceConfig] = None, provider_name: str = "unknown"
):
    """Context manager for creating a resilient provider."""
    resilient = ResilientProvider(provider, config, provider_name)
    try:
        yield resilient
    finally:
        # Cleanup if needed
        pass


# Default resilience configurations for different providers
DEFAULT_CONFIGS = {
    "anthropic": ResilienceConfig(
        max_retries=3,
        base_delay=1.0,
        rate_limit_rpm=50.0,  # Conservative for Anthropic
        timeout=120.0,
    ),
    "openai": ResilienceConfig(max_retries=3, base_delay=1.0, rate_limit_rpm=60.0, timeout=120.0),
    "gemini": ResilienceConfig(max_retries=3, base_delay=1.0, rate_limit_rpm=60.0, timeout=120.0),
    "http": ResilienceConfig(max_retries=2, base_delay=2.0, rate_limit_rpm=30.0, timeout=180.0),
    "default": ResilienceConfig(max_retries=3, base_delay=1.0, rate_limit_rpm=30.0, timeout=120.0),
}


def get_resilience_config(provider_name: str) -> ResilienceConfig:
    """Get default resilience configuration for a provider."""
    return DEFAULT_CONFIGS.get(provider_name, DEFAULT_CONFIGS["default"])
