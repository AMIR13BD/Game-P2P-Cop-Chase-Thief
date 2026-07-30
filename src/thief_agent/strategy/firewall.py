"""Legality firewall: validate a proposed action; substitute a legal fallback."""

from ..domain.rules import barrier_cell, is_move_legal, legal_barrier_targets
from .base import Action, Observation
from .fallback import safe_fallback


def is_legal(action: Action, obs: Observation, board, role: str) -> bool:
    if action.kind == "STAY":
        return True
    if action.kind == "MOVE":
        return action.direction in ("N", "S", "E", "W") and is_move_legal(
            obs.self_pos, action.direction, board
        )
    if action.kind == "BARRIER":
        if role != "police" or obs.barriers_used >= obs.max_barriers:
            return False
        if action.direction not in legal_barrier_targets(obs.self_pos, board):
            return False
        return board.in_bounds(barrier_cell(obs.self_pos, action.direction))
    return False


def enforce(action: Action, obs: Observation, board, role: str) -> tuple[Action, bool]:
    """Return (legal_action, substituted?). Never returns an illegal action."""
    if is_legal(action, obs, board, role):
        return action, False
    return safe_fallback(obs, board), True
