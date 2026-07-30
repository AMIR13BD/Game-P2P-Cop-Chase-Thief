"""PoliceGreedyBrain: pursue the highest-belief cell via a shortest path.

Uses only legally visible data (own position, barriers, received thief scent)."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .fallback import safe_fallback
from .pathing import bfs_first_step


class PoliceGreedyBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        direction = bfs_first_step(board, obs.self_pos, target)
        if direction is None:
            return Action("STAY")
        return Action("MOVE", direction)

    def hint(self, obs: Observation) -> str:
        return "closing in near the avenue"
