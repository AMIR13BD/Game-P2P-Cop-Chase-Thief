"""CLI handlers for the visual layer: the live GUI window and the replay viewer.

Split out of commands_report.py so both stay inside the line limit. These handlers only
read artifacts that already exist and open windows -- they never touch the match engine,
the strategies, or the protocol. `--gui` opens Tk; without it the original headless text
rendering is printed, so nothing that ran before behaves differently."""

import argparse

from .shared.config_validate import validate
from .shared.defaults import DEFAULT_GAME_CONFIG


def _cfg() -> dict:
    return validate(DEFAULT_GAME_CONFIG)


def natural_role() -> str:
    """This repository's own role. Imported lazily: commands.py imports us back."""
    from .commands import NATURAL_ROLE

    return str(NATURAL_ROLE)


def _frame_index(args, frames) -> int:
    wanted = getattr(args, "step", None)
    if wanted is None:
        return len(frames) - 1
    for index, frame in enumerate(frames):
        if frame.step >= wanted:
            return index
    return len(frames) - 1


def build_observation(args, cfg: dict, role: str):
    """A real recorded Observation when --replay-dir is given; the opening one otherwise."""
    from .gui.evidence import frames_from_dir, observation_at
    from .strategy.base import Observation

    directory = getattr(args, "replay_dir", None)
    if directory:
        frames = frames_from_dir(directory, args.game_id, getattr(args, "sub_game", 1))
        if frames:
            return observation_at(frames, _frame_index(args, frames), cfg, role)
    start = cfg["cop_start"] if role == "police" else cfg["thief_start"]
    return Observation(
        role=role,
        self_pos=tuple(start),
        board_size=cfg["grid_size"],
        barriers=frozenset(),
        scent={},
        step=1,
        max_barriers=cfg["max_barriers"],
        barriers_used=0,
    )


def _run(root, args) -> None:
    if getattr(args, "hold_ms", 0):
        root.after(int(args.hold_ms), root.destroy)
    root.mainloop()


def cmd_view(args: argparse.Namespace) -> int:
    """Live GUI: board, belief heatmap and the YOUR TURN / LOCKED indicator."""
    from .gui.live_model import live_state
    from .gui.window import local_view

    cfg = _cfg()
    role = getattr(args, "role", None) or natural_role()
    obs = build_observation(args, cfg, role)
    if getattr(args, "gui", False):
        from .gui import tk_live

        state = live_state(obs, state=getattr(args, "state", "MOVE"))
        title = f"{role.upper()} - Live GUI - belief heatmap (step {obs.step})"
        _run(tk_live.show(role, cfg["grid_size"], state, title), args)
        return 0
    view = local_view(obs, state=getattr(args, "state", "MOVE"))
    print(view["banner"])
    print(view["board"])
    print("-- belief heatmap --")
    print(view["heatmap"])
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    """Replay viewer over a recorded series, with real per-step SHA-256 verification."""
    from .gui.replay_data import render_truth_board
    from .gui.replay_model import load_sub_games

    cfg = _cfg()
    models = load_sub_games(args.dir, args.game_id, cfg["grid_size"])
    if not models:
        print("no replayable logs found")
        return 0
    if getattr(args, "gui", False):
        from .gui import tk_replay

        _run(tk_replay.show(models, f"Replay Viewer - {args.game_id}"), args)
        return 0
    for position, model in enumerate(models):
        print(f"sub_game={model.sub_game} frames={model.total} {model.integrity_text()}")
        if position == 0 and model.frames:
            model.go(model.total - 1)  # same final board the text viewer always printed
            frame = model.current()
            print(
                render_truth_board(
                    cfg["grid_size"], frame["police"], frame["thief"], frame["barriers"]
                )
            )
    return 0
