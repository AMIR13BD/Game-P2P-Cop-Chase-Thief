"""Fresh held-out trap-oriented POLICE opponents for final Thief validation.

Created AFTER Thief-candidate selection and NOT inspected during tuning, to test that the
anti-herding correction generalises beyond corner_trap. Each is generic, legal, and
role-agnostic (a simple flee when it happens to play thief)."""

from ...domain.board import Board
from ...domain.rules import barrier_cell, legal_barrier_targets
from ...strategy.base import Action, BrainBase, Observation
from ...strategy.belief import BeliefMap
from ...strategy.fallback import safe_fallback
from ...strategy.moves import manhattan, move_away, move_toward


def _threat(obs: Observation, board: Board):
    belief = BeliefMap(board)
    belief.update(obs.scent)
    return belief.argmax()


def _flee(obs, board, t):
    return move_away(obs, board, t) if t is not None else safe_fallback(obs, board)


def _nearest_corner(board: Board, cell):
    n = board.size - 1
    return min([(0, 0), (0, n), (n, 0), (n, n)], key=lambda c: manhattan(c, cell))


def _nearest_edge(board: Board, cell):
    n = board.size - 1
    r, c = cell
    return min([(0, c), (n, c), (r, 0), (r, n)], key=lambda e: manhattan(e, cell))


class EdgeHerderBrain(BrainBase):
    """Police drives the belief toward the nearest wall/edge."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        t = _threat(obs, board)
        if obs.role != "police" or t is None:
            return _flee(obs, board, t)
        return move_toward(obs, board, _nearest_edge(board, t))


class ChokeControllerBrain(BrainBase):
    """Police claims the central choke, then closes on the thief."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        t = _threat(obs, board)
        if obs.role != "police":
            return _flee(obs, board, t)
        center = (obs.board_size // 2, obs.board_size // 2)
        if t is not None and manhattan(obs.self_pos, center) <= 1:
            return move_toward(obs, board, t)
        return move_toward(obs, board, center)


class DelayedCornerBrain(BrainBase):
    """Chase directly to open the gap, then herd toward the thief's corner."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        t = _threat(obs, board)
        if obs.role != "police" or t is None:
            return _flee(obs, board, t)
        if obs.step <= obs.board_size:
            return move_toward(obs, board, t)
        return move_toward(obs, board, _nearest_corner(board, t))


class SealAssistBrain(BrainBase):
    """Herd toward the corner and drop a barrier when close (barrier-assisted sealing)."""

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        t = _threat(obs, board)
        if obs.role != "police" or t is None:
            return _flee(obs, board, t)
        if obs.barriers_used < obs.max_barriers and manhattan(obs.self_pos, t) <= 2:
            for tt in legal_barrier_targets(obs.self_pos, board):
                if barrier_cell(obs.self_pos, tt) != obs.self_pos:
                    return Action("BARRIER", tt)
        return move_toward(obs, board, _nearest_corner(board, t))
