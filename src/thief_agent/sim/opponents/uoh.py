"""Faithful sparring proxy for the public uoh-ay26 policy (their pinned SHAs).

Independent reimplementation of the mechanisms visible in their public
``tactical_planner.py`` -- NOT a copy of their code. Two roles:

* ``UohThiefBrain`` -- safety is a HARD CONSTRAINT (drop any move with direct- or
  proximity-capture risk while a safer legal move exists), then maximise mobility,
  escape routes and open area; loop/revisit history breaks oscillation.
* ``UohCopBrain`` -- pure interception (their cop places no barriers): minimise
  expected distance to the belief peak and to its evasive reply, and stand where it
  collapses the thief's escape area (containment); STAY is never a cop candidate.

Used only as an evaluation opponent (never in the tuning set) so our own strategy is
measured against, not overfit to, their public play. Deterministic under a seed."""

from collections import Counter, deque

from ...domain.board import Board, Cell
from ...strategy.base import Action, BrainBase, Observation
from ...strategy.belief import BeliefMap
from ...strategy.disjoint import edge_cells, vertex_disjoint_paths
from ...strategy.fallback import safe_fallback
from ...strategy.graph import distance_map, reachable_area
from ...strategy.moves import legal_steps


def _capture_cells(board: Board, cop: Cell) -> set[Cell]:
    """Cells the cop reaches next turn (move or STAY): its neighbours and itself."""
    return {cop} | set(board.neighbors(cop))


def _threat(obs: Observation, board: Board) -> Cell | None:
    belief = BeliefMap(board)
    belief.update(obs.scent)
    return belief.argmax()


class UohThiefBrain(BrainBase):
    def __init__(self, rng) -> None:
        super().__init__(rng)
        self._recent: deque[Cell] = deque(maxlen=8)
        self._visits: Counter[Cell] = Counter()

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        self._recent.append(obs.self_pos)
        self._visits[obs.self_pos] += 1
        threat = _threat(obs, board)
        steps = legal_steps(obs, board)
        if threat is None:
            best = max(steps, key=lambda dc: reachable_area(board, dc[1]))
            return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])
        danger = _capture_cells(board, threat)
        safe = [dc for dc in steps if dc[1] != threat] or steps
        safe = [dc for dc in safe if dc[1] not in danger] or safe
        edges = edge_cells(board)
        dist = distance_map(board, threat)
        recent2 = set(list(self._recent)[-2:])

        def score(dc: tuple[str, Cell]) -> float:
            cell = dc[1]
            margin = max(0.0, dist.get(cell, 0) - 1.0)
            mobility = len(board.neighbors(cell))
            routes = vertex_disjoint_paths(board, cell, edges)
            trial = Board(board.size, board.barriers | {threat})
            space = reachable_area(trial, cell) if cell != threat else 0
            return (
                9.0 * margin + 2.2 * mobility + 5.0 * routes + 0.6 * space
                - 4.0 * self._visits[cell] - 15.0 * (cell in recent2)
                - (9.0 if dc[0] == "STAY" else 0.0)
            )

        best = max(safe, key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "slipping down a side street"


class UohCopBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        target = _threat(obs, board)
        if target is None:
            return safe_fallback(obs, board)
        steps = [dc for dc in legal_steps(obs, board) if dc[0] != "STAY"] or legal_steps(obs, board)
        tdist = distance_map(board, target)
        # the thief's believed best one-step flight away from us
        flee = max(board.neighbors(target) or [target],
                   key=lambda c: distance_map(board, obs.self_pos).get(c, 0))
        fdist = distance_map(board, flee)
        far = board.size * board.size

        def score(dc: tuple[str, Cell]) -> float:
            cell = dc[1]
            expected = tdist.get(cell, far)
            intercept = fdist.get(cell, far)
            trial = Board(board.size, board.barriers | {cell})
            contain = reachable_area(trial, target) if cell != target else 0
            mobility = len(board.neighbors(cell))
            return -10.0 * expected - 4.0 * intercept + 1.4 * mobility - 0.35 * contain

        best = max(steps, key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "closing the net"
