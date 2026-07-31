"""Belief heatmap (P21): bucket the belief distribution (derived only from received
scent, via the same BeliefMap the strategies use) into 0-9 intensity cells."""

from ..domain.board import Board
from ..strategy.belief import BeliefMap
from .board_view import _norm_scent


def belief_buckets(size: int, scent, barriers=()) -> dict:
    """Map each cell to a 0-9 bucket proportional to its belief probability."""
    board = Board(size, {tuple(b) for b in barriers})
    belief = BeliefMap(board)
    belief.update(_norm_scent(scent))
    peak = max(belief.dist.values()) if belief.dist else 0.0
    if peak <= 0:
        return {}
    return {cell: min(9, int(round(9 * p / peak))) for cell, p in belief.dist.items()}


def render_heatmap(size: int, scent, barriers=()) -> str:
    buckets = belief_buckets(size, scent, barriers)
    bset = {tuple(b) for b in barriers}
    rows = []
    for r in range(size):
        rows.append(
            " ".join("#" if (r, c) in bset else str(buckets.get((r, c), 0)) for c in range(size))
        )
    return "\n".join(rows)
