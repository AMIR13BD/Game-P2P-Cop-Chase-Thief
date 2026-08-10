"""Barrier encoding on the peer-facing wire/audit. Per the HW PDF §3.4, a Cop barrier
turn FOREGOES movement, so its sealed move must be the legal token STAY and the placement
is declared SEPARATELY as barrier_placed — never as an illegal 'BARRIER:*' move token
(move_set is FIXED N,S,E,W,STAY). Reproduces the reported Game-2 BARRIER:N/E/W/S records.
"""

import json

from thief_agent.peer.net_engine import PeerHalf
from thief_agent.security.signer import DevTestSigner
from thief_agent.strategy.base import Action


def _legal_move(m: str) -> bool:
    # peers accept a bare N/S/E/W/STAY token or the MOVE:<dir> form; never BARRIER:*
    return m == "STAY" or (m.startswith("MOVE:") and m.split(":", 1)[1] in {"N", "S", "E", "W"})


CFG = {
    "grid_size": 7,
    "cop_start": [0, 0],
    "thief_start": [3, 3],
    "pheromone_decay": 0.1,
    "max_barriers": 14,
}
LEGAL = {"N", "S", "E", "W", "STAY"}


class _BarrierBrain:
    def decide(self, obs):
        return Action("BARRIER", "S")  # place a barrier one step south (foregoes movement)

    def hint(self, obs):
        return "sealing a lane"


class _MoveBrain:
    def decide(self, obs):
        return Action("MOVE", "E")

    def hint(self, obs):
        return "east"


def _police(brain):
    return PeerHalf("police", CFG, brain, "g", "0" * 40, DevTestSigner(), 1)


def test_barrier_turn_seals_stay_and_separate_barrier_placed():
    ph = _police(_BarrierBrain())
    start = ph.pos
    out = ph.act()
    rec = ph.records[-1]["payload"]
    # move is the legal no-move token; NOT an illegal 'BARRIER:*'
    assert rec["move"] == "STAY"
    assert rec["move"] in LEGAL
    assert "BARRIER" not in rec["move"]
    # barrier is declared SEPARATELY (sealed + on the wire), and the Cop did not move
    assert rec["barrier_placed"] == [start[0] + 1, start[1]]  # one step south of (0,0)
    assert out["barrier_placed"] == rec["barrier_placed"]
    assert ph.pos == start  # foregoes movement (no physical move on a barrier turn)
    # never a BARRIER:* token anywhere on the wire or in the sealed record
    assert "BARRIER:" not in json.dumps(out) + json.dumps(ph.records[-1])


def test_normal_move_still_moves_and_has_no_barrier_field():
    ph = _police(_MoveBrain())
    out = ph.act()
    rec = ph.records[-1]["payload"]
    assert rec["move"] == "MOVE:E"  # peers normalize MOVE:<dir> -> E
    assert "barrier_placed" not in rec  # absent when no barrier placed
    assert out["barrier_placed"] is None


def test_no_barrier_move_token_across_a_multi_step_police_run():
    ph = _police(_BarrierBrain())
    seen = set()
    for _ in range(6):
        ph.act()
        seen.add(ph.records[-1]["payload"]["move"])
    assert all(_legal_move(m) for m in seen), seen
    assert not any(m.startswith("BARRIER") for m in seen)
