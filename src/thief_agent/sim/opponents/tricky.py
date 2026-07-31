"""Held-out opponents (not used during tuning): corner/trap, barrier-heavy, and
deceptive/unpredictable. Each handles either role and stays legal by construction."""

from ...domain.board import Board
from ...domain.rules import barrier_cell, legal_barrier_targets
from ...strategy.base import Action, BrainBase, Observation
from ...strategy.belief import BeliefMap
from ...strategy.fallback import safe_fallback
from ...strategy.hints import HintGenerator
from ...strategy.moves import legal_steps, manhattan, move_away, move_toward


def _threat(obs: Observation, board: Board):
    belief = BeliefMap(board)
    belief.update(obs.scent)
    return belief.argmax()


def _nearest_corner(board: Board, cell) -> tuple:
    n = board.size - 1
    corners = [(0, 0), (0, n), (n, 0), (n, n)]
    return min(corners, key=lambda c: manhattan(c, cell))


class CornerTrapBrain(BrainBase):
    """Police herds toward a corner near the belief; Thief hides in a corner."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = _threat(obs, board)
        if obs.role == "police":
            aim = _nearest_corner(board, target) if target else _nearest_corner(board, obs.self_pos)
            return move_toward(obs, board, aim)
        return move_toward(obs, board, _nearest_corner(board, obs.self_pos))


class BarrierHeavyBrain(BrainBase):
    """Police spends barriers aggressively; Thief just flees (cannot wall)."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = _threat(obs, board)
        if obs.role == "police" and obs.barriers_used < obs.max_barriers:
            for t in legal_barrier_targets(obs.self_pos, board):
                if barrier_cell(obs.self_pos, t) != obs.self_pos:
                    return Action("BARRIER", t)
        if target is None:
            return safe_fallback(obs, board)
        return (
            move_toward(obs, board, target)
            if obs.role == "police"
            else move_away(obs, board, target)
        )


class DeceptiveBrain(BrainBase):
    """Unpredictable movement (seeded) plus misleading hints."""

    def __init__(self, rng, honesty: float = 0.3) -> None:
        super().__init__(rng)
        self.honesty = honesty
        self._hints = HintGenerator(rng, mode="deceptive")

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        steps = legal_steps(obs, board)
        if self.rng.random() < self.honesty:
            target = _threat(obs, board)
            if target is not None:
                return (
                    move_toward(obs, board, target)
                    if obs.role == "police"
                    else move_away(obs, board, target)
                )
        d, _ = steps[self.rng.randrange(len(steps))]
        return Action("STAY") if d == "STAY" else Action("MOVE", d)

    def hint(self, obs: Observation) -> str:
        return self._hints.generate(toward="N")
