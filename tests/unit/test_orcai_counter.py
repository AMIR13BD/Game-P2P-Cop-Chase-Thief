"""Tests for the Orcai-MJ counter: opponent model, tracker, Cop locator, both brains.

Covers the properties the strategy actually relies on -- the ring lock, exact
prediction, evidence overruling the model, the Barrier-Law constraint (including a
Cop standing on a wall of its own making), capture-on-adjacency, the STAY capture,
safe degradation behind the confidence gate, and the Thief's hard safety tiers.
"""

import os

from thief_agent.domain import smell
from thief_agent.domain.board import Board
from thief_agent.strategy.base import Action, Observation
from thief_agent.strategy.cop_locate import CopLocator
from thief_agent.strategy.orcai_model import OrcaiBelief, ring_cells, ring_of, ringrunner_next
from thief_agent.strategy.orcai_track import OrcaiThiefTracker
from thief_agent.strategy.police_ringbreak import RingBreakerBrain
from thief_agent.strategy.production import make_gameplay_brain
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_antisqueeze import AntiSqueezeBrain

N = 7


def _obs(role, pos, step=1, scent=None, barriers=(), used=0):
    return Observation(
        role=role, self_pos=pos, board_size=N, barriers=frozenset(barriers),
        scent=dict(scent or {}), step=step, max_barriers=14, barriers_used=used,
    )


# ------------------------------------------------------------------ their model
def test_ring_index_and_ring_one_loop():
    assert ring_of((0, 0), N) == 0 and ring_of((1, 1), N) == 1 and ring_of((3, 3), N) == 3
    loop = ring_cells(N, 1)
    assert len(loop) == 16 and (1, 1) in loop and (3, 3) not in loop


def test_ring_lock_never_leaves_ring_one():
    """Ring weight 3 beats any one-step distance swing (max 2): the loop is a trap."""
    board = Board(N)
    for cell in sorted(ring_cells(N, 1)):
        for hunter in ((0, 0), (6, 6), (3, 3), (0, 6)):
            assert ring_of(ringrunner_next(cell, hunter, board), N) == 1


def test_ringrunner_holds_when_walled_in():
    board = Board(N, {(0, 1), (1, 0)})
    assert ringrunner_next((0, 0), (6, 6), board) == (0, 0)


def test_belief_argmax_breaks_ties_to_lowest_cell():
    assert OrcaiBelief(N).most_likely() == (0, 0)


def test_belief_fuse_moves_argmax_to_the_scented_cell():
    b = OrcaiBelief(N)
    b.fuse({(5, 2): 0.9})
    assert b.most_likely() == (5, 2)


# --------------------------------------------------------------------- tracker
def test_tracker_advances_once_per_step_and_is_idempotent():
    board = Board(N)
    t = OrcaiThiefTracker(N, (3, 3))
    first = t.advance(_obs("police", (0, 0), step=1), board)
    assert t.advance(_obs("police", (0, 0), step=1), board) == first


def test_tracker_resync_lets_evidence_overrule_the_model():
    t = OrcaiThiefTracker(N, (3, 3))
    assert t.resync((6, 6)) == (6, 6) and t.pred == (6, 6)


def test_tracker_confidence_falls_when_evidence_disagrees():
    t = OrcaiThiefTracker(N, (3, 3))
    for _ in range(8):
        t.score({}, evidence=(0, 0))  # model says (3,3), evidence says otherwise
    assert t.confidence == 0.0


# --------------------------------------------------------------------- locator
def test_locator_keeps_a_cop_standing_on_its_own_wall():
    """A Cop may wall the cell it occupies, so a barrier is not evidence of absence."""
    board = Board(N, {(2, 2)})
    loc = CopLocator(N, (2, 2))
    assert (2, 2) in loc.update({}, frozenset({(2, 2)}), board)


def test_locator_applies_the_barrier_law_only_for_a_cop():
    board = Board(N, {(6, 6)})
    cop = CopLocator(N, (0, 0))
    cop.update({}, frozenset({(6, 6)}), board)
    assert all(abs(c[0] - 6) + abs(c[1] - 6) <= 1 for c in cop.candidates)
    thief = CopLocator(N, (0, 0), barrier_law=False)
    thief.update({}, frozenset({(6, 6)}), board)
    assert (6, 6) not in thief.candidates  # a far wall says nothing about a Thief


# ------------------------------------------------------------------- Cop brain
def _broadcast(cell):
    """The scent field an agent standing on `cell` actually puts on the wire."""
    return smell.step_update({}, cell, Board(N), 0.1)


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


# ----------------------------------------------------------------- Thief brain
def test_thief_never_ends_within_pounce_range_when_it_can_avoid_it():
    brain = AntiSqueezeBrain(make_rng(3), horizon=35, seed=3)
    obs = _obs("thief", (3, 3), step=4, scent=smell.step_update({}, (3, 1), Board(N), 0.1))
    act = brain.decide(obs)
    dest = (3, 3) if act.kind == "STAY" else _step((3, 3), act.direction)
    cop = brain.locator.best
    assert abs(dest[0] - cop[0]) + abs(dest[1] - cop[1]) >= 2


def _step(pos, d):
    dr, dc = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}[d]
    return (pos[0] + dr, pos[1] + dc)


def test_thief_action_is_always_legal_and_never_a_barrier():
    brain = AntiSqueezeBrain(make_rng(5), horizon=35, seed=5)
    for step in range(1, 12):
        act = brain.decide(_obs("thief", (3, 3), step=step, scent={(0, 0): 0.5}))
        assert act.kind in ("MOVE", "STAY")


# ------------------------------------------------------------------- factory
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
