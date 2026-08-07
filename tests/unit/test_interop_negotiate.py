"""Unit tests for the interop signed-terms negotiation gate and the official scoring:
negotiation happy path derives the shared ids and a reproducible signature; refusals cover
terms mismatch, bad signature, missing group, and a wrong-input game_uid declaration; the
scoring aggregation reproduces the reference points, alternation and series-tie award."""

import hashlib
import json

import pytest

from thief_agent.interop import scoring, terms
from thief_agent.interop.negotiate import NegotiationRefusedError, Negotiator
from thief_agent.interop.series import identity_for


def _canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _ref_sig(t, nonce):
    return hashlib.sha256(f"{_canon(t)}|{nonce}".encode()).hexdigest()


def _neg(group, t=None):
    t = t or terms.default_terms()
    return Negotiator(t, identity_for(group), group)


def test_negotiation_happy_path_derives_shared_ids():
    t = terms.default_terms()
    a, b = _neg("amireman", t), _neg("sparring-local", t)
    agreed = a.verify_peer(b.signed("thief", 1).to_wire())
    assert agreed.opponent_group == "sparring-local"
    seed = f"{_canon(t)}|{'|'.join(sorted(['amireman', 'sparring-local']))}"
    import uuid

    assert agreed.game_uid == str(uuid.UUID(bytes=hashlib.sha256(seed.encode()).digest()[:16]))
    msg = b.signed("thief", 1)
    assert msg.signature == _ref_sig(t, msg.nonce)  # independently reproducible


def test_negotiation_refuses_terms_mismatch():
    a = _neg("amireman")
    b = _neg("sparring-local", terms.default_terms(board_size=9))
    with pytest.raises(NegotiationRefusedError):
        a.verify_peer(b.signed("thief", 1).to_wire())


def test_negotiation_refuses_bad_signature_and_missing_group():
    a = _neg("amireman")
    good = _neg("sparring-local").signed("thief", 1).to_wire()
    with pytest.raises(NegotiationRefusedError):
        a.verify_peer({**good, "signature": "0" * 64})
    with pytest.raises(NegotiationRefusedError):
        a.verify_peer({**good, "group_id": "", "identity": {}})


def test_negotiation_refuses_wrong_uid_declaration():
    a = _neg("amireman")
    msg = _neg("sparring-local").signed("thief", 2, opponent_group="amireman").to_wire()
    with pytest.raises(NegotiationRefusedError):
        a.verify_peer({**msg, "game_uid": "00000000-0000-4000-8000-000000000000"})


def test_negotiation_refuses_incomplete_terms():
    a = _neg("amireman")
    good = _neg("sparring-local").signed("thief", 1).to_wire()
    broken = {**good, "terms": {k: v for k, v in good["terms"].items() if k != "board_size"}}
    with pytest.raises(NegotiationRefusedError):
        a.verify_peer(broken)


def test_negotiation_refuses_tampered_nonce():
    a = _neg("amireman")
    good = _neg("sparring-local").signed("thief", 1).to_wire()
    with pytest.raises(NegotiationRefusedError):
        a.verify_peer({**good, "nonce": "deadbeef"})


def test_scores_and_role_alternation():
    assert scoring.score_for("capture", "police") == 20
    assert scoring.score_for("survival", "thief") == 10
    assert scoring.score_for("timeout", "police") == 0
    assert scoring.role_for("police", 1) == "police"
    assert scoring.role_for("police", 2) == "thief"


def test_aggregate_survival_series_tie_and_decisive_winner():
    tie_rows = [
        {"result": "survival", "score": {"a": 5, "b": 10}},
        {"result": "survival", "score": {"a": 10, "b": 5}},
    ]
    agg = scoring.aggregate(tie_rows, "a", "b")
    assert agg["total_score"] == {"a": 17, "b": 17}  # 15+15, +2 each on a series tie
    assert agg["series_tie"] is True and agg["winner_group"] is None
    win = scoring.aggregate([{"result": "capture", "score": {"a": 20, "b": 5}}], "a", "b")
    assert win["winner_group"] == "a" and win["series_tie"] is False
