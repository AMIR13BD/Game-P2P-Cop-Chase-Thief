"""Immutable physics vocabulary. Orthogonal movement only; diagonals never exist."""

from enum import StrEnum


class Role(StrEnum):
    POLICE = "police"
    THIEF = "thief"


# (row_delta, col_delta); row grows downward (south). Orthogonal + STAY only.
DELTAS: dict[str, tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1),
    "STAY": (0, 0),
}
ORTHO: tuple[str, ...] = ("N", "S", "E", "W")
LEGAL_TOKENS: tuple[str, ...] = ("N", "S", "E", "W", "STAY")
DIAGONALS: frozenset[str] = frozenset({"NE", "NW", "SE", "SW"})
BARRIER_TARGETS: tuple[str, ...] = ("SELF", "N", "S", "E", "W")


def complement(role: Role) -> Role:
    """The opposite role (used for six-sub-game alternation)."""
    return Role.THIEF if role is Role.POLICE else Role.POLICE
