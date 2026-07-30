"""Shortest-path helper (BFS) over passable cells; returns the first step direction."""

from collections import deque

from ..constants import DELTAS, ORTHO
from ..domain.board import Board, Cell


def bfs_first_step(board: Board, start: Cell, goal: Cell) -> str | None:
    """Direction (N/S/E/W) of the first step on a shortest path start->goal, or None."""
    if start == goal:
        return None
    prev: dict[Cell, Cell] = {start: start}
    q: deque[Cell] = deque([start])
    while q:
        cur = q.popleft()
        for nxt in board.neighbors(cur):
            if nxt in prev:
                continue
            prev[nxt] = cur
            if nxt == goal:
                return _dir_from(start, _first_hop(prev, start, goal))
            q.append(nxt)
    return None


def _first_hop(prev: dict[Cell, Cell], start: Cell, goal: Cell) -> Cell:
    node = goal
    while prev[node] != start:
        node = prev[node]
    return node


def _dir_from(a: Cell, b: Cell) -> str | None:
    for d in ORTHO:
        dr, dc = DELTAS[d]
        if (a[0] + dr, a[1] + dc) == b:
            return d
    return None
