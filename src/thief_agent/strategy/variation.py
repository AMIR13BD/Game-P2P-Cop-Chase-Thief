"""Deterministic seeded micro-variation: a tiny tie-break bonus that diversifies
only strategically-equivalent choices across sub-games. Always < the objective
terms so it can never rescue a materially worse action. Seed 0 => no variation
(reproducible unit-test baseline). Never uses randomness or any hidden state."""

import hashlib

Cell = tuple[int, int]


def micro_variation(seed: int, step: int, cell: Cell, direction: str, scale: float = 0.45) -> float:
    """A stable pseudo-value in [0, scale) keyed by (seed, turn, cell, move)."""
    if not seed:
        return 0.0
    material = f"{seed}:{step}:{cell[0]}:{cell[1]}:{direction}".encode()
    value = int.from_bytes(hashlib.sha256(material).digest()[:4], "big")
    return (value / 0xFFFFFFFF) * scale
