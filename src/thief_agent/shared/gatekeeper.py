"""DoS guard: enforce max concurrency + bounded queue and a per-minute rate.

Admission capacity is max_concurrent + queue_depth; beyond that -> QueueFullError.
(Per PDF rule #28 the per-minute limiter targets the OUTGOING Gmail report path;
the concurrency/queue guard protects any network endpoint from overload.)"""

from ..exceptions import QueueFullError, RateLimitError
from .rate_limiter import TokenBucket


class Gatekeeper:
    def __init__(
        self, requests_per_minute: int, concurrent_requests: int, queue_depth: int, now=None
    ) -> None:
        self.bucket = (
            TokenBucket(requests_per_minute)
            if now is None
            else TokenBucket(requests_per_minute, now=now)
        )
        self.capacity = concurrent_requests + queue_depth
        self.inflight = 0

    def admit(self) -> None:
        if not self.bucket.allow():
            raise RateLimitError("requests-per-minute exceeded")
        if self.inflight >= self.capacity:
            raise QueueFullError("request queue overflow")
        self.inflight += 1

    def release(self) -> None:
        self.inflight = max(0, self.inflight - 1)
