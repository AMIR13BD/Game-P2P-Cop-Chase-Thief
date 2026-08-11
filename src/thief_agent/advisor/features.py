"""Deterministic, role-safe tactical features + legal candidate enumeration.

Every value here is derived only from LEGALLY VISIBLE data: the agent's own
position/state, the shared board/barriers, and the received-scent belief over the
opponent. No hidden opponent position is ever read. The output is a compact context
(a handful of numbers per candidate) for the OpenAI selector -- never raw logs."""

from ..domain.board import Board, Cell
from ..domain.rules import barrier_cell, legal_barrier_targets
from ..strategy.base import Action, Observation
from ..strategy.belief import BeliefMap
from ..strategy.graph import distance_map, reachable_area
from ..strategy.moves import legal_steps

MAX_BARRIER_CANDIDATES = 3


def _barrier_candidates(obs: Observation, board: Board, peak: Cell | None) -> list[Action]:
    if obs.role != "police" or obs.barriers_used >= obs.max_barriers or peak is None:
        return []
    base = reachable_area(board, peak)
    scored: list[tuple[int, str]] = []
    for t in legal_barrier_targets(obs.self_pos, board):
        cell = barrier_cell(obs.self_pos, t)
        if cell == obs.self_pos:
            continue
        trial = Board(board.size, board.barriers | {cell})
        gain = base - (reachable_area(trial, peak) if trial.passable(peak) else 0)
        if trial.passable(peak) and distance_map(trial, peak).get(obs.self_pos) is None:
            continue  # self-obstruction: could no longer reach the belief cell
        scored.append((gain, t))
    scored.sort(reverse=True)
    return [Action("BARRIER", t) for _, t in scored[:MAX_BARRIER_CANDIDATES] if _ > 0]


def candidate_actions(obs: Observation, board: Board, peak: Cell | None) -> list[Action]:
    """Legal move/STAY candidates plus, for the Police, top value-positive barriers."""
    out = [Action("STAY") if d == "STAY" else Action("MOVE", d) for d, _ in legal_steps(obs, board)]
    return out + _barrier_candidates(obs, board, peak)


def _dest(obs: Observation, action: Action, board: Board) -> Cell:
    if action.kind == "BARRIER":
        return obs.self_pos
    if action.kind == "STAY":
        return obs.self_pos
    from ..domain.rules import step as step_move

    return step_move(obs.self_pos, action.direction)


def tactical_context(obs, board, candidates, recommended, profile, horizon=35) -> dict:
    """Compact JSON-able context: globals, opponent belief, and per-candidate features."""
    belief = BeliefMap(board)
    belief.update(obs.scent)
    peak = belief.argmax()
    pdist = distance_map(board, peak) if peak is not None else {}
    plausible = ({peak} | set(board.neighbors(peak))) if peak is not None else set()
    dmaps = [distance_map(board, p) for p in plausible]
    far = board.size * board.size

    def cop_dist(cell: Cell) -> int:
        return min((dm.get(cell, far) for dm in dmaps), default=far)

    cands = []
    for i, act in enumerate(candidates):
        cell = _dest(obs, act, board)
        feat = {
            "id": f"A{i}",
            "action": act.kind if act.kind != "MOVE" else f"MOVE:{act.direction}",
            "barrier_target": act.direction if act.kind == "BARRIER" else None,
            "opp_distance": pdist.get(cell, far) if peak is not None else -1,
            "mobility": len(board.neighbors(cell)),
            "reachable_area": reachable_area(board, cell),
        }
        if obs.role == "thief":
            feat["safe_exits"] = sum(cop_dist(n) >= 2 for n in board.neighbors(cell))
            feat["capturable_next"] = cop_dist(cell) <= 1
        cands.append(feat)
    return {
        "role": obs.role,
        "turn": obs.step,
        "max_turns": horizon,
        "board_size": obs.board_size,
        "self": list(obs.self_pos),
        "belief_peak": list(peak) if peak is not None else None,
        "remaining_barriers": obs.max_barriers - obs.barriers_used,
        "opponent_profile": profile or {},
        "recommended_id": recommended,
        "candidates": cands,
    }
