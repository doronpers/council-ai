# Test resilience module

from council_ai.providers import RateLimiter, ResilienceConfig


def test_rate_limiter():
    limiter = RateLimiter(requests_per_minute=60.0)
    assert limiter.requests_per_minute == 60.0


def test_resilience_config():
    config = ResilienceConfig(max_retries=5)
    assert config.max_retries == 5
