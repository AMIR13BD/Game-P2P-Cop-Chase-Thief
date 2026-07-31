import anyio
import pytest

from thief_agent.exceptions import ExhaustedRetriesError
from thief_agent.infra.reliability import ReliableCaller
from thief_agent.peer.deadline import Deadline


def _ok(req):
    return {
        "request_id": req["request_id"],
        "session_id": req["session_id"],
        "echo": req["payload"],
    }


def _caller(send, **kw):
    kw.setdefault("timeout_s", 1.0)
    kw.setdefault("retries", 3)
    kw.setdefault("backoff_s", 0.0)
    return ReliableCaller(send, **kw)


async def _ok_send(req):
    return _ok(req)


def test_success():
    r = anyio.run(_caller(_ok_send).call, {"x": 1})
    assert r["echo"] == {"x": 1}


def test_retry_then_success_after_drops():
    calls = {"n": 0}

    async def send(req):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise ConnectionError("dropped")
        return _ok(req)

    r = anyio.run(_caller(send, retries=3).call, {"x": 1})
    assert r["echo"] == {"x": 1} and calls["n"] == 3


def test_exhausted_retries_raises():
    async def send(req):
        raise ConnectionError("always")

    with pytest.raises(ExhaustedRetriesError):
        anyio.run(_caller(send, retries=3).call, {"x": 1})


def test_exhausted_maps_to_technical_zero_zero():
    async def send(req):
        raise ConnectionError("always")

    r = anyio.run(_caller(send, retries=2).call_or_technical, {"x": 1})
    assert r["outcome"] == "technical" and r["police_score"] == 0 and r["thief_score"] == 0


def test_timeout_then_retry():
    calls = {"n": 0}

    async def send(req):
        calls["n"] += 1
        if calls["n"] == 1:
            await anyio.sleep(5)
        return _ok(req)

    r = anyio.run(_caller(send, timeout_s=0.2, retries=3).call, {"x": 1})
    assert r["echo"] == {"x": 1} and calls["n"] == 2


def test_delayed_within_timeout_ok():
    async def send(req):
        await anyio.sleep(0.05)
        return _ok(req)

    assert anyio.run(_caller(send, timeout_s=1.0).call, {"x": 1})["echo"] == {"x": 1}


def test_duplicate_request_served_from_cache():
    calls = {"n": 0}

    async def send(req):
        calls["n"] += 1
        return _ok(req)

    c = _caller(send)
    a = anyio.run(c.call, {"x": 1}, "rid-1")
    b = anyio.run(c.call, {"x": 1}, "rid-1")
    assert a == b and calls["n"] == 1


def test_correlation_mismatch_rejected():
    async def send(req):
        return {"request_id": "WRONG", "session_id": req["session_id"]}

    with pytest.raises(ExhaustedRetriesError):
        anyio.run(_caller(send, retries=2).call, {"x": 1})


def test_malformed_response_rejected():
    async def send(req):
        return "not-a-dict"

    with pytest.raises(ExhaustedRetriesError):
        anyio.run(_caller(send, retries=2).call, {"x": 1})


def test_stale_session_rejected():
    async def send(req):
        return {"request_id": req["request_id"], "session_id": "OTHER"}

    with pytest.raises(ExhaustedRetriesError):
        anyio.run(_caller(send, retries=2).call, {"x": 1})


def test_deadline_enforced():
    with pytest.raises(ExhaustedRetriesError):
        anyio.run(
            _caller(_ok_send, deadline=Deadline(0.0, now=lambda: 0.0), retries=2).call, {"x": 1}
        )


def test_programmer_error_not_swallowed():
    async def send(req):
        raise ValueError("bug")

    with pytest.raises(ValueError):
        anyio.run(_caller(send).call, {"x": 1})


def test_bounded_memory_cache():
    c = _caller(_ok_send, cache_max=5)
    for i in range(50):
        anyio.run(c.call, {"i": i}, f"rid-{i}")
    assert len(c._seen) <= 5 and len(c._order) <= 5
