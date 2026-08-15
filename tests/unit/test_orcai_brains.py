"""Orcai-MJ counter, brain half: capture-on-adjacency, the STAY capture, safe
degradation behind the confidence gate, the Thief's hard safety tiers, and the
production factory's defaults and env overrides. Model/tracker/locator tests live
in test_orcai_counter.py."""

import os

from thief_agent.domain import smell
from thief_agent.domain.board import Board
from thief_agent.strategy.base import Action, Observation
from thief_agent.strategy.police_ringbreak import RingBreakerBrain
from thief_agent.strategy.production import make_gameplay_brain
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_antisqueeze import AntiSqueezeBrain

N = 7


def _obs(role, pos, step=1, scent=None, barriers=(), used=0):
    return Observation(
        role=role,
        self_pos=pos,
        board_size=N,
        barriers=frozenset(barriers),
        scent=dict(scent or {}),
        step=step,
        max_barriers=14,
        barriers_used=used,
    )


def _broadcast(cell):
    """The scent field an agent standing on `cell` actually puts on the wire."""
    return smell.step_update({}, cell, Board(N), 0.1)


def _step(pos, d):
    dr, dc = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}[d]
    return (pos[0] + dr, pos[1] + dc)


def test_cop_captures_by_stepping_onto_the_modelled_cell():
    brain = RingBreakerBrain(make_rng(1), horizon=35, seed=1)
    act = brain.decide(_obs("police", (0, 0), step=1, scent=_broadcast((0, 1))))
    assert brain.tracker.pred == (0, 1)
    assert act == Action("MOVE", "E")


def test_cop_stays_to_capture_a_thief_that_walked_onto_it():
    """Their ring term outweighs distance, so they do step onto us; STAY + claim ends it."""
    brain = RingBreakerBrain(make_rng(1), horizon=35, seed=1)
    act = brain.decide(_obs("police", (3, 3), step=1, scent=_broadcast((3, 3))))
    assert brain.tracker.pred == (3, 3) and act == Action("STAY")


def test_cop_defers_to_the_fallback_once_confidence_collapses():
    brain = RingBreakerBrain(make_rng(1), horizon=35, seed=1)
    brain.decide(_obs("police", (0, 0), step=1, scent=_broadcast((5, 5))))
    brain.tracker.hits = [False] * 8
    act = brain.decide(_obs("police", (0, 0), step=2, scent=_broadcast((5, 5))))
    assert brain.log[-1]["mode"] == "fallback" and act.kind in ("MOVE", "STAY", "BARRIER")


def test_thief_never_ends_within_pounce_range_when_it_can_avoid_it():
    brain = AntiSqueezeBrain(make_rng(3), horizon=35, seed=3)
    obs = _obs("thief", (3, 3), step=4, scent=smell.step_update({}, (3, 1), Board(N), 0.1))
    act = brain.decide(obs)
    dest = (3, 3) if act.kind == "STAY" else _step((3, 3), act.direction)
    cop = brain.locator.best
    assert abs(dest[0] - cop[0]) + abs(dest[1] - cop[1]) >= 2


def test_thief_action_is_always_legal_and_never_a_barrier():
    brain = AntiSqueezeBrain(make_rng(5), horizon=35, seed=5)
    for step in range(1, 12):
        act = brain.decide(_obs("thief", (3, 3), step=step, scent={(0, 0): 0.5}))
        assert act.kind in ("MOVE", "STAY")


def test_defaults_and_env_overrides(monkeypatch):
    monkeypatch.delenv("POLICE_STRATEGY", raising=False)
    monkeypatch.delenv("THIEF_STRATEGY", raising=False)
    monkeypatch.delenv("OPENAI_ADVISOR", raising=False)
    assert type(make_gameplay_brain("police", 1)).__name__ == "RingBreakerBrain"
    assert type(make_gameplay_brain("thief", 1)).__name__ == "AntiSqueezeBrain"
    monkeypatch.setenv("POLICE_STRATEGY", "meta")
    monkeypatch.setenv("THIEF_STRATEGY", "survivor")
    assert type(make_gameplay_brain("police", 1)).__name__ == "MetaController"
    assert type(make_gameplay_brain("thief", 1)).__name__ == "SurvivorBrain"
    assert os.environ.get("POLICE_STRATEGY") == "meta"
