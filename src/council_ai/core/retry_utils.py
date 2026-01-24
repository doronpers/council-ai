"""
Retry utilities for handling transient failures in LLM API calls.

Provides decorators and utilities for implementing exponential backoff,
rate limit handling, and robust error recovery.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, Set, Type, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic function signatures
T = TypeVar("T")


class RetryableError(Exception):
    """Base class for errors that should trigger a retry."""

    pass


class RateLimitError(RetryableError):
    """Error raised when API rate limits are exceeded."""

    pass


class TransientAPIError(RetryableError):
    """Error raised for transient API failures (network, timeout, etc.)."""

    pass


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error should trigger a retry.

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable, False otherwise
    """
    # Check if it's explicitly a retryable error
    if isinstance(error, RetryableError):
        return True

    # Check error message for common retryable patterns
    error_str = str(error).lower()
    retryable_patterns = [
        "rate limit",
        "too many requests",
        "timeout",
        "connection",
        "network",
        "temporarily unavailable",
        "service unavailable",
        "429",  # HTTP 429 Too Many Requests
        "503",  # HTTP 503 Service Unavailable
        "504",  # HTTP 504 Gateway Timeout
    ]

    return any(pattern in error_str for pattern in retryable_patterns)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_factor: float = 2.0,
    retryable_exceptions: Optional[Set[Type[Exception]]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exponential_factor: Factor to multiply delay by after each retry (default: 2.0)
        retryable_exceptions: Set of exception types to retry on. If None, uses is_retryable_error

    Returns:
        Decorated function with retry logic

    Example:
        ```python
        @retry_with_backoff(max_retries=3, base_delay=2.0)
        async def call_api():
            return await provider.complete(...)
        ```
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this error should be retried
                    should_retry = False
                    if retryable_exceptions:
                        should_retry = any(
                            isinstance(e, exc_type) for exc_type in retryable_exceptions
                        )
                    else:
                        should_retry = is_retryable_error(e)

                    # If not retryable or out of retries, raise immediately
                    if not should_retry or attempt >= max_retries:
                        if attempt > 0:
                            logger.error(
                                f"Function {func.__name__} failed after {attempt + 1} attempts: {e}"
                            )
                        raise

                    # Log retry and wait
                    logger.warning(
                        f"Retrying {func.__name__} after error (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Waiting {delay:.2f}s before retry..."
                    )
                    await asyncio.sleep(delay)

                    # Increase delay for next retry (exponential backoff with cap)
                    delay = min(delay * exponential_factor, max_delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            delay = base_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this error should be retried
                    should_retry = False
                    if retryable_exceptions:
                        should_retry = any(
                            isinstance(e, exc_type) for exc_type in retryable_exceptions
                        )
                    else:
                        should_retry = is_retryable_error(e)

                    # If not retryable or out of retries, raise immediately
                    if not should_retry or attempt >= max_retries:
                        if attempt > 0:
                            logger.error(
                                f"Function {func.__name__} failed after {attempt + 1} attempts: {e}"
                            )
                        raise

                    # Log retry and wait
                    logger.warning(
                        f"Retrying {func.__name__} after error (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Waiting {delay:.2f}s before retry..."
                    )
                    time.sleep(delay)

                    # Increase delay for next retry (exponential backoff with cap)
                    delay = min(delay * exponential_factor, max_delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_factor: float = 2.0,
    **kwargs: Any,
) -> T:
    """
    Retry an async function with exponential backoff (functional API).

    This is an alternative to the decorator for cases where you want
    to retry a function call without decorating it.

    Args:
        func: The async function to retry
        *args: Positional arguments to pass to the function
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_factor: Factor to multiply delay by after each retry
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call

    Example:
        ```python
        result = await retry_async(
            provider.complete,
            prompt="test",
            max_retries=3
        )
        ```
    """
    decorated: Callable[..., Awaitable[T]] = retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_factor=exponential_factor,
    )(func)

    return await decorated(*args, **kwargs)
