"""Series-level regression for the TEST22 shape: aggregation, alternation, consensus.

TEST22 played six alternating sub-games in which our Thief survived (1/3/5) and our Cop
captured on step 9 (2/4/6). The peer scored that 90-30 to us; our own report said 30-15
because the three captures had been misrecorded as timeouts. These tests pin the correct
aggregation and the end-of-series consensus exchange.
"""

from thief_agent.interop.artifacts import build_result
from thief_agent.interop.scoring import role_for
from thief_agent.interop.series import _CONSENSUS_TAG, _exchange_consensus

OURS, THEIRS = "amireman", "Orcai-MJ"
SHA = "1" * 64
PEER_SHA = "2" * 64


def _summary(n, role, result):
    return {
        "sub_game_number": n,
        "role": role,
        "result": result,
        "winner": "police" if result == "capture" else "thief",
        "steps": 9 if result == "capture" else 35,
        "records": [],
        "audit": {"log_verified": True, "tampered": False, "result_agreed": True},
        "started_at": "t0",
        "duration_seconds": 1.0,
        "tokens_total": 0,
        "peer_github_commit": "b" * 40,
    }


def _test22_summaries():
    """Our natural role is thief: odd sub-games thief (survival), even police (capture)."""
    out = []
    for n in range(1, 7):
        role = role_for("thief", n)
        out.append(_summary(n, role, "survival" if role == "thief" else "capture"))
    return out


# ------------------------------------------------------------------ alternation
def test_roles_alternate_exactly_once_per_sub_game():
    assert [role_for("thief", n) for n in range(1, 7)] == [
        "thief",
        "police",
        "thief",
        "police",
        "thief",
        "police",
    ]


# ------------------------------------------------------------------ aggregation
def test_test22_pattern_aggregates_to_90_30():
    doc = build_result("TEST22", "uid", OURS, THEIRS, _test22_summaries())
    final = doc["final_result"]
    assert final["total_score"] == {OURS: 90, THEIRS: 30}
    assert final["sub_games_won"] == {OURS: 6, THEIRS: 0}
    assert final["winner_group"] == OURS
    assert final["series_tie"] is False
    assert final["ties"] == 0


def test_captures_are_recorded_as_capture_not_timeout():
    doc = build_result("TEST22", "uid", OURS, THEIRS, _test22_summaries())
    by_n = {r["sub_game_number"]: r for r in doc["sub_games"]}
    for n in (2, 4, 6):
        assert by_n[n]["result"] == "capture", f"sub-game {n} must be a capture"
        assert by_n[n]["score"] == {OURS: 20, THEIRS: 5}
    for n in (1, 3, 5):
        assert by_n[n]["result"] == "survival"
        assert by_n[n]["score"] == {OURS: 10, THEIRS: 5}


def test_a_timeout_row_would_score_zero_both_sides():
    """Guards the contrast: the old misclassification really did cost the points."""
    summaries = _test22_summaries()
    summaries[1]["result"] = "timeout"
    doc = build_result("TEST22", "uid", OURS, THEIRS, summaries)
    assert doc["final_result"]["total_score"][OURS] == 70


# -------------------------------------------------------------------- consensus
class _ConsensusTransport:
    def __init__(self, audits=()):
        self.audits = list(audits)
        self.sent_audits: list = []

    def send_audit(self, payload):
        self.sent_audits.append(payload)

    def poll_audit(self, timeout):
        return self.audits.pop(0) if self.audits else None


def _envelope(sender, sha, tag=_CONSENSUS_TAG, records=None):
    return {
        "sender": sender,
        "records": [] if records is None else records,
        "result_claim": tag,
        "consensus_sha": sha,
    }


def test_series_consensus_envelope_is_sent():
    tp = _ConsensusTransport([_envelope("police", SHA)])
    got = _exchange_consensus(tp, "thief", "police", SHA, turn_timeout=1.0)
    assert len(tp.sent_audits) == 1
    sent = tp.sent_audits[0]
    assert sent["result_claim"] == _CONSENSUS_TAG
    assert sent["records"] == []
    assert sent["consensus_sha"] == SHA
    assert sent["sender"] == "thief"
    assert got == SHA


def test_matching_digest_confirms_and_mismatch_does_not():
    tp = _ConsensusTransport([_envelope("police", SHA)])
    assert _exchange_consensus(tp, "thief", "police", SHA, turn_timeout=1.0) == SHA
    tp2 = _ConsensusTransport([_envelope("police", PEER_SHA)])
    assert _exchange_consensus(tp2, "thief", "police", SHA, turn_timeout=1.0) == PEER_SHA


def test_consensus_accepts_either_peer_wire_role():
    """Roles alternate, so the peer may label with its natural OR last-sub-game role."""
    for sender in ("police", "thief"):
        tp = _ConsensusTransport([_envelope(sender, SHA)])
        assert _exchange_consensus(tp, "thief", "police", SHA, turn_timeout=1.0) == SHA


def test_straggler_sub_game_audit_is_skipped_not_mistaken_for_consensus():
    straggler = {"sender": "police", "records": [{"payload": {}}], "result_claim": "capture"}
    tp = _ConsensusTransport([straggler, _envelope("police", SHA)])
    assert _exchange_consensus(tp, "thief", "police", SHA, turn_timeout=1.0) == SHA


def test_a_silent_peer_yields_no_digest_but_ours_was_still_sent():
    tp = _ConsensusTransport([])
    assert _exchange_consensus(tp, "thief", "police", SHA, turn_timeout=0.3) is None
    assert len(tp.sent_audits) == 1
