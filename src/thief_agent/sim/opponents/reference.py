"""Reference-style opponent: a competent, balanced baseline (shortest-path pursuit
with an occasional close-range barrier for Police; distance + mobility for Thief).

Deliberately distinct from and simpler than the championship portfolio -- it is the
'reference-baseline adapter' used to sanity-check that our agents actually improve."""

from ...domain.board import Board
from ...domain.rules import barrier_cell, legal_barrier_targets
from ...strategy.base import Action, BrainBase, Observation
from ...strategy.belief import BeliefMap
from ...strategy.fallback import safe_fallback
from ...strategy.moves import legal_steps, manhattan, move_toward


class ReferenceBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        if obs.role == "police":
            if manhattan(obs.self_pos, target) <= 2 and obs.barriers_used < obs.max_barriers:
                for t in legal_barrier_targets(obs.self_pos, board):
                    if barrier_cell(obs.self_pos, t) != obs.self_pos:
                        return Action("BARRIER", t)
            return move_toward(obs, board, target)
        # Thief: maximise distance, breaking ties by mobility.
        best, best_key = ("STAY", obs.self_pos), None
        for d, cell in legal_steps(obs, board):
            key = (manhattan(cell, target), len(board.neighbors(cell)))
            if best_key is None or key > best_key:
                best, best_key = (d, cell), key
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "patrolling the usual routes"
