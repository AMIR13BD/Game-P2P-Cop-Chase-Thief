"""Free natural-language hint generation and consumption (P17).

Hints are strategy-linked: the generator encodes a real movement tendency
(truthful), hides it (vague), or inverts it (deceptive). `biased_target` shows the
receiving side genuinely acting on a hint -- but only when audited credibility makes
it trustworthy, so deceptive or unproven hints do not perturb pursuit."""

from ..domain.board import Board
from .belief import BeliefMap
from .hint_filter import DEFAULT_WORD_CAP, hint_direction, sanitize

_DIR_WORD = {"N": "north", "S": "south", "E": "east", "W": "west"}
_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
_VAGUE = (
    "weaving through the busy streets",
    "keeping to the shadows for now",
    "somewhere among the evening crowds",
    "taking the long way downtown",
)


class HintGenerator:
    """Produce a public-safe hint in truthful / vague / deceptive mode."""

    def __init__(self, rng, mode: str = "vague", cap: int = DEFAULT_WORD_CAP) -> None:
        self.rng = rng
        self.mode = mode
        self.cap = cap

    def generate(self, toward: str | None = None) -> str:
        if self.mode == "vague" or toward not in _DIR_WORD:
            return sanitize(self._vague(), self.cap)
        if self.mode == "deceptive":
            toward = _OPPOSITE[toward]
        return sanitize(f"heading {_DIR_WORD[toward]} toward the district", self.cap)

    def _vague(self) -> str:
        return _VAGUE[self.rng.randrange(len(_VAGUE))]


def biased_target(board: Board, scent: dict, hint, credibility: float):
    """Pursuit target after applying a hint, gated by audited credibility (>=0.5
    ignores; only a proven-honest hint shifts the target one cell in its direction)."""
    belief = BeliefMap(board)
    belief.update(scent)
    base = belief.argmax()
    delta = hint_direction(hint)
    if base is None or delta is None or credibility <= 0.5:
        return base
    cand = (base[0] + delta[0], base[1] + delta[1])
    return cand if board.passable(cand) else base
