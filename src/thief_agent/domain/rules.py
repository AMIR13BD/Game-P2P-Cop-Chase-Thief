"""Movement and barrier legality over a board. Pure functions; no LLM, no I/O."""

from ..constants import BARRIER_TARGETS, DELTAS, ORTHO
from .board import Board, Cell


def legal_move_dirs(pos: Cell, board: Board) -> list[str]:
    dirs = ["STAY"]
    for d in ORTHO:
        dr, dc = DELTAS[d]
        if board.passable((pos[0] + dr, pos[1] + dc)):
            dirs.append(d)
    return dirs


def step(pos: Cell, direction: str) -> Cell:
    dr, dc = DELTAS[direction]
    return (pos[0] + dr, pos[1] + dc)


def barrier_cell(pos: Cell, target: str) -> Cell:
    if target == "SELF":
        return pos
    return step(pos, target)


def legal_barrier_targets(pos: Cell, board: Board) -> list[str]:
    out: list[str] = []
    for t in BARRIER_TARGETS:
        cell = barrier_cell(pos, t)
        if board.in_bounds(cell) and cell not in board.barriers:
            out.append(t)
    return out


def is_move_legal(pos: Cell, direction: str, board: Board) -> bool:
    return direction in legal_move_dirs(pos, board)
