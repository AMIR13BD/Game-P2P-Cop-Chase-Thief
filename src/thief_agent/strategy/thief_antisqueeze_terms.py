"""Tuning constants and the wall-threat geometry for ``AntiSqueezeBrain``.

Split out of ``thief_antisqueeze.py`` purely to keep each module inside the repository's
150-line ceiling. Values and behaviour are unchanged -- the brain imports these names and
uses them exactly as before.
"""

from ..domain.board import Board, Cell

DIST_CAP = 8

DEFAULT_WEIGHTS = {
    "seal": 4.0,  # worst-case area after the Cop's best single wall (primary)
    "area": 1.0,  # area right now, Cop treated as blocked
    "exits": 6.0,  # neighbours that are themselves out of pounce range
    "routes": 3.0,  # vertex-disjoint escape routes to the frontier
    "degree": 2.0,  # open neighbours
    "artic": 8.0,  # penalty: standing on a cut vertex
    "corner": 3.0,  # penalty: corner proximity while walls remain
    "dist": 2.0,  # mild tie-break only -- never the objective
    "revisit": 4.0,
    "recent": 10.0,
    "stay": 6.0,
}


def cop_wall_targets(board: Board, cops: set[Cell]) -> set[Cell]:
    """Every cell the Cop could legally wall next turn (its own cell or one beside it)."""
    out: set[Cell] = set()
    for c in cops:
        if board.in_bounds(c) and c not in board.barriers:
            out.add(c)
        for n in board.neighbors(c):
            out.add(n)
    return out
