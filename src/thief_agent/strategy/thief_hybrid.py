"""ThiefHybridBrain: composes the Thief portfolio -- endgame survival search near
the limit, trap-avoiding evasion when geometry is dangerous, distance-preserving
escape when the pursuer is close, and entropy-preserving ambiguity otherwise."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .connectivity import articulation_points
from .moves import manhattan
from .thief_endgame import EndgameBrain
from .thief_entropy import EntropyBrain
from .thief_escape import EscapeBrain
from .thief_evade import EvadeBrain

CLOSE = 2  # pursuer within this many cells is treated as an immediate threat
ENDGAME_WINDOW = 6  # within this many turns of the limit, switch to survival search


class ThiefHybridBrain(BrainBase):
    def __init__(self, rng, horizon: int = 35) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self._endgame = EndgameBrain(rng)
        self._evade = EvadeBrain(rng)
        self._escape = EscapeBrain(rng)
        self._entropy = EntropyBrain(rng)

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        threat = belief.argmax()
        if self.horizon - obs.step <= ENDGAME_WINDOW:
            return self._endgame.decide(obs)
        if obs.self_pos in articulation_points(board):
            return self._evade.decide(obs)  # sitting on a self-trap -> get off it
        if threat is not None and manhattan(obs.self_pos, threat) <= CLOSE:
            return self._escape.decide(obs)  # pursuer is close -> maximise distance
        return self._entropy.decide(obs)  # safe -> stay ambiguous

    def hint(self, obs: Observation) -> str:
        return "blending into the evening traffic"
