"""Baseline (tuning-set) opponents: greedy, random-walk, shortest-path, mobility.
Each handles either role, produces only legal actions, and is fully deterministic
given its seed."""

from ...domain.board import Board
from ...strategy.base import Action, BrainBase, Observation
from ...strategy.belief import BeliefMap
from ...strategy.fallback import safe_fallback
from ...strategy.moves import legal_steps, manhattan, move_away, move_toward


def _threat(obs: Observation, board: Board):
    belief = BeliefMap(board)
    belief.update(obs.scent)
    return belief.argmax()


class GreedyBrain(BrainBase):
    """Naive greedy: minimise/maximise Manhattan distance (ignores barrier detours)."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = _threat(obs, board)
        if target is None:
            return safe_fallback(obs, board)
        want_close = obs.role == "police"
        best, best_key = ("STAY", obs.self_pos), None
        for d, cell in legal_steps(obs, board):
            md = manhattan(cell, target)
            key = md if want_close else -md
            if best_key is None or key < best_key:
                best, best_key = (d, cell), key
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])


class RandomWalkBrain(BrainBase):
    """Uniform random legal move (seeded)."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        steps = legal_steps(obs, board)
        d, _ = steps[self.rng.randrange(len(steps))]
        return Action("STAY") if d == "STAY" else Action("MOVE", d)


class ShortestPathBrain(BrainBase):
    """BFS-optimal pursuit (Police) or flight (Thief) around barriers."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = _threat(obs, board)
        if target is None:
            return safe_fallback(obs, board)
        return (
            move_toward(obs, board, target)
            if obs.role == "police"
            else move_away(obs, board, target)
        )


class MobilityBrain(BrainBase):
    """Maximise own passable-neighbour count; break ties by role-appropriate distance."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = _threat(obs, board)
        want_close = obs.role == "police"

        def key(dc):
            cell = dc[1]
            mob = len(board.neighbors(cell))
            md = manhattan(cell, target) if target else 0
            return (mob, -md if want_close else md)

        best = max(legal_steps(obs, board), key=key)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])
