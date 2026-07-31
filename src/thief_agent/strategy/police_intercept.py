"""InterceptBrain: pursue the Thief's *predicted future* position, not just its
current belief cell. Falls back to exact shortest-path pursuit when no useful
prediction exists. Uses only received scent (never a hidden Thief position)."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .fallback import safe_fallback
from .graph import reachable_area
from .moves import move_toward
from .predict import belief_targets


class InterceptBrain(BrainBase):
    def __init__(self, rng, horizon: int = 2) -> None:
        super().__init__(rng)
        self.horizon = horizon

    def _intercept_cell(self, board: Board, target):
        """Predict the Thief flees to its largest-area neighbour; aim to cut it off."""
        best, best_area = target, -1
        for nb in board.neighbors(target):
            area = reachable_area(Board(board.size, board.barriers), nb)
            if area > best_area:
                best, best_area = nb, area
        return best

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        # If we can already reach the belief cell, close on it directly (endgame).
        if obs.self_pos in board.neighbors(target) or obs.self_pos == target:
            return move_toward(obs, board, target)
        aim = self._intercept_cell(board, target)
        act = move_toward(obs, board, aim)
        if act.kind == "STAY":  # interception blocked; revert to direct pursuit
            act = move_toward(obs, board, target)
        return act

    def hint(self, obs: Observation) -> str:
        return "cutting off the next junction"


def top_belief_cells(obs: Observation) -> list:
    """Convenience: the Police's ranked belief cells (used by the meta-controller)."""
    board = Board(obs.board_size, set(obs.barriers))
    return belief_targets(board, obs.scent, top=3)
