def test_rate_limiter_allows_under_limit():
    from app.rate_limit import RateLimiter
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    for _ in range(5):
        assert limiter.check("1.2.3.4") is True


def test_rate_limiter_blocks_over_limit():
    from app.rate_limit import RateLimiter
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    for _ in range(3):
        limiter.check("1.2.3.4")
    assert limiter.check("1.2.3.4") is False


def test_rate_limiter_isolates_ips():
    from app.rate_limit import RateLimiter
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.check("1.1.1.1")
    limiter.check("1.1.1.1")
    assert limiter.check("1.1.1.1") is False
    assert limiter.check("2.2.2.2") is True
