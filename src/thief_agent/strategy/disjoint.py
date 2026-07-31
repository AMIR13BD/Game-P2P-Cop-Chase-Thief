"""Vertex-disjoint path counting via max-flow on a vertex-split graph (Menger's
theorem). Used by the Thief to preserve multiple escape routes and by the Police
to reason about destroying them. Pure and deterministic."""

from collections import defaultdict, deque

from ..domain.board import Board, Cell

INF = 10**9


def _max_flow(cap: dict, src, sink) -> int:
    """Edmonds-Karp: repeated BFS augmenting paths on the residual graph."""
    flow = 0
    while True:
        parent = {src: None}
        q = deque([src])
        while q:
            u = q.popleft()
            if u == sink:
                break
            for v, c in cap[u].items():
                if c > 0 and v not in parent:
                    parent[v] = u
                    q.append(v)
        if sink not in parent:
            return flow
        v = sink
        while parent[v] is not None:
            u = parent[v]
            cap[u][v] -= 1
            cap[v][u] += 1
            v = u
        flow += 1


def vertex_disjoint_paths(board: Board, source: Cell, targets) -> int:
    """Max number of internally vertex-disjoint paths from source to any target."""
    goal = {t for t in targets if t != source and board.passable(t)}
    if not goal or not board.passable(source):
        return 0
    cap: dict = defaultdict(lambda: defaultdict(int))
    for cell in board.all_cells():
        if cell in board.barriers:
            continue
        vin, vout = (cell, 0), (cell, 1)
        cap[vin][vout] += INF if cell == source else 1
        for nb in board.neighbors(cell):
            cap[vout][(nb, 0)] += 1
    sink = "SINK"
    for t in goal:
        cap[(t, 1)][sink] += INF
    return _max_flow(cap, (source, 1), sink)


def edge_cells(board: Board) -> set[Cell]:
    """Perimeter cells of the board (natural escape frontier for the Thief)."""
    n = board.size
    return {(r, c) for r in range(n) for c in range(n) if r in (0, n - 1) or c in (0, n - 1)}
