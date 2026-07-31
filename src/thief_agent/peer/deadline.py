"""Deadline tracking so no operation waits forever."""

import time

from ..exceptions import ProtocolError


class Deadline:
    def __init__(self, seconds: float, now=time.monotonic) -> None:
        self._now = now
        self._end = now() + seconds

    def remaining(self) -> float:
        return self._end - self._now()

    def expired(self) -> bool:
        return self.remaining() <= 0

    def check(self) -> None:
        if self.expired():
            raise ProtocolError("deadline exceeded")
