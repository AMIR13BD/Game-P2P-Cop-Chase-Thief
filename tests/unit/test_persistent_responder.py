"""Regression for the persistent-responder idempotency collision (public-smoke-003 ->
local-smoke-004): a second netplay series against the SAME responder process with the
SAME token must not be falsely rejected as a replay. Each run now gets a unique session
id, so its request ids are disjoint from a prior run's; the server idempotency cache is
keyed by (token, session, request-id). Anti-replay within a run is preserved.

Deterministic; no live server required."""

import pytest

from thief_agent.infra.idempotency import IdemCache
from thief_agent.infra.reliability import ReliableCaller, new_session_id

TOKEN = "MATCH_TOKEN"


def _run_ids(prefix, n):
    rc = ReliableCaller(
        None, timeout_s=1, retries=1, backoff_s=0, session_id=new_session_id(prefix)
    )
    return rc.session_id, [rc._next_id() for _ in range(n)]


def test_two_runs_unique_session_and_disjoint_request_ids():
    s1, ids1 = _run_ids("amireman-thief-net", 8)
    s2, ids2 = _run_ids("amireman-thief-net", 8)
    assert s1 != s2  # fresh session id per netplay invocation
    assert set(ids1).isdisjoint(ids2)  # no request-id reuse across runs


def test_persistent_idem_cache_no_false_collision_but_still_anti_replay():
    idem = IdemCache()
    s1, ids1 = _run_ids("amireman-thief-net", 8)
    s2, ids2 = _run_ids("amireman-thief-net", 8)

    def exchange(sid, rid, commit):
        payload = {"_rid": rid, "_sid": sid, "step": 1, "commit": commit}
        return idem.get_or_run(
            (TOKEN, sid, rid), IdemCache.fingerprint(payload), lambda: {"ok": rid}
        )

    exchange(s1, ids1[3], "aaaa")  # run 1, first exchange
    exchange(s2, ids2[3], "bbbb")  # run 2, same token+rid-suffix, different session -> OK now
    # Anti-replay is NOT weakened: same session+rid with a different payload still fails closed.
    with pytest.raises(ValueError, match="reused with a different payload"):
        exchange(s1, ids1[3], "cccc")
    # A genuine retry (same session+rid+payload) is still deduped without error.
    assert exchange(s1, ids1[3], "aaaa")["ok"] == ids1[3]
