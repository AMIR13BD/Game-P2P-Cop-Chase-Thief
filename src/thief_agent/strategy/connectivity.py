"""Connectivity structure of the passable board: articulation points and bridges
via a single iterative DFS (Tarjan low-link). Used for cut/trap planning (Police)
and articulation avoidance (Thief). Pure and deterministic."""

from ..domain.board import Board, Cell


def _dfs_order(board: Board, root: Cell) -> tuple[dict, dict, dict]:
    """Iterative DFS from root; returns discovery times, low-links, parent map."""
    disc: dict[Cell, int] = {}
    low: dict[Cell, int] = {}
    parent: dict[Cell, Cell | None] = {root: None}
    stack: list[tuple[Cell, int]] = [(root, 0)]
    timer = 0
    while stack:
        node, idx = stack.pop()
        nbrs = board.neighbors(node)
        if idx == 0:
            disc[node] = low[node] = timer
            timer += 1
        if idx < len(nbrs):
            stack.append((node, idx + 1))
            nxt = nbrs[idx]
            if nxt not in disc:
                parent[nxt] = node
                stack.append((nxt, 0))
            elif nxt != parent.get(node):
                low[node] = min(low[node], disc[nxt])
        else:
            p = parent.get(node)
            if p is not None:
                low[p] = min(low[p], low[node])
    return disc, low, parent


def articulation_points(board: Board) -> set[Cell]:
    """Cells whose removal disconnects their component (over all components)."""
    cut: set[Cell] = set()
    seen: set[Cell] = set()
    for start in board.all_cells():
        if start in board.barriers or start in seen:
            continue
        disc, low, parent = _dfs_order(board, start)
        seen |= set(disc)
        children = sum(1 for c, p in parent.items() if p == start)
        if children > 1:
            cut.add(start)
        for node, p in parent.items():
            if p is None or p == start:
                continue
            if low[node] >= disc[p]:
                cut.add(p)
    return cut


def bridges(board: Board) -> set[frozenset[Cell]]:
    """Edges whose removal disconnects the graph (as frozenset {u, v})."""
    out: set[frozenset[Cell]] = set()
    seen: set[Cell] = set()
    for start in board.all_cells():
        if start in board.barriers or start in seen:
            continue
        disc, low, parent = _dfs_order(board, start)
        seen |= set(disc)
        for node, p in parent.items():
            if p is not None and low[node] > disc[p]:
                out.add(frozenset((node, p)))
    return out
