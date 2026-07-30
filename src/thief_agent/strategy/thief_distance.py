"""ThiefDistanceBrain: move to maximize Manhattan distance from the police belief.

Uses only legally visible data (own position, barriers, received police scent)."""

from ..constants import DELTAS, ORTHO
from ..domain.board import Board
from ..domain.rules import legal_move_dirs
from .base import Action, BrainBase, Observation
from .belief import BeliefMap


def _manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class ThiefDistanceBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        threat = belief.argmax()
        if threat is None:
            return Action("STAY")
        best_dir, best_dist = "STAY", _manhattan(obs.self_pos, threat)
        for d in ORTHO:
            if d not in legal_move_dirs(obs.self_pos, board):
                continue
            dr, dc = DELTAS[d]
            cell = (obs.self_pos[0] + dr, obs.self_pos[1] + dc)
            dist = _manhattan(cell, threat)
            if dist > best_dist:
                best_dir, best_dist = d, dist
        return Action("STAY") if best_dir == "STAY" else Action("MOVE", best_dir)

    def hint(self, obs: Observation) -> str:
        return "slipping away past the park"
