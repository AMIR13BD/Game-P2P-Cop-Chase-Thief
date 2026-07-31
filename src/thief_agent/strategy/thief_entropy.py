"""EntropyBrain: keep the Police belief distribution spread out (hard to localise)
using controlled, seeded randomisation among near-optimal escape moves. This yields
ambiguous movement histories and manipulates the adversary's belief mass -- without
ever revealing a true position. Reproducible for a fixed seed."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .graph import distance_map, reachable_area
from .moves import legal_steps

TOLERANCE = 1  # moves within this distance of the best are treated as equivalent


class EntropyBrain(BrainBase):
    def __init__(self, rng, epsilon: float = 0.3) -> None:
        super().__init__(rng)
        self.epsilon = epsilon

    def _ranked(self, obs: Observation, board: Board):
        belief = BeliefMap(board)
        belief.update(obs.scent)
        threat = belief.argmax()
        dist = distance_map(board, threat) if threat is not None else {}
        steps = legal_steps(obs, board)
        scored = [((dist.get(c, 0), reachable_area(board, c)), (d, c)) for d, c in steps]
        scored.sort(key=lambda sc: sc[0], reverse=True)
        return scored

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        scored = self._ranked(obs, board)
        best_dist = scored[0][0][0]
        pool = [step for (val, step) in scored if best_dist - val[0] <= TOLERANCE]
        # controlled randomisation: seeded choice among near-optimal moves
        choice = pool[self.rng.randrange(len(pool))] if self.epsilon > 0 else scored[0][1]
        return Action("STAY") if choice[0] == "STAY" else Action("MOVE", choice[0])

    def hint(self, obs: Observation) -> str:
        return "doubling back through side streets"
