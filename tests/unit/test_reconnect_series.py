"""Regression for the public reconnect-continuation defect (public-smoke-006/007): a
recoverable transport drop mid-series must let the driver open a FRESH session and finish
the remaining games -- it must NOT abandon the series or leave `series incomplete`
placeholders. The earlier fix reconnected but a RuntimeError on the reconnect hit a
`break`, so games 4-6 were never played; and a crashed session's cancel scope could block
the next session. These tests script the exact failing sequence at the transport boundary.

Deterministic; no live server / no ngrok."""

import anyio
import httpx
import pytest

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
    """Benign responder; optionally raises `err` at the Nth start_subgame (session drop)."""

    def __init__(self, drop_at=None, err=None):
        self.starts = 0
        self.drop_at = drop_at
        self.err = err or httpx.ConnectError("")

    async def call_tool(self, tool, kw):
        p = kw["payload"]
        base = {"request_id": p.get("_rid"), "session_id": p.get("_sid")}
        if tool == "start_subgame":
            self.starts += 1
            if self.drop_at and self.starts >= self.drop_at:
                raise self.err
            return _Resp({**base, "ok": True})
        if tool == "exchange":
            return _Resp({**base, "msg": {}, "claim_response": {"caught": False}})
        if tool == "finalize":
            return _Resp({**base, "records": []})
        return _Resp({**base})


class _Ctx:
    def __init__(self, client, enter_err=None):
        self.client, self.enter_err = client, enter_err

    async def __aenter__(self):
        if self.enter_err:
            raise self.enter_err  # drop at the session boundary (before any sub-game)
        return self.client

    async def __aexit__(self, *a):
        return False


class _Connector:
    """Scripts one _Ctx per connection attempt from a list of (kind, arg) plans."""

    def __init__(self, plans):
        self.plans, self.i, self.opens = plans, 0, 0

    def __call__(self, url, token):
        self.opens += 1
        kind, arg = self.plans[min(self.i, len(self.plans) - 1)]
        self.i += 1
        if kind == "enter_err":
            return _Ctx(None, enter_err=arg)
        return _Ctx(_FakeClient(drop_at=arg) if kind == "drop" else _FakeClient())


def _run(conn):
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
        conn,
    )


def _outs(res):
    return [g["outcome"] for g in res["sub_games"]]


def test_drop_after_game2_then_runtime_error_reconnect_then_completes():
    # exact public-007 shape: drop during game 3, reconnect first raises a connect-ish
    # RuntimeError (the old `break` trigger), then a fresh session finishes games 4-6.
    conn = _Connector(
        [("drop", 3), ("enter_err", RuntimeError("peer closed connection")), ("ok", None)]
    )
    res = _run(conn)
    outs = _outs(res)
    assert outs == ["survival", "survival", "technical", "survival", "survival", "survival"]
    assert conn.opens >= 3  # dropped session + failed reconnect + working reconnect
    assert all(g.get("reason") != "series incomplete" for g in res["sub_games"])  # none remain


def test_isolated_reconnect_after_clean_drop_finishes_series():
    conn = _Connector([("drop", 3), ("ok", None)])
    outs = _outs(_run(conn))
    assert outs.count("technical") == 1 and outs[2] == "technical"
    assert outs[3:] == ["survival", "survival", "survival"]  # games 4-6 actually executed


def test_exception_group_wrapped_drop_is_recoverable():
    # a drop that surfaces wrapped in an ExceptionGroup must still be classified recoverable
    grp = BaseExceptionGroup("stream", [httpx.ConnectError("")])
    ctxs = iter([_Ctx(_FakeClient(drop_at=3, err=grp)), _Ctx(_FakeClient())])
    res = _run(lambda u, t: next(ctxs))
    assert _outs(res) == ["survival", "survival", "technical", "survival", "survival", "survival"]


def test_connect_boundary_drop_before_any_game_loses_no_game():
    # a drop at the session boundary before game 1 must not consume a game
    conn = _Connector([("enter_err", httpx.ConnectError("")), ("ok", None)])
    assert _outs(_run(conn)) == ["survival"] * 6


def test_non_transport_error_is_reraised_not_swallowed():
    ctxs = iter([_Ctx(_FakeClient(drop_at=1, err=KeyError("bug")))])
    with pytest.raises(KeyError):
        _run(lambda u, t: next(ctxs))
