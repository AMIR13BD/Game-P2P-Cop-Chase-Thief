"""Deterministic seeded RNG so runs are reproducible."""

import random


def make_rng(seed: int) -> random.Random:
    return random.Random(seed)
