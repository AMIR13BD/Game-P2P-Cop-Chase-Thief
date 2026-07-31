"""EndgameBrain: near the move limit, choose the move that maximises simulated
survival depth against a modelled greedy pursuer (located from belief only). Uses
the anytime deepening search so it stays within a decision-time budget."""

from ..domain.board import Board, Cell
from ..domain.rules import step as step_move
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .moves import legal_steps
from .pathing import bfs_first_step
from .search import deepening_best


def _survives(board: Board, thief: Cell, pursuer: Cell, depth: int) -> int:
    """Simulate `depth` alternating turns; return steps survived (higher = safer)."""
    for t in range(1, depth + 1):
        d = bfs_first_step(board, pursuer, thief)
        pursuer = step_move(pursuer, d) if d else pursuer
        if pursuer == thief:
            return t - 1
        nbrs = board.neighbors(thief)
        if not nbrs:
            return t - 1
        thief = max(nbrs, key=lambda c: (abs(c[0] - pursuer[0]) + abs(c[1] - pursuer[1]), c))
    return depth


class EndgameBrain(BrainBase):
    def __init__(self, rng, max_depth: int = 6, deadline_s: float = 0.03) -> None:
        super().__init__(rng)
        self.max_depth = max_depth
        self.deadline_s = deadline_s

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        pursuer = belief.argmax()
        steps = legal_steps(obs, board)
        if pursuer is None:
            return Action("STAY") if steps[0][0] == "STAY" and len(steps) == 1 else _pick(steps)
        best = deepening_best(
            steps,
            lambda dc, depth: _survives(board, dc[1], pursuer, depth),
            self.max_depth,
            self.deadline_s,
        )
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "holding out until the clock runs down"


def _pick(steps) -> Action:
    move = next((s for s in steps if s[0] != "STAY"), steps[0])
    return Action("STAY") if move[0] == "STAY" else Action("MOVE", move[0])
