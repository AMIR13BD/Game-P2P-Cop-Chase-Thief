"""Named strategy portfolio: brain factories keyed by role. Used by the adaptive
meta-controller (P16) for selection and by the evaluation harness (P12) for
round-robin comparison. A single source of truth avoids duplicated wiring."""

from .police_barrier import BarrierBrain
from .police_greedy import PoliceGreedyBrain
from .police_herding import HerdBrain
from .police_hybrid import PoliceHybridBrain
from .police_intercept import InterceptBrain
from .thief_distance import ThiefDistanceBrain
from .thief_endgame import EndgameBrain
from .thief_entropy import EntropyBrain
from .thief_escape import EscapeBrain
from .thief_evade import EvadeBrain
from .thief_hybrid import ThiefHybridBrain

POLICE_PORTFOLIO = {
    "greedy": PoliceGreedyBrain,
    "intercept": InterceptBrain,
    "barrier": BarrierBrain,
    "herd": HerdBrain,
    "hybrid": PoliceHybridBrain,
}
THIEF_PORTFOLIO = {
    "distance": ThiefDistanceBrain,
    "escape": EscapeBrain,
    "evade": EvadeBrain,
    "entropy": EntropyBrain,
    "endgame": EndgameBrain,
    "hybrid": ThiefHybridBrain,
}


def portfolio(role: str) -> dict:
    return POLICE_PORTFOLIO if role == "police" else THIEF_PORTFOLIO


def make_brain(role: str, name: str, rng):
    return portfolio(role)[name](rng)
