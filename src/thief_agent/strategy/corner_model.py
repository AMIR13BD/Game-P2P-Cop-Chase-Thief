"""Forward model of a CORNER-RUNNING evader, plus the score that decides whether to
trust it.

Some Thieves do not evade in the plane at all: they pick the board corner furthest from
the Cop's last DECLARED cell and walk the shortest path to it. That policy is a pure
function of things the protocol already puts on the wire -- the public barrier set, the
Thief's own broadcast scent (whose peak is its cell), and OUR OWN capture-claim, which we
choose. Nothing secret is read, and no simulator shortcut is taken; this is the same
"model the opponent from public data" construction ``orcai_model`` already uses.

Modelling matters because capture needs a NEXT cell, not a current one. Rounds are
thief-first, so by the time we move, their move is already made: stepping onto where they
ARE can never catch an equal-speed evader, while stepping onto where they will BE does.

``CornerRunnerTracker`` is the safety valve, and it grades the only thing that matters --
whether last turn's PREDICTION came true. A model that stops describing the opponent
stops being trusted, and the caller keeps its previous behaviour unchanged. Localisation
accuracy is deliberately NOT used as the score: knowing where someone stands says nothing
about knowing where they are going, and conflating the two is what lets a wrong model
drive a whole match.
"""

from collections import deque

# Orthogonal steps in the tie-break order a shortest-path evader conventionally applies.
ORDER = (("N", (-1, 0)), ("S", (1, 0)), ("E", (0, 1)), ("W", (0, -1)))


def corners(size: int) -> tuple:
    edge = size - 1
    return ((0, 0), (0, edge), (edge, 0), (edge, edge))


def _distances(size: int, barriers: frozenset, target: tuple) -> dict:
    """BFS distance from every reachable cell to ``target`` over the passable board."""
    if not (0 <= target[0] < size and 0 <= target[1] < size) or target in barriers:
        return {}
    seen = {target: 0}
    pending = deque([target])
    while pending:
        cell = pending.popleft()
        for _, (dr, dc) in ORDER:
            nxt = (cell[0] + dr, cell[1] + dc)
            inside = 0 <= nxt[0] < size and 0 <= nxt[1] < size
            if inside and nxt not in barriers and nxt not in seen:
                seen[nxt] = seen[cell] + 1
                pending.append(nxt)
    return seen


def corner_target(size: int, barriers: frozenset, threat: tuple) -> tuple | None:
    """The corner such an evader heads for: furthest from ``threat`` by Manhattan."""
    legal = [cell for cell in corners(size) if cell not in barriers]
    if not legal:
        return None
    return max(
        legal,
        key=lambda c: (abs(c[0] - threat[0]) + abs(c[1] - threat[1]), c[0], c[1]),
    )


def corner_next(size: int, barriers: frozenset, pos: tuple, threat: tuple) -> tuple:
    """Where a corner-runner standing on ``pos`` moves once it has seen ``threat``."""
    target = corner_target(size, barriers, threat)
    if target is None or pos == target:
        return pos
    distance = _distances(size, barriers, target)
    options = []
    for _, (dr, dc) in ORDER:
        nxt = (pos[0] + dr, pos[1] + dc)
        inside = 0 <= nxt[0] < size and 0 <= nxt[1] < size
        if inside and nxt not in barriers and nxt in distance:
            options.append((nxt, distance[nxt]))
    if not options:
        return pos
    shortest = min(step for _, step in options)
    for nxt, step in options:  # ORDER is already the tie-break order
        if step == shortest:
            return nxt
    return pos


class CornerRunnerTracker:
    """Rolling agreement score for the corner-runner model's NEXT-cell prediction.

    ``commit`` records the cell we are betting the opponent will occupy; ``observe``
    grades that bet against the cell they turned out to occupy. ``trusted`` stays False
    until enough graded predictions exist, so a brain never switches policy on a guess.
    """

    def __init__(self, size: int, window: int = 6, gate: float = 0.75, minimum: int = 3):
        self.size = size
        self.gate = gate
        self.minimum = minimum
        self.hits: deque[bool] = deque(maxlen=window)
        self._pending: tuple | None = None

    def commit(self, cell: tuple | None) -> None:
        self._pending = cell

    def observe(self, actual: tuple | None) -> None:
        if self._pending is not None and actual is not None:
            self.hits.append(self._pending == actual)
        self._pending = None

    @property
    def accuracy(self) -> float:
        return (sum(self.hits) / len(self.hits)) if self.hits else 0.0

    @property
    def trusted(self) -> bool:
        return len(self.hits) >= self.minimum and self.accuracy >= self.gate

    def predict(self, barriers: frozenset, pos: tuple, threat: tuple) -> tuple:
        return corner_next(self.size, frozenset(barriers), pos, threat)
