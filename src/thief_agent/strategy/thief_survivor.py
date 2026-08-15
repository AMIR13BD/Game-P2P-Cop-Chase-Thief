"""SurvivorBrain: safety-hard-constrained, mobility-maximising Thief evasion.

Fixes the 0-6 failure mode (fleeing to a corner then oscillating until the Police
walks in). Locates the pursuer from received scent only. Because our scent view can
lag the pursuer's true cell by one move, the true pursuer is treated as anywhere in
the closed neighbourhood of the belief peak. Distance is then a HARD SAFETY
CONSTRAINT (never step adjacent-or-onto a plausible pursuer cell if a safer legal
move exists), and among safe moves we maximise future mobility, escape space and
route diversity while penalising revisits/corners/articulation cells. Anti-loop
history + seeded micro-variation stop sub-games replaying one exploitable path.
Deterministic under a fixed seed; every action stays legal via the firewall."""

from collections import Counter, deque

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .connectivity import articulation_points
from .disjoint import edge_cells, vertex_disjoint_paths
from .graph import distance_map, reachable_area
from .moves import legal_steps

DIST_CAP = 10  # keep-distance is the primary flee term (7x7 diameter ~ 12)
ENDGAME_WINDOW = 12  # start guaranteed-survival scoring earlier (was 6): a strong Police herds
# a pure distance-maximiser into a corner ~step 26-27, before the old step-29 endgame engaged.
TIE_MARGIN = 2.0  # seeded-random pick among moves within this of the best -> path diversity so a
# fixed herding line cannot be replayed; < the 10.0 distance weight, so a materially safer/farther
# move is never traded away (safety/survival stays primary).

# Tunable objective weights (Phase 7 parameter optimisation target). Distance from the
# pursuer is the PRIMARY term (maximising the buffer is the strongest evasion against
# an equal-speed pursuer); openness/routes only break near-ties. The corner death is
# handled separately by a hard 2-ply trap filter, so distance is not sacrificed
# globally -- only cells where the pursuer could actually corner us are refused.
DEFAULT_WEIGHTS = {
    "dist": 10.0,  # capped BFS distance from the pursuer (primary: keep the buffer)
    "mobility": 1.5,  # open degree at the destination
    "area": 0.25,  # escape space with the pursuer treated as a wall
    "routes": 1.0,  # vertex-disjoint escape routes to the board frontier
    "future": 0.5,  # worst-case degree one step ahead (anti dead-end approach)
    "revisit": 5.0,  # penalty per prior visit to the destination
    "recent": 10.0,  # penalty for bouncing back into recent cells (anti-loop)
    "corner": 0.5,  # gentle tie-break weight on (4-degree)
    "artic": 2.0,  # penalty for stepping onto a cut vertex
    "stay": 6.0,  # penalty for a predictable STAY
}


def _blocked_area(board: Board, cell: Cell, wall: Cell | None) -> int:
    """Reachable component size from `cell` treating `wall` (the pursuer) as blocked."""
    if wall is None or wall == cell:
        return reachable_area(board, cell)
    trial = Board(board.size, board.barriers | {wall})
    return reachable_area(trial, cell)


class SurvivorBrain(BrainBase):
    def __init__(self, rng, horizon: int = 35, weights: dict | None = None, seed: int = 0) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self.seed = seed
        self.w = dict(DEFAULT_WEIGHTS)
        if weights:
            self.w.update(weights)
        self._recent: deque[Cell] = deque(maxlen=6)
        self._visits: Counter[Cell] = Counter()

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        self._recent.append(obs.self_pos)
        self._visits[obs.self_pos] += 1
        belief = BeliefMap(board)
        belief.update(obs.scent)
        peak = belief.argmax()
        plausible = {peak} | set(board.neighbors(peak)) if peak is not None else set()
        dmaps = [distance_map(board, p) for p in plausible]
        far = board.size * board.size

        def cop_dist(cell: Cell) -> int:
            return min((dm.get(cell, far) for dm in dmaps), default=far)

        def safe_exits(cell: Cell) -> int:
            """Neighbours of `cell` the pursuer cannot capture on its next move."""
            return sum(cop_dist(n) >= 2 for n in board.neighbors(cell))

        steps = legal_steps(obs, board)
        # Tier 0: never move onto a plausible pursuer cell (immediate capture).
        pool = [dc for dc in steps if dc[1] not in plausible] or steps
        # Tier 1: keep >= 2 from every plausible pursuer cell when we still can.
        safe = [dc for dc in pool if cop_dist(dc[1]) >= 2] or pool
        # Tier 2 (anti-corner-death): when the pursuer is close, refuse cells it could
        # corner -- one safe exit or fewer -- exactly the trap that lost G1/G3/G5. Only
        # applied while a safer option remains, so distance is never given up needlessly.
        untrapped = [dc for dc in safe if cop_dist(dc[1]) > 2 or safe_exits(dc[1]) >= 2]
        safe = untrapped or safe
        edges = edge_cells(board)
        cut = articulation_points(board)
        recent = set(self._recent)
        endgame = self.horizon - obs.step <= ENDGAME_WINDOW

        def score(dc: tuple[str, Cell]) -> float:
            direction, cell = dc
            cd = min(cop_dist(cell), DIST_CAP)
            degree = len(board.neighbors(cell))
            if endgame:  # near the threshold: guaranteed survival dominates novelty
                return (
                    100.0 * cd
                    + 12.0 * degree
                    + _blocked_area(board, cell, peak)
                    - 50.0 * (cell in plausible)
                )
            routes = vertex_disjoint_paths(board, cell, edges)
            future = min((len(board.neighbors(n)) for n in board.neighbors(cell)), default=0)
            w = self.w
            value = (
                w["dist"] * cd
                + w["mobility"] * degree
                + w["area"] * _blocked_area(board, cell, peak)
                + w["routes"] * routes
                + w["future"] * future
                - w["revisit"] * self._visits[cell]
                - w["recent"] * (cell in recent)
                - w["corner"] * max(0, 3 - degree)
                - w["artic"] * (cell in cut)
                - w["stay"] * (direction == "STAY")
            )
            return value

        # Seeded controlled-random tie-break among the safe moves within TIE_MARGIN of the best:
        # gives real path diversity (ahk-yosi cannot replay one herding line) without ever trading
        # away a materially safer/farther move. self.rng is seeded per sub-game -> reproducible.
        scored = [(score(dc), dc) for dc in safe]
        best_val = max(s for s, _ in scored)
        near = [dc for s, dc in scored if best_val - s <= TIE_MARGIN]
        best = near[self.rng.randrange(len(near))]
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "keeping to the crowded main roads"
