"""Guaranteed legal fallback action (deterministic ordering)."""

from ..domain.rules import legal_move_dirs
from .base import Action, Observation


def safe_fallback(obs: Observation, board) -> Action:
    """Always returns a legal action: prefer a real move, else STAY."""
    dirs = legal_move_dirs(obs.self_pos, board)
    for d in ("N", "S", "E", "W"):
        if d in dirs:
            return Action("MOVE", d)
    return Action("STAY")
