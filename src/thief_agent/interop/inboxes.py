"""The peer's inbound mailboxes and the one place an untrusted message is taken in.

Split out of ``server.py`` to keep both modules inside the repository's 150-line ceiling.

These queues are filled directly by an unauthenticated opponent over a public tunnel, so
they are BOUNDED. An unbounded queue on that path is an invitation to exhaust our memory
during a counted window, and it costs the sender nothing. The cap is orders of magnitude
above any legal traffic — a whole six-sub-game series is roughly thirty-six turns, six
audits and six agreements — so it can only be reached deliberately.

Refusal here is deliberately quiet and local: we drop the arrival and say so in the tool's
return value. We do NOT convert a flood into a game outcome, because that would let a peer
choose our result by sending garbage rather than by playing.
"""

import queue

from ..shared.wirecheck import MAX_QUEUED, enqueue, oversized


class PeerInboxes:
    """Thread-safe mailboxes filled by MCP tools, drained by the runtime."""

    def __init__(self, maxsize: int = MAX_QUEUED):
        self.agreements: queue.Queue = queue.Queue(maxsize)
        self.turns: queue.Queue = queue.Queue(maxsize)
        self.audits: queue.Queue = queue.Queue(maxsize)
        self.controls: queue.Queue = queue.Queue(maxsize)


def accept(inbox: queue.Queue, message: object) -> dict:
    """Take one inbound message, or refuse it without raising into the ASGI worker."""
    if oversized(message) or not enqueue(inbox, message):
        return {"ok": False, "error": "refused: message too large or inbox full"}
    return {"ok": True}
