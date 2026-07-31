"""Latency-injected opponent (P24 robustness): wraps any opponent with a bounded,
fixed decision delay so evaluation can measure behaviour against a slow peer. The
delay is small and configurable (default 0 so unit tests stay fast); it never changes
the chosen action, keeping results deterministic."""

import time

from ...strategy.base import Action, Observation


class LatencyBrain:
    def __init__(self, inner, delay_s: float = 0.0) -> None:
        self.inner = inner
        self.delay_s = delay_s

    def decide(self, obs: Observation) -> Action:
        if self.delay_s > 0:
            time.sleep(self.delay_s)
        return self.inner.decide(obs)

    def hint(self, obs: Observation) -> str:
        return self.inner.hint(obs)


def latency_opponent(factory, delay_s: float = 0.0):
    """Adapt an opponent factory into a latency-injected one for the harness."""
    return lambda rng: LatencyBrain(factory(rng), delay_s)
