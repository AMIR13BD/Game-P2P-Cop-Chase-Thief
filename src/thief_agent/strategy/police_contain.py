"""ContainBrain: belief-tracking interception + value-positive barrier containment Police.

Equal-speed pursuit alone cannot catch an equal-speed evader on open ground, so this
brain wins by locating the Thief precisely and then *closing + shrinking* its space:

(a) LOCALISE — the received additive scent saturates into a plateau of 0.9-capped cells,
    so the raw argmax mislocates the Thief. Instead we read the FRESH-emission delta of
    the received scent between our turns: the cell whose intensity just jumped by ~a
    centre deposit is the Thief's current cell. We persist the last lock while the Thief
    is stationary and fall back to the belief argmax only when there is no signal.
(b) CAPTURE on contact (Police moves first, so landing on the tracked cell is a capture).
(c) BARRIER — place one only when it measurably reduces the Thief's reachable component
    or seals it (``best_barrier`` is internally gated on a real area cut, never walls
    empty space or self-obstructs).
(d) CLOSE — shortest-path pursuit with a Chebyshev edge-cornering bias, a containment
    term (stand in the doorway), anti-cycling memory (break the oscillation that let the
    Thief idle), and raised aggression as the move limit approaches.

Deterministic and fast (no randomness, no LLM); every action stays legal via the
firewall. Emits nothing onto the wire — ``capture_claim`` is produced by the runtime,
never here."""

from collections import Counter

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .connectivity import articulation_points
from .fallback import safe_fallback
from .graph import distance_map, reachable_area
from .moves import legal_steps
from .police_barrier import best_barrier
from .variation import micro_variation

DECAY_COMPLEMENT = 0.9  # 1 - decay_per_step (agreed term decay_per_step = 0.1)
FRESH_DELTA = 0.15  # a scent jump above this = a fresh centre deposit (the Thief moved here)
ENDGAME_WINDOW = 6  # last few turns: prioritise closing over finesse


def _containment(board: Board, dest: Cell, target: Cell) -> int:
    """Thief reachable area if the Police stands on `dest` (dest treated as a wall)."""
    if dest == target:
        return 0
    trial = Board(board.size, board.barriers | {dest})
    return reachable_area(trial, target)


class ContainBrain(BrainBase):
    def __init__(self, rng, horizon: int = 35, seed: int = 0) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self.seed = seed
        self._prev_scent: dict[Cell, float] = {}  # received scent at our previous turn
        self._target: Cell | None = None  # persisted Thief-cell lock
        self._visits: Counter[Cell] = Counter()  # our own visited cells (anti-cycling)

    def _locate(self, board: Board, scent: dict[Cell, float]) -> Cell | None:
        """Track the Thief's CURRENT cell from the fresh-emission delta of received scent.

        The delta ``scent - (1-rho)*prev`` peaks at the cell that just received a fresh
        centre deposit (~0.9), which disambiguates the 0.9 saturation plateau. When the
        Thief is stationary the delta is small, so we hold the previous lock. Only when
        there is no lock and no fresh signal do we fall back to the belief argmax."""
        best, best_delta = None, 0.0
        for cell, val in scent.items():
            if cell in board.barriers:
                continue
            delta = val - DECAY_COMPLEMENT * self._prev_scent.get(cell, 0.0)
            if delta > best_delta:
                best_delta, best = delta, cell
        if best is not None and best_delta > FRESH_DELTA:
            self._target = best  # a fresh deposit appeared: the Thief moved here
        elif self._target is None or self._target in board.barriers:
            belief = BeliefMap(board)
            belief.update(scent)
            self._target = belief.argmax()
        return self._target

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = self._locate(board, obs.scent)
        self._prev_scent = dict(obs.scent)
        self._visits[obs.self_pos] += 1
        if target is None:
            return safe_fallback(obs, board)
        steps = legal_steps(obs, board)
        # Capture on contact: step onto the tracked Thief cell if we can (Police moves first).
        for direction, cell in steps:
            if cell == target and direction != "STAY":
                return Action("MOVE", direction)
        # Value-positive containment barrier: gated internally on a measurable reachable-area
        # reduction (> tempo) / outright seal, and rejects self-obstruction -- never wastes one.
        bar = best_barrier(obs, board, target)
        if bar is not None:
            return bar
        # Cornering pursuit: shortest-path closing is primary (robust from any start), with a
        # Chebyshev-axis bias to drive the Thief against an edge, a containment term to stand
        # in the doorway, and an anti-cycling penalty so we never idle in an oscillation while
        # the Thief sits. Aggression rises near the move limit. STAY is never chosen if we can move.
        movers = [dc for dc in steps if dc[0] != "STAY"] or steps
        tdist = distance_map(board, target)
        far = board.size * board.size
        endgame = self.horizon - obs.step <= ENDGAME_WINDOW
        cut = articulation_points(board)
        w_close = 14.0 if endgame else 10.0

        def score(dc: tuple[str, Cell]) -> float:
            direction, cell = dc
            total = tdist.get(cell, far)  # shortest-path distance to the tracked Thief cell
            axis = max(abs(cell[0] - target[0]), abs(cell[1] - target[1]))  # Chebyshev edge bias
            contain = _containment(board, cell, target)  # smaller Thief escape area is better
            revisit = self._visits[cell]  # anti-cycling: avoid re-treading our own path
            block = 1 if cell in cut else 0  # standing on a cut vertex constrains the Thief
            value = (
                -w_close * total
                - 2.0 * axis
                - 0.25 * contain
                - 3.0 * revisit
                + 0.5 * block
            )
            return value + micro_variation(self.seed, obs.step, cell, direction)

        best = max(movers, key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "setting up a roadblock ahead"
