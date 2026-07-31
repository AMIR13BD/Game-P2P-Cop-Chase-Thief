"""HerdBrain: drive the Thief toward low-mobility regions (corners / bottlenecks)
rather than chasing directly, shrinking its escape space over time. Includes the
endgame rule: when adjacent to the belief cell, step onto it to capture."""

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .fallback import safe_fallback
from .graph import reachable_area
from .moves import legal_steps, manhattan, move_toward


def _corner_pressure(board: Board, cell: Cell) -> int:
    """How boxed-in `cell` is: fewer passable neighbours = higher pressure."""
    return 4 - len(board.neighbors(cell))


def herd_target(board: Board, thief_cell: Cell) -> Cell:
    """The neighbour of the Thief cell with the smallest reachable area: the
    direction we want to compress it toward (a corner or a bottleneck)."""
    best, best_area = thief_cell, reachable_area(board, thief_cell)
    for nb in board.neighbors(thief_cell):
        area = reachable_area(board, nb) - _corner_pressure(board, nb)
        if area < best_area:
            best, best_area = nb, area
    return best


class HerdBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        # Endgame: if we can land on the belief cell this turn, do it.
        for d, cell in legal_steps(obs, board):
            if cell == target and d != "STAY":
                return Action("MOVE", d)
        # Otherwise approach the cell that compresses the Thief's space.
        approach = herd_target(board, target)
        act = move_toward(obs, board, approach)
        if act.kind == "STAY" and manhattan(obs.self_pos, target) > 0:
            act = move_toward(obs, board, target)
        return act

    def hint(self, obs: Observation) -> str:
        return "pushing them toward the dead end"
