"""Reporting and visualization CLI handlers (tournament, replay, GUI view, Gmail).

Kept separate from commands.py so both stay within the line limit. These are
role-agnostic; they read the shared config and delegate to the relevant modules."""

import argparse

from .shared.config_validate import validate
from .shared.defaults import DEFAULT_GAME_CONFIG


def cmd_tournament(args: argparse.Namespace) -> int:
    from .sim.tournament import select_champion

    cfg = validate(DEFAULT_GAME_CONFIG)
    seeds = list(range(1, args.seeds + 1))
    for role in ("police", "thief"):
        r = select_champion(cfg, role, seeds)
        print(f"{role} champion={r['champion']} {r['metric']}={r['score']} games={r['games']}")
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    import os

    from .gui.replay_controls import status_line
    from .gui.replay_data import board_at, load_log, reconstruct, render_truth_board
    from .gui.replay_verify import replay_status
    from .report import ids

    size = validate(DEFAULT_GAME_CONFIG)["grid_size"]
    found = 0
    for nn in range(1, 7):
        recs = load_log(os.path.join(args.dir, ids.log_name(args.game_id, nn)))
        if not recs:
            continue
        found += 1
        frames = reconstruct(recs)
        print(f"sub_game={nn} frames={len(frames)} {status_line(replay_status(recs))}")
        if found == 1 and frames:
            pos = board_at(frames, len(frames) - 1)
            print(render_truth_board(size, pos["police"], pos["thief"], pos["barriers"]))
    if not found:
        print("no replayable logs found")
    return 0


def cmd_view(args: argparse.Namespace) -> int:
    from .gui.window import local_view
    from .strategy.base import Observation

    cfg = validate(DEFAULT_GAME_CONFIG)
    obs = Observation(
        role="police",
        self_pos=tuple(cfg["cop_start"]),
        board_size=cfg["grid_size"],
        barriers=frozenset(),
        scent={},
        step=1,
        max_barriers=cfg["max_barriers"],
        barriers_used=0,
    )
    v = local_view(obs, state="MOVE")
    print(v["banner"])
    print(v["board"])
    print("-- belief heatmap --")
    print(v["heatmap"])
    return 0


def cmd_gmail(args: argparse.Namespace) -> int:
    from .infra.gmail_cli import run

    return run(args)
