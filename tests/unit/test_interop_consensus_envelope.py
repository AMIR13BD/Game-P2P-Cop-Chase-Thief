"""The final post-series consensus AuditPayload envelope, agreed VERBATIM with uoh-ay26:
sender = OUR wire role ("police"/"thief"), result_claim = "series_consensus", records = [],
consensus_sha = 64 lowercase hex. We accept the peer's digest ONLY when its envelope matches
exactly (peer wire role, tag, empty records, present sha); anything else fails safe. Covers
regression scenarios A-L.
"""

from thief_agent.interop.series import _CONSENSUS_TAG, _exchange_consensus
from thief_agent.interop.wire import AuditPayload

SHA = "0123456789abcdef" * 4  # a valid 64 lowercase hex digest
OTHER = "f" * 64


class _Transport:
    """Captures our outbound audit and replays one scripted peer response (wire dict or None)."""

    def __init__(self, peer_wire=None):
        self.sent = []
        self._peer = peer_wire

    def send_audit(self, payload):
        self.sent.append(payload)

    def poll_audit(self, timeout):
        peer, self._peer = self._peer, None
        return peer


def _peer(sender="thief", tag="series_consensus", records=None, sha=SHA):
    p = AuditPayload(sender, records if records is not None else [], tag, consensus_sha=sha)
    return p.to_wire()


def _run(our_role="police", peer_role="thief", peer_wire=None, sha=SHA):
    t = _Transport(peer_wire)
    got = _exchange_consensus(t, our_role, peer_role, sha, turn_timeout=1.0)
    return t, got


def test_outbound_envelope_uses_wire_role_tag_and_empty_records():
    """Scenarios A, B, C."""
    t, _ = _run(our_role="police")
    wire = t.sent[0]
    assert wire["sender"] == "police"  # A: our wire role, never a group id
    assert wire["result_claim"] == "series_consensus" == _CONSENSUS_TAG  # B
    assert wire["records"] == []  # C
    assert wire["consensus_sha"] == SHA


def test_valid_peer_envelope_is_accepted():
    """Scenario D."""
    _t, got = _run("police", "thief", _peer(sender="thief"))
    assert got == SHA


def test_wrong_result_claim_tag_is_rejected():
    """Scenario E: result_claim='consensus' (not 'series_consensus') -> not accepted."""
    _t, got = _run("police", "thief", _peer(sender="thief", tag="consensus"))
    assert got is None


def test_wrong_sender_role_is_rejected():
    """Scenario F: peer sender is not the expected complementary wire role."""
    _t, got = _run("police", "thief", _peer(sender="police"))
    assert got is None


def test_non_empty_records_is_rejected():
    """Scenario G."""
    _t, got = _run("police", "thief", _peer(sender="thief", records=[{"x": 1}]))
    assert got is None


def test_missing_consensus_sha_is_rejected():
    """Scenario H: an audit without a digest (per-sub-game straggler) never confirms."""
    _t, got = _run("police", "thief", _peer(sender="thief", sha=None))
    assert got is None


def test_mismatched_digest_is_returned_but_fails_equality_upstream():
    """Scenario I: a valid envelope with a DIFFERENT sha is envelope-accepted, but the caller's
    SHA-equality check (series.sha_match) then keeps confirmed false."""
    _t, got = _run("police", "thief", _peer(sender="thief", sha=OTHER), sha=SHA)
    assert got == OTHER  # envelope OK...
    assert got != SHA  # ...but the digests differ -> sha_match=False upstream -> confirmed false


def test_no_peer_response_fails_safely():
    """Scenario K support: a silent peer yields None (results are never rewritten here)."""
    _t, got = _run("police", "thief", None)
    assert got is None


def test_both_police_and_thief_produce_and_accept_the_agreed_envelope():
    """Scenario L: symmetric — each running role sends its own wire role and accepts the peer's."""
    tp, gp = _run("police", "thief", _peer(sender="thief"))
    assert tp.sent[0]["sender"] == "police" and gp == SHA
    tt, gt = _run("thief", "police", _peer(sender="police"))
    assert tt.sent[0]["sender"] == "thief" and gt == SHA
