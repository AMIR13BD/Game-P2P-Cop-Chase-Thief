"""Bounded local event log (P21): a fixed-capacity ring of human-readable events for
the GUI's activity pane. Old entries are dropped so memory stays bounded."""

from collections import deque


class EventLog:
    def __init__(self, capacity: int = 100) -> None:
        self.capacity = capacity
        self._events: deque[str] = deque(maxlen=capacity)

    def append(self, event) -> None:
        self._events.append(str(event))

    def tail(self, n: int = 10) -> list[str]:
        return list(self._events)[-n:] if n > 0 else []

    def render(self, n: int = 10) -> str:
        return "\n".join(self.tail(n))

    def __len__(self) -> int:
        return len(self._events)
