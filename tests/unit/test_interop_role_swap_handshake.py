"""Role-swap negotiation race regression (peer router swaps the active role-agent
between sub-games). The mutual handshake must re-send our SAME offer until we have
also received the peer's offer for that sub-game. No protocol/canonical/audit change."""

import threading
import time

from thief_agent.interop.client import McpTransport
from thief_agent.interop.server import PeerInboxes


def _transport(sends):
    inboxes = PeerInboxes()
    t = McpTransport(
        "http://peer/mcp",
        inboxes,
        agreement_timeout=5.0,
        resend_interval=0.02,
        resend_timeout=0.5,
    )

    def fake_call(tool, argument, timeout=None):  # never touches the network
        sends.append(dict(argument))

    t._call_with_retry = fake_call  # type: ignore[method-assign]
    return t, inboxes


def test_role_swap_first_offer_lost_then_resent_completes():
    """Our 1st offer is accepted+lost by the old agent; the new agent posts its offer
    after we have re-sent, and we complete — proving we did NOT rely on one POST."""
    sends: list = []
    t, inboxes = _transport(sends)
    ours = {"sub_game_number": 2, "group_id": "amireman", "nonce": "N", "terms": {}}

    def peer_new_agent():
        # simulate the swapped-in agent only appearing after our first send is "lost"
        while len(sends) < 2:
            time.sleep(0.005)
        inboxes.agreements.put({"sub_game_number": 2, "group_id": "sharNamr"})

    threading.Thread(target=peer_new_agent, daemon=True).start()

    got = t.exchange_agreement(ours)
    assert got["group_id"] == "sharNamr" and got["sub_game_number"] == 2
    assert len(sends) >= 2, "must re-send our offer, not rely on a single POST"
    assert all(s == ours for s in sends), "every (re)send must be the IDENTICAL offer"


def test_normal_negotiation_still_works():
    sends: list = []
    t, inboxes = _transport(sends)
    inboxes.agreements.put({"sub_game_number": 1, "group_id": "sharNamr"})
    ours = {"sub_game_number": 1, "group_id": "amireman", "nonce": "N", "terms": {}}
    got = t.exchange_agreement(ours)
    assert got["group_id"] == "sharNamr"
    assert len(sends) >= 1


def test_duplicate_offers_are_safe():
    sends: list = []
    t, inboxes = _transport(sends)
    for _ in range(3):
        inboxes.agreements.put({"sub_game_number": 1, "group_id": "sharNamr"})
    ours = {"sub_game_number": 1, "nonce": "N", "terms": {}}
    got = t.exchange_agreement(ours)
    assert got["group_id"] == "sharNamr"  # accepts one; extras remain harmlessly queued


def test_stale_prev_subgame_offer_is_skipped():
    sends: list = []
    t, inboxes = _transport(sends)
    inboxes.agreements.put({"sub_game_number": 1, "group_id": "sharNamr"})  # stragggler
    inboxes.agreements.put({"sub_game_number": 2, "group_id": "sharNamr"})  # the real one
    ours = {"sub_game_number": 2, "nonce": "N", "terms": {}}
    got = t.exchange_agreement(ours)
    assert got["sub_game_number"] == 2


def test_bounded_timeout_no_infinite_hang():
    sends: list = []
    t, inboxes = _transport(sends)  # peer never sends anything
    ours = {"sub_game_number": 2, "nonce": "N", "terms": {}}
    start = time.time()
    raised = False
    try:
        t.exchange_agreement(ours)
    except Exception:
        raised = True
    assert raised, "must raise, not hang, when the peer never sends its offer"
    assert time.time() - start < 20.0, "must be bounded by agreement_timeout"
    assert len(sends) >= 2, "should have kept re-sending while waiting"
