"""Capture predicates: landing, barrier-on-thief, and trapped-thief."""

from ..constants import DELTAS, ORTHO
from .board import Board, Cell


def captured_by_landing(police_pos: Cell, thief_pos: Cell) -> bool:
    return police_pos == thief_pos


def barrier_captures(barrier: Cell, thief_pos: Cell) -> bool:
    return barrier == thief_pos


def thief_trapped(thief_pos: Cell, board: Board) -> bool:
    """True when every orthogonal neighbor is impassable (barrier and/or edge)."""
    for d in ORTHO:
        dr, dc = DELTAS[d]
        if board.passable((thief_pos[0] + dr, thief_pos[1] + dc)):
            return False
    return True
