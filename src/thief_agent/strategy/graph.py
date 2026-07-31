"""Graph analysis over the passable board: BFS distance maps, reachable sets and
areas, and connected components. Pure and deterministic; shared by both roles."""

from collections import deque

from ..domain.board import Board, Cell


def distance_map(board: Board, start: Cell) -> dict[Cell, int]:
    """BFS hop-distance from `start` to every reachable passable cell."""
    dist: dict[Cell, int] = {start: 0}
    q: deque[Cell] = deque([start])
    while q:
        cur = q.popleft()
        for nxt in board.neighbors(cur):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    return dist


def reachable_set(board: Board, start: Cell, max_steps: int) -> set[Cell]:
    """Cells reachable from `start` within `max_steps` orthogonal moves."""
    return {c for c, d in distance_map(board, start).items() if d <= max_steps}


def reachable_area(board: Board, start: Cell) -> int:
    """Size of `start`'s connected component (number of reachable cells)."""
    return len(distance_map(board, start))


def component_of(board: Board, start: Cell) -> set[Cell]:
    """The full connected component containing `start`."""
    return set(distance_map(board, start))


def connected_components(board: Board) -> list[set[Cell]]:
    """Every connected component of passable cells (deterministic order)."""
    seen: set[Cell] = set()
    comps: list[set[Cell]] = []
    for cell in board.all_cells():
        if cell in board.barriers or cell in seen:
            continue
        comp = component_of(board, cell)
        seen |= comp
        comps.append(comp)
    return comps


def largest_component(board: Board) -> set[Cell]:
    """The biggest passable component, or an empty set if the board is full."""
    comps = connected_components(board)
    return max(comps, key=len) if comps else set()
