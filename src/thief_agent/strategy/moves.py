"""Movement-selection helpers shared by every strategy. All return legal actions
(or directions that map to legal moves); the legality firewall remains the final
safety net. Deterministic tie-breaking keeps runs reproducible."""

from ..constants import DELTAS, ORTHO
from ..domain.board import Board, Cell
from ..domain.rules import legal_move_dirs
from .base import Action, Observation
from .graph import distance_map


def legal_steps(obs: Observation, board: Board) -> list[tuple[str, Cell]]:
    """(direction, resulting_cell) for every legal move, STAY first."""
    out: list[tuple[str, Cell]] = [("STAY", obs.self_pos)]
    for d in ORTHO:
        if d in legal_move_dirs(obs.self_pos, board):
            dr, dc = DELTAS[d]
            out.append((d, (obs.self_pos[0] + dr, obs.self_pos[1] + dc)))
    return out


def _dist_to(board: Board, target: Cell) -> dict[Cell, int]:
    return distance_map(board, target)


def move_toward(obs: Observation, board: Board, target: Cell) -> Action:
    """Legal move minimising BFS distance to target (ties: N,S,E,W order)."""
    dist = _dist_to(board, target)
    big = board.size * board.size + 1
    best: tuple[str, Cell] = ("STAY", obs.self_pos)
    best_d = dist.get(obs.self_pos, big)
    for d, cell in legal_steps(obs, board):
        if dist.get(cell, big) < best_d:
            best, best_d = (d, cell), dist.get(cell, big)
    return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])


def move_away(obs: Observation, board: Board, threat: Cell) -> Action:
    """Legal move maximising BFS distance from threat (ties keep the larger step)."""
    dist = _dist_to(board, threat)
    best: tuple[str, Cell] = ("STAY", obs.self_pos)
    best_d = dist.get(obs.self_pos, -1)
    for d, cell in legal_steps(obs, board):
        cd = dist.get(cell, -1)
        if cd > best_d:
            best, best_d = (d, cell), cd
    return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])


def manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
