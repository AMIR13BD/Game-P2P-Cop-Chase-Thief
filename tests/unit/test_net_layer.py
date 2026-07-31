"""In-process coverage of the peer network layer: PeerHalf message logic and the
net_driver helpers (role rotation, brain selection, reliable send, sub-game loop)
exercised with fakes so no live transport is required."""

import anyio

from thief_agent.constants import Role
from thief_agent.peer import net_driver
from thief_agent.peer.net_engine import PeerHalf, _grid_in, _grid_out
from thief_agent.peer.watchdog import Watchdog
from thief_agent.security.signer import DevTestSigner
from thief_agent.strategy.police_greedy import PoliceGreedyBrain
from thief_agent.strategy.rng import make_rng


def _half(cfg, role):
    brain = PoliceGreedyBrain(make_rng(1))
    return PeerHalf(role, cfg, brain, "grp", "0" * 40, DevTestSigner(), sub_game=1)


def test_grid_round_trip():
    g = {(1, 2): 0.5, (3, 4): 0.25}
    assert _grid_in(_grid_out(g)) == g
    assert _grid_in(None) == {}


def test_peer_half_act_emits_public_message(cfg):
    half = _half(cfg, "police")
    msg = half.act()
    assert msg["step"] == 1 and msg["sender"] == "police"
    assert set(msg) == {"step", "sender", "commit", "hint", "scent", "claim"}
    assert len(half.records) == 2  # step-0 record + first turn


def test_peer_half_receive_absorbs_opponent(cfg):
    police = _half(cfg, "police")
    thief = _half(cfg, "thief")
    out = police.act()
    caught = thief.receive(out)
    assert isinstance(caught, bool)
    assert thief.recv_hint == out["hint"]


def test_role_for_alternates():
    assert net_driver.role_for(Role.POLICE, 1) == Role.POLICE
    assert net_driver.role_for(Role.POLICE, 2) == Role.THIEF


def test_brain_selection():
    assert net_driver.brain("police", 1).__class__.__name__ == "PoliceGreedyBrain"
    assert net_driver.brain("thief", 1).__class__.__name__ == "ThiefDistanceBrain"


def test_technical_and_score_rows():
    tr = net_driver.technical_row(2, "police")
    assert tr["outcome"] == "technical" and tr["self_score"] == 0
    row, s, o = net_driver.score_row(
        1, "police", {"outcome": "capture", "steps": 4, "records": [], "opp_records": []}
    )
    assert row["self_role"] == "police" and s >= 0 and o >= 0


class _Data:
    def __init__(self, data):
        self.data = data


class _FakeClient:
    async def call_tool(self, tool, kwargs):
        return _Data({"ok": True, "tool": tool})


def test_make_send_correlates_ids():
    send = net_driver.make_send(_FakeClient())

    async def go():
        return await send(
            {"payload": {"tool": "exchange", "args": {}}, "request_id": "r1", "session_id": "s1"}
        )

    out = anyio.run(go)
    assert out["request_id"] == "r1" and out["session_id"] == "s1"


class _FakeRC:
    def __init__(self, exchange):
        self._exchange = exchange

    async def call(self, req):
        tool = req["tool"]
        if tool == "exchange":
            return self._exchange
        if tool == "finalize":
            return {"records": []}
        return {}


def test_play_subgame_capture(cfg):
    rc = _FakeRC({"claim_response": {"caught": True}, "msg": {}})

    async def go():
        return await net_driver.play_subgame(
            rc, cfg, "police", 1, "grp", "0" * 40, DevTestSigner(), Watchdog(60)
        )

    sg = anyio.run(go)
    assert sg["outcome"] == "capture" and sg["records"]
