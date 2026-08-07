"""Shared in-process loopback transport for interop integration tests (no sockets).

Two peers each own a set of queues; sends go to the PEER's queues, polls read the
OWN queues. ``dup=True`` delivers every turn twice to exercise the at-least-once
receiver contract. Not a test module (no ``test_`` prefix), so pytest imports but
never collects it."""

import queue


class Boxes:
    def __init__(self):
        self.agreements: queue.Queue = queue.Queue()
        self.turns: queue.Queue = queue.Queue()
        self.audits: queue.Queue = queue.Queue()


class Loopback:
    def __init__(self, own: Boxes, peer: Boxes, dup: bool = False):
        self.own = own
        self.peer = peer
        self.dup = dup

    def exchange_agreement(self, signed: dict) -> dict:
        self.peer.agreements.put(signed)
        return self.own.agreements.get(timeout=10)

    def send_turn(self, message: dict) -> None:
        self.peer.turns.put(message)
        if self.dup:
            self.peer.turns.put(dict(message))

    def poll_turn(self, timeout: float):
        try:
            return self.own.turns.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_audit(self, payload: dict) -> None:
        self.peer.audits.put(payload)

    def poll_audit(self, timeout: float):
        try:
            return self.own.audits.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_control(self, message):  # pragma: no cover - unused
        pass

    def poll_control(self):
        return None

    def drain_inboxes(self):  # pragma: no cover - unused
        pass
