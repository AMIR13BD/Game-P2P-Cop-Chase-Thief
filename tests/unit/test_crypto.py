import pytest

from thief_agent.domain.crypto import (
    audit_records,
    canonical_json,
    commit_of,
    fresh_nonce,
    seal,
    verify,
)
from thief_agent.exceptions import CryptoError


def test_canonical_key_order_independent():
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


def test_commit_deterministic_given_nonce():
    p = {"x": 1, "y": [2, 3]}
    assert commit_of(p, "ab") == commit_of(p, "ab")


def test_fresh_nonce_unique():
    assert len({fresh_nonce() for _ in range(2000)}) == 2000


def test_roundtrip_ok():
    p = {"step": 1, "move": "MOVE:N"}
    s = seal(p)
    verify(p, s["nonce"], s["commit"])


def test_tamper_payload_nonce_commit():
    p = {"step": 1, "move": "MOVE:N"}
    s = seal(p)
    with pytest.raises(CryptoError):
        verify({"step": 1, "move": "MOVE:S"}, s["nonce"], s["commit"])
    with pytest.raises(CryptoError):
        verify(p, "00" * 16, s["commit"])
    with pytest.raises(CryptoError):
        verify(p, s["nonce"], "0" * 64)


def test_audit_records_detects_tamper():
    recs = []
    for i in range(3):
        p = {"step": i}
        recs.append({"payload": p, **seal(p)})
    assert audit_records(recs)["passed"]
    recs[1]["commit"] = "0" * 64
    res = audit_records(recs)
    assert not res["passed"] and res["failed_steps"] == [1]
