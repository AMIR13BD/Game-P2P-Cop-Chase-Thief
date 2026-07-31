"""Token-bucket rate limiter (requests per minute) with a stable long-run rate."""

import time


class TokenBucket:
    def __init__(self, rate_per_min: int, capacity: int | None = None, now=time.monotonic) -> None:
        self.rate = rate_per_min / 60.0
        self.capacity = float(capacity if capacity is not None else rate_per_min)
        self.tokens = self.capacity
        self._now = now
        self._ts = now()

    def _refill(self) -> None:
        t = self._now()
        self.tokens = min(self.capacity, self.tokens + (t - self._ts) * self.rate)
        self._ts = t

    def allow(self) -> bool:
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False
