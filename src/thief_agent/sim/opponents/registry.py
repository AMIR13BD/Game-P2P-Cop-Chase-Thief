"""Opponent registry with an explicit tuning / held-out split. Champion selection
must validate on the held-out set (never used during tuning) to avoid overfitting."""

from .reference import ReferenceBrain
from .simple import GreedyBrain, MobilityBrain, RandomWalkBrain, ShortestPathBrain
from .tricky import BarrierHeavyBrain, CornerTrapBrain, DeceptiveBrain

# Seen during tuning/self-play.
TUNING_OPPONENTS = {
    "greedy": GreedyBrain,
    "random": RandomWalkBrain,
    "shortest": ShortestPathBrain,
    "mobility": MobilityBrain,
}

# Reserved for final validation only.
HELD_OUT_OPPONENTS = {
    "corner_trap": CornerTrapBrain,
    "barrier_heavy": BarrierHeavyBrain,
    "deceptive": DeceptiveBrain,
    "reference": ReferenceBrain,
}


def all_opponents() -> dict:
    return {**TUNING_OPPONENTS, **HELD_OUT_OPPONENTS}


def make_opponent(name: str, rng):
    return all_opponents()[name](rng)
