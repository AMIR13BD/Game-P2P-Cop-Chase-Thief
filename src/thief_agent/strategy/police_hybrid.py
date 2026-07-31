"""PoliceHybridBrain: a single strong Police policy that composes the portfolio --
endgame capture, tempo-aware cut/trap barriers, herding when the Thief has space,
and shortest-path interception otherwise -- with risk-sensitivity near the limit.

The adaptive meta-controller (P16) chooses *between* whole brains; this brain is the
default aggressive choice and also composes cleanly inside that controller."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .fallback import safe_fallback
from .graph import reachable_area
from .moves import legal_steps
from .police_barrier import best_barrier
from .police_herding import HerdBrain
from .police_intercept import InterceptBrain

RISK_WINDOW = 5  # within this many turns of the limit, stop spending tempo on walls


class PoliceHybridBrain(BrainBase):
    def __init__(self, rng, horizon: int = 35) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self._intercept = InterceptBrain(rng)
        self._herd = HerdBrain(rng)

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        for d, cell in legal_steps(obs, board):  # endgame: capture if reachable now
            if cell == target and d != "STAY":
                return Action("MOVE", d)
        remaining = self.horizon - obs.step
        if remaining > RISK_WINDOW:  # early/mid game: barriers are worth the tempo
            bar = best_barrier(obs, board, target)
            if bar is not None:
                return bar
        if reachable_area(board, target) > (board.size * board.size) // 2:
            return self._herd.decide(obs)  # lots of open space -> compress it
        return self._intercept.decide(obs)  # cornered space -> intercept directly

    def hint(self, obs: Observation) -> str:
        return "coordinating units to close the net"
