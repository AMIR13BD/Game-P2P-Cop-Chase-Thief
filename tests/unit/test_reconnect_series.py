"""Regression for the public six-game transport defect (public-smoke-003/006): a
recoverable transport drop mid-series must NOT turn every remaining sub-game technical.
The driver isolates the drop to the current sub-game and RECONNECTS a fresh session to
finish the rest. Two drop shapes are covered at the real transport boundary:

  * a session that drops *during* sub-game 3 (surfaces via the per-call guard); and
  * a bare httpx.ConnectError at *connect time* (surfaces at the `async with` boundary,
    exactly like the empty-message ConnectError seen over ngrok).

Deterministic; no live server / no ngrok. Mirrors the observed "fails after two games"
pattern but proves recovery."""

import anyio
import httpx

from thief_agent.constants import Role
from thief_agent.peer.net_runtime import run_networked
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

CFG = validate(DEFAULT_GAME_CONFIG)


class _Resp:
    def __init__(self, data):
        self.data = data


class _FakeClient:
    """Benign responder; optionally drops the session at the Nth start_subgame."""

    def __init__(self, drop_at_start=None):
        self.starts = 0
        self.drop_at_start = drop_at_start

    async def call_tool(self, tool, kw):
        p = kw["payload"]
        base = {"request_id": p.get("_rid"), "session_id": p.get("_sid")}
        if tool == "start_subgame":
            self.starts += 1
            if self.drop_at_start and self.starts >= self.drop_at_start:
                raise httpx.ConnectError("")  # session dropped mid-series
            return _Resp({**base, "ok": True})
        if tool == "exchange":
            return _Resp({**base, "msg": {}, "claim_response": {"caught": False}})
        if tool == "finalize":
            return _Resp({**base, "records": []})
        return _Resp({**base})  # negotiate/confirm/etc.


class _Ctx:
    def __init__(self, client, fail_enter=False):
        self.client, self.fail_enter = client, fail_enter

    async def __aenter__(self):
        if self.fail_enter:
            raise httpx.ConnectError("")  # bare, empty-message drop at connect time
        return self.client

    async def __aexit__(self, *a):
        return False


def _run(connect):
    return anyio.run(
        run_networked,
        "https://x.example/mcp",
        "TOK",
        CFG,
        Role.THIEF,
        "amireman-thief",
        "0" * 40,
        DevTestSigner(),
        1234,
        None,
        5,
        1,
        0.0,
        connect,
    )


def test_drop_during_subgame3_reconnects_and_completes_all_six():
    opens = {"n": 0}

    def connect(url, token):
        opens["n"] += 1
        return _Ctx(_FakeClient(drop_at_start=3 if opens["n"] == 1 else None))

    res = _run(connect)
    outs = [s["outcome"] for s in res["sub_games"]]
    assert len(outs) == 6
    assert outs[0] == "survival" and outs[1] == "survival"  # two complete games, as observed
    assert outs[2] == "technical"  # the dropped sub-game
    assert outs[3:] == ["survival", "survival", "survival"]  # RECONNECTED and continued
    assert outs.count("technical") == 1  # NOT every remaining game turned technical
    assert opens["n"] == 2  # exactly one reconnect
    reason = res["sub_games"][2]["reason"]
    assert reason and "series incomplete" not in reason  # surfaced, not a bare fill


def test_bare_connect_error_at_boundary_is_recovered():
    opens = {"n": 0}

    def connect(url, token):
        opens["n"] += 1
        return _Ctx(_FakeClient(), fail_enter=(opens["n"] == 1))

    res = _run(connect)
    outs = [s["outcome"] for s in res["sub_games"]]
    assert outs[0] == "technical" and outs[1:] == ["survival"] * 5  # first drop, then recover
    assert "ConnectError" in (res["sub_games"][0]["reason"] or "")  # improved diagnostic
    assert res["sub_games"][0]["reason"].strip() != "ConnectError:"  # never bare/empty
