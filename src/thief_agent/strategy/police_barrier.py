"""Police barrier planning: cut/trap placement that shrinks the Thief's reachable
area or seals an escape, subject to self-obstruction avoidance and a tempo cost.

`best_barrier` returns a legal BARRIER Action or None (meaning: prefer to move)."""

from ..domain.board import Board
from ..domain.rules import barrier_cell, legal_barrier_targets
from .base import Action, BrainBase, Observation
from .connectivity import articulation_points
from .fallback import safe_fallback
from .graph import distance_map, reachable_area
from .moves import move_toward

TEMPO_COST = 1  # a barrier costs a tempo; only place when it buys more than that


def _thief_area(board: Board, barrier, target) -> int:
    trial = Board(board.size, board.barriers | {barrier})
    if not trial.passable(target):
        return -1  # barrier lands on the belief cell = an immediate seal candidate
    return reachable_area(trial, target)


def best_barrier(obs: Observation, board: Board, target) -> Action | None:
    """Pick the barrier that most reduces Thief reachable area, if worth the tempo."""
    if obs.role != "police" or obs.barriers_used >= obs.max_barriers or target is None:
        return None
    base_area = reachable_area(board, target)
    cut = articulation_points(board)
    best_t, best_gain = None, TEMPO_COST
    for t in legal_barrier_targets(obs.self_pos, board):
        cell = barrier_cell(obs.self_pos, t)
        if cell == obs.self_pos:
            continue  # never wall our own cell
        area = _thief_area(board, cell, target)
        if area < 0:
            return Action("BARRIER", t)  # seals the belief cell outright
        gain = (base_area - area) + (2 if cell in cut else 0)
        trial = Board(board.size, board.barriers | {cell})
        if distance_map(trial, target).get(obs.self_pos) is None:
            continue  # self-obstruction: we could no longer reach the target
        if gain > best_gain:
            best_t, best_gain = t, gain
    return Action("BARRIER", best_t) if best_t else None


class BarrierBrain(BrainBase):
    """Cut/trap-focused Police: place value-positive barriers, else chase."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        from .belief import BeliefMap

        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        bar = best_barrier(obs, board, target)
        return bar if bar is not None else move_toward(obs, board, target)

    def hint(self, obs: Observation) -> str:
        return "setting up a roadblock ahead"
