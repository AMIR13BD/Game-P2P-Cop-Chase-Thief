"""Opponent-motion prediction from legally-visible data only (received scent and
the shared board). No hidden opponent position is ever consulted."""

from ..domain.board import Board, Cell
from .belief import BeliefMap
from .graph import reachable_set
from .pathing import bfs_first_step


def belief_targets(board: Board, scent: dict, top: int = 3) -> list[Cell]:
    """Highest-probability opponent cells inferred from received scent."""
    belief = BeliefMap(board)
    belief.update(scent)
    ranked = sorted(belief.dist.items(), key=lambda kv: (-kv[1], kv[0]))
    return [cell for cell, _ in ranked[:top]]


def scent_peak(scent: dict) -> Cell | None:
    """The most intense received-scent cell (proxy for a recent opponent visit)."""
    if not scent:
        return None
    return max(scent.items(), key=lambda kv: (kv[1], kv[0]))[0]


def future_reach(board: Board, origins, k: int) -> set[Cell]:
    """Union of cells reachable within k steps from any predicted origin cell."""
    out: set[Cell] = set()
    for origin in origins:
        out |= reachable_set(board, origin, k)
    return out


def predict_pursuer_step(board: Board, pursuer: Cell, prey_belief: Cell) -> Cell:
    """Assume a greedy pursuer: where it moves next when chasing `prey_belief`."""
    direction = bfs_first_step(board, pursuer, prey_belief)
    if direction is None:
        return pursuer
    from ..domain.rules import step as step_move

    nxt = step_move(pursuer, direction)
    return nxt if board.passable(nxt) else pursuer
