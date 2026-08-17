"""An opponent must not be able to exhaust our memory, and cannot flood us into a crash.

The inbound queues are filled directly by an unauthenticated peer over a public tunnel.
Every limit here is far above any legal 7x7 traffic — a whole six-sub-game series is about
thirty-six turns — so a conforming peer can never reach one.
"""

import queue

from thief_agent.interop.inboxes import PeerInboxes, accept
from thief_agent.shared import wirecheck as wc


def test_the_inboxes_are_bounded():
    boxes = PeerInboxes()
    for inbox in (boxes.agreements, boxes.turns, boxes.audits, boxes.controls):
        assert inbox.maxsize == wc.MAX_QUEUED
        assert inbox.maxsize > 0


def test_a_flood_is_dropped_rather_than_growing_without_bound():
    inbox = queue.Queue(4)
    assert all(accept(inbox, {"n": n})["ok"] for n in range(4))
    refused = accept(inbox, {"n": 5})
    assert refused["ok"] is False and "error" in refused
    assert inbox.qsize() == 4  # the flood cost the sender a message, not us our memory


def test_an_oversized_message_is_refused_without_being_queued():
    inbox = queue.Queue(8)
    assert accept(inbox, {"hint": "x" * (wc.MAX_MESSAGE_BYTES + 1)})["ok"] is False
    assert inbox.qsize() == 0


def test_a_legal_sized_turn_is_never_refused():
    """A full 7x7 scent field, a 15-word hint and a commit: nowhere near the cap."""
    legal = {
        "step": 12,
        "sender": "police",
        "commit": "a" * 64,
        "hint": "I am somewhere north of the old port, near the market square today",
        "smell_grid": {f"{r},{c}": 0.9 for r in range(7) for c in range(7)},
        "timestamp": "2026-08-08T19:00:00Z",
    }
    assert not wc.oversized(legal)
    assert accept(queue.Queue(8), legal)["ok"] is True


def test_the_limits_sit_well_above_legal_traffic():
    assert wc.MAX_QUEUED >= 256
    assert wc.MAX_MESSAGE_BYTES >= 64_000
    assert wc.AUDIT_RECORDS_PER_STEP >= 2  # tolerates a peer numbering half-turns


def test_enqueue_never_blocks_or_raises_on_a_full_inbox():
    inbox = queue.Queue(1)
    assert wc.enqueue(inbox, "first") is True
    assert wc.enqueue(inbox, "second") is False
