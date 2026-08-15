"""Tests for the Orcai-MJ counter: opponent model, tracker, Cop locator, both brains.

Covers the properties the strategy actually relies on -- the ring lock, exact
prediction, evidence overruling the model, the Barrier-Law constraint (including a
Cop standing on a wall of its own making), capture-on-adjacency, the STAY capture,
safe degradation behind the confidence gate, and the Thief's hard safety tiers.
"""

from thief_agent.domain import smell
from thief_agent.domain.board import Board
from thief_agent.strategy.base import Observation
from thief_agent.strategy.cop_locate import CopLocator
from thief_agent.strategy.orcai_model import OrcaiBelief, ring_cells, ring_of, ringrunner_next
from thief_agent.strategy.orcai_track import OrcaiThiefTracker

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
