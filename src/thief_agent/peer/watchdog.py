"""Watchdog: detect a stalled peer and force a deterministic technical loss."""

import time


class Watchdog:
    def __init__(self, threshold_s: float, now=time.monotonic) -> None:
        self.threshold = threshold_s
        self._now = now
        self._beat = now()

    def heartbeat(self) -> None:
        self._beat = self._now()

    def stalled(self) -> bool:
        return (self._now() - self._beat) >= self.threshold
