"""Black-box interop: our production runtime plays a full six-sub-game series against an
INDEPENDENT stdlib-only reference-v3 peer (``blackbox_peer.BlackBoxPeer``) that imports
none of our adapter, then each side audits the other's revealed records with its own
serializer. Approximates a random compliant student team (SPEC §15)."""

import threading

from blackbox_peer import BlackBoxPeer, game_uid
from interop_loopback import Boxes, Loopback

from thief_agent.interop.series import run_series
from thief_agent.interop.terms import default_terms


def test_our_runtime_plays_an_independent_blackbox_peer():
    a, b = Boxes(), Boxes()
    terms = default_terms()
    bb = BlackBoxPeer("blackbox-student", terms, b, a)
    ours: dict = {}

    def our_side():
        ours["r"] = run_series(
            terms, "police", Loopback(a, b), "amireman", "local", num_games=6, turn_timeout=8.0
        )

    t1 = threading.Thread(target=our_side)
    t2 = threading.Thread(target=bb.run_series)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    result = ours["r"]
    # 1. identifiers recomputed identically by both independent implementations
    assert result.game_id == "amireman-vs-blackbox-student"
    assert result.game_uid == game_uid(terms, "amireman", "blackbox-student")
    # 2. six sub-games, alternating roles, complementary to the black-box
    assert len(result.summaries) == 6 and len(bb.results) == 6
    assert [s["role"] for s in result.summaries] == ["police", "thief"] * 3
    for ours_sg, bb_sg in zip(result.summaries, bb.results, strict=True):
        assert ours_sg["role"] != bb_sg["role"]
        assert ours_sg["result"] == bb_sg["result"]  # both settle identically
        # 3. our records pass the black-box's independent re-hash audit, and theirs pass ours
        assert bb_sg["opponent_audit_ok"] and ours_sg["audit"]["log_verified"]
        assert not ours_sg["audit"]["tampered"]
