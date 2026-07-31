import pytest

from thief_agent.infra.idempotency import IdemCache


def test_dedup_same_request_returns_cached_without_recompute():
    c = IdemCache()
    calls = {"n": 0}

    def compute():
        calls["n"] += 1
        return {"v": calls["n"]}

    fp = IdemCache.fingerprint({"a": 1, "_rid": "R", "_sid": "S"})
    r1 = c.get_or_run(("tok", "R"), fp, compute)
    r2 = c.get_or_run(("tok", "R"), fp, compute)
    assert r1 == r2 and calls["n"] == 1  # exactly one state transition


def test_same_id_changed_payload_rejected():
    c = IdemCache()
    c.get_or_run(("tok", "R"), "fp1", lambda: {"v": 1})
    with pytest.raises(ValueError):
        c.get_or_run(("tok", "R"), "fp2", lambda: {"v": 2})


def test_cache_scoped_by_session_token():
    c = IdemCache()
    calls = {"n": 0}

    def compute():
        calls["n"] += 1
        return calls["n"]

    a = c.get_or_run(("t1", "R"), "fp", compute)
    b = c.get_or_run(("t2", "R"), "fp", compute)  # different session -> fresh
    assert a == 1 and b == 2 and calls["n"] == 2


def test_cache_is_bounded():
    c = IdemCache(cap=5)
    for i in range(50):
        c.get_or_run(("t", f"R{i}"), "fp", lambda i=i: i)
    assert len(c._d) <= 5 and len(c._order) <= 5


def test_fingerprint_ignores_rid_and_sid():
    a = IdemCache.fingerprint({"x": 1, "_rid": "A", "_sid": "B"})
    b = IdemCache.fingerprint({"x": 1, "_rid": "C", "_sid": "D"})
    assert a == b
