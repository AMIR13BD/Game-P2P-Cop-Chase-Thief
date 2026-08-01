"""Regression: a six-sub-game networked series crosses the game-2 -> game-3 boundary
without a technical loss, and request IDs never repeat across sub-games (ruling out
idempotency/correlation leakage as a cause of technical). Also: a technical sub-game
now carries a surfaced reason (previously swallowed). Deterministic, no live server."""

import anyio

from thief_agent.infra.reliability import ReliableCaller
from thief_agent.peer.net_driver import play_subgame, score_row, technical_row
from thief_agent.peer.watchdog import Watchdog
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

CFG = validate(DEFAULT_GAME_CONFIG)


class _FakeResponder:
    """A benign in-process responder: valid, correlated replies; never captures."""

    def __init__(self):
        self.rids = []

    async def send(self, req):
        self.rids.append(req["request_id"])
        base = {"request_id": req["request_id"], "session_id": req["session_id"]}
        tool = req["payload"]["tool"]
        if tool == "exchange":
            return {**base, "msg": {}, "claim_response": {"caught": False}}
        if tool == "finalize":
            return {**base, "records": []}
        return {**base, "ok": True}


def test_six_subgames_cross_boundary_without_technical():
    fr = _FakeResponder()

    async def go():
        rc = ReliableCaller(
            fr.send, timeout_s=5, retries=1, backoff_s=0, session_id="amireman-thief-net"
        )
        outcomes = []
        for n in range(1, 7):  # thief-natural driver, same topology as the public run
            drole = "thief" if n % 2 == 1 else "police"
            sg = await play_subgame(
                rc, CFG, drole, n, "amireman-thief", "0" * 40, DevTestSigner(), Watchdog(60)
            )
            outcomes.append(sg["outcome"])
        return outcomes

    outcomes = anyio.run(go)
    assert len(outcomes) == 6
    assert outcomes[1] != "technical" and outcomes[2] != "technical"  # game 2 -> game 3
    assert all(o != "technical" for o in outcomes)  # whole series crosses cleanly
    assert len(fr.rids) == len(set(fr.rids))  # no request-id reuse across sub-games


def test_technical_rows_surface_reason():
    # Previously the technical-loss reason was discarded; it must now be carried.
    assert technical_row(3, "thief", "ExhaustedRetriesError: boom")["reason"] == (
        "ExhaustedRetriesError: boom"
    )
    row, _s, _o = score_row(
        1,
        "thief",
        {"outcome": "technical", "steps": 0, "records": [], "opp_records": [], "reason": "drop"},
    )
    assert row["reason"] == "drop"
    assert technical_row(1, "police")["reason"] is None  # default when unknown
