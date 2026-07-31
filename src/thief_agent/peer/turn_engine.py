"""Local sub-game engine: commit-reveal per turn, scent, capture/survival checks.

Drives the state machine and returns outcome, scores, sealed records and trajectory.
Defined failures (illegal transition / crypto) propagate to the caller's safe_play."""

from ..constants import ORTHO
from ..domain import capture as cap
from ..domain import scoring, smell
from ..domain.board import Board
from ..domain.crypto import seal
from ..domain.protocol import build_payload
from ..domain.rules import barrier_cell
from ..domain.rules import step as step_move
from ..strategy.base import Observation
from ..strategy.firewall import enforce
from . import state_machine as states
from .sealing import make_step0_record


def _state_str(n, pos, barriers) -> str:
    return f"grid={n};self={list(pos)};barriers={sorted(list(b) for b in barriers)}"


def _obs(role, pos, board, scent, hint, step, max_b, used) -> Observation:
    return Observation(
        role=role,
        self_pos=pos,
        board_size=board.size,
        barriers=frozenset(board.barriers),
        scent=dict(scent),
        last_hint=hint,
        step=step,
        max_barriers=max_b,
        barriers_used=used,
    )


def run_sub_game(police_brain, thief_brain, cfg, group_name, signer, github_commit) -> dict:
    n = cfg["grid_size"]
    board = Board(n)
    police, thief = tuple(cfg["cop_start"]), tuple(cfg["thief_start"])
    max_moves, surv, max_b = cfg["max_moves"], cfg["survival_threshold"], cfg["max_barriers"]
    rho = cfg["pheromone_decay"]
    sm = states.StateMachine()
    for st in (states.CONFIG, states.NEGOTIATION, states.STEP0, states.READY):
        sm.to(st)
    records = [make_step0_record(group_name, cfg.get("sub_game_number", 1), signer, github_commit)]
    p_scent = smell.step_update({}, police, board, rho)
    t_scent = smell.step_update({}, thief, board, rho)
    traj: list = []
    illegal = diagonal = used = step = 0
    hint_p = hint_t = ""
    outcome = None

    def seal_turn(role, pos, action, hint):
        payload = build_payload(
            step,
            role,
            _state_str(n, pos, board.barriers),
            f"{action.kind}:{action.direction}",
            "truth",
            hint,
        )
        records.append({"payload": payload, **seal(payload)})

    while step < max_moves:
        step += 1
        for st in (states.COMMIT, states.ACK, states.REVEAL, states.MOVE):
            sm.to(st)
        obs = _obs("police", police, board, t_scent, hint_t, step, max_b, used)
        act, sub = enforce(police_brain.decide(obs), obs, board, "police")
        illegal += sub
        diagonal += 1 if (act.kind == "MOVE" and act.direction not in ORTHO) else 0
        hint_p = police_brain.hint(obs)
        if act.kind == "BARRIER":
            cell = barrier_cell(police, act.direction)
            board.add_barrier(cell)
            used += 1
            seal_turn("police", police, act, hint_p)
            if cap.barrier_captures(cell, thief):
                outcome = "capture"
                break
        else:
            police = step_move(police, act.direction) if act.kind == "MOVE" else police
            seal_turn("police", police, act, hint_p)
            if cap.captured_by_landing(police, thief):
                outcome = "capture"
                break
        for st in (states.COMMIT, states.ACK, states.REVEAL, states.MOVE):
            sm.to(st)
        if cap.thief_trapped(thief, board):
            outcome = "capture"
            break
        obs = _obs("thief", thief, board, p_scent, hint_p, step, max_b, used)
        act, sub = enforce(thief_brain.decide(obs), obs, board, "thief")
        illegal += sub
        diagonal += 1 if (act.kind == "MOVE" and act.direction not in ORTHO) else 0
        hint_t = thief_brain.hint(obs)
        thief = step_move(thief, act.direction) if act.kind == "MOVE" else thief
        seal_turn("thief", thief, act, hint_t)
        if cap.captured_by_landing(police, thief):
            outcome = "capture"
            break
        p_scent = smell.step_update(p_scent, police, board, rho)
        t_scent = smell.step_update(t_scent, thief, board, rho)
        traj.append((step, tuple(police), tuple(thief)))
        if step >= surv:
            outcome = "survival"
            break
    if outcome is None:
        outcome = "survival"
    sm.to(states.SUBGAME_DONE)
    p_score, t_score = scoring.score_outcome(outcome)
    return {
        "outcome": outcome,
        "police_score": p_score,
        "thief_score": t_score,
        "steps": step,
        "records": records,
        "trajectory": traj,
        "illegal": illegal,
        "diagonal": diagonal,
        "state": sm.state,
    }
