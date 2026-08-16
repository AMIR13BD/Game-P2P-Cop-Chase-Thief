"""Rebuild REAL observations from recorded match evidence, to feed the live GUI.

A belief heatmap only means something when it is fed the scent field an agent actually
perceived. Rather than inventing probabilities for a screenshot, this module replays the
trajectories recorded in an audited log through the very same stigmergic kernel the match
engine uses (`domain.smell.step_update`), and hands the result to the same `BeliefMap` the
strategies consult. Nothing here participates in gameplay: it is a read-only
reconstruction over artifacts that already exist on disk."""

import os

from ..domain import smell
from ..domain.board import Board
from ..report import ids
from ..strategy.base import Observation
from .replay_data import load_log, reconstruct


def cells_upto(frames, idx) -> tuple:
    """(police_cell, thief_cell, barriers) as last recorded at or before frame `idx`."""
    police = thief = None
    barriers: list = []
    for frame in frames[: idx + 1]:
        if frame.cell is not None:
            if frame.role == "police":
                police = tuple(frame.cell)
            elif frame.role == "thief":
                thief = tuple(frame.cell)
        barriers = frame.barriers
    return police, thief, [tuple(b) for b in barriers]


def scents_upto(frames, idx, board, rho) -> tuple[dict, dict]:
    """(police_scent, thief_scent) after replaying every recorded position up to `idx`
    through the real emission kernel -- the same accumulation the turn engine performs."""
    police_scent: dict = {}
    thief_scent: dict = {}
    for frame in frames[: idx + 1]:
        if frame.cell is None:
            continue
        cell = tuple(frame.cell)
        if frame.role == "police":
            police_scent = smell.step_update(police_scent, cell, board, rho)
        elif frame.role == "thief":
            thief_scent = smell.step_update(thief_scent, cell, board, rho)
    return police_scent, thief_scent


def observation_at(frames, idx, cfg, role) -> Observation:
    """The Observation `role` legitimately held at frame `idx`.

    Own cell comes from that role's own recorded track; the scent is the OPPONENT's
    emission field, exactly as `peer.turn_engine` hands it to a brain."""
    police, thief, barriers = cells_upto(frames, idx)
    board = Board(cfg["grid_size"], set(barriers))
    police_scent, thief_scent = scents_upto(frames, idx, board, cfg["pheromone_decay"])
    fallback = cfg["cop_start"] if role == "police" else cfg["thief_start"]
    own = (police if role == "police" else thief) or tuple(fallback)
    step = frames[idx].step if 0 <= idx < len(frames) else 0
    return Observation(
        role=role,
        self_pos=tuple(own),
        board_size=cfg["grid_size"],
        barriers=frozenset(barriers),
        scent=thief_scent if role == "police" else police_scent,
        step=step,
        max_barriers=cfg["max_barriers"],
        barriers_used=len(barriers),
    )


def frames_from_dir(directory, game_id, sub_game=1) -> list:
    """Reconstructed frames for one sub-game of a recorded series; [] when absent."""
    return reconstruct(load_log(os.path.join(directory, ids.log_name(game_id, sub_game))))


def discover_game_ids(directory) -> list[str]:
    """Game ids that have at least one log file in `directory` (sorted, de-duplicated)."""
    found: set[str] = set()
    try:
        names = os.listdir(directory)
    except OSError:
        return []
    for name in names:
        if name.startswith("log_") and name.endswith(".json") and "_g" in name:
            found.add(name[len("log_") : name.rindex("_g")])
    return sorted(found)
