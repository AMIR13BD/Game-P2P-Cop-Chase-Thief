#!/usr/bin/env python3
"""Capture the mandatory submission screenshots from the REAL Tk windows.

This is not part of the agent. It is a reproducible way to photograph the live GUI and the
replay viewer so that the images under docs/images are genuine captures of this code
running on real recorded evidence rather than mock-ups. Needs an X display and ffmpeg.

    uv run python scripts/capture_gui.py live   --dir <evidence> --game-id <id> --out a.png
    uv run python scripts/capture_gui.py replay --dir <evidence> --game-id <id> --out b.png
"""

import argparse
import os
import subprocess
import time

from thief_agent.gui import tk_live, tk_replay
from thief_agent.gui.evidence import frames_from_dir, observation_at
from thief_agent.gui.live_model import live_state
from thief_agent.gui.replay_model import load_sub_games
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def grab(root, out: str) -> None:
    """Photograph exactly this Tk toplevel via ffmpeg's X11 window capture."""
    root.update_idletasks()
    root.update()
    time.sleep(0.8)  # let the compositor map and paint the window
    root.update()
    width, height = root.winfo_width(), root.winfo_height()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "x11grab",
            "-draw_mouse",
            "0",
            "-window_id",
            str(root.winfo_id()),
            "-video_size",
            f"{width}x{height}",
            "-i",
            os.environ.get("DISPLAY", ":0"),
            "-frames:v",
            "1",
            "-update",
            "1",
            "-y",
            out,
        ],
        check=True,
    )
    print(f"captured {out} ({width}x{height})")


def capture_live(args) -> int:
    cfg = validate(DEFAULT_GAME_CONFIG)
    frames = frames_from_dir(args.dir, args.game_id, args.sub_game)
    if not frames:
        print("no frames found - cannot build a real belief map")
        return 1
    index = args.frame if args.frame is not None else len(frames) - 1
    obs = observation_at(frames, index, cfg, args.role)
    state = live_state(obs, state=args.state)
    if not state["informative"]:
        print("refusing to capture: belief map is uniform (no scent at this frame)")
        return 1
    title = f"{args.role.upper()} - Live GUI - belief heatmap (step {obs.step})"
    root = tk_live.show(args.role, cfg["grid_size"], state, title)
    grab(root, args.out)
    root.destroy()
    return 0


def capture_replay(args) -> int:
    cfg = validate(DEFAULT_GAME_CONFIG)
    models = load_sub_games(args.dir, args.game_id, cfg["grid_size"])
    if not models:
        print("no replayable logs found")
        return 1
    if args.tamper_step is not None:
        models = _tampered(models, args.tamper_step, cfg)
    model = models[0]
    for _ in range(args.frame or 0):
        model.step_forward()
    verdict = "TAMPERED" if not model.verified else "VERIFIED OK"
    print(f"verifier says: {model.integrity_text()}")
    if args.expect and args.expect not in verdict:
        print(f"refusing to capture: expected {args.expect}, verifier returned {verdict}")
        return 1
    root = tk_replay.show(models, f"Replay Viewer - {args.game_id}")
    grab(root, args.out)
    root.destroy()
    return 0


def _tampered(models, step: int, cfg: dict):
    """In-memory only: corrupt one record so the RED badge can be demonstrated honestly."""
    from thief_agent.gui.replay_model import ReplayModel
    from thief_agent.sim.tamper_gen import tamper_commit

    first = models[0]
    bad = tamper_commit(first.records, step=step)
    return [ReplayModel(bad, cfg["grid_size"], first.sub_game), *models[1:]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="capture_gui")
    sub = parser.add_subparsers(dest="mode", required=True)
    for name, handler in (("live", capture_live), ("replay", capture_replay)):
        part = sub.add_parser(name)
        part.add_argument("--dir", required=True)
        part.add_argument("--game-id", dest="game_id", required=True)
        part.add_argument("--sub-game", dest="sub_game", type=int, default=1)
        part.add_argument("--frame", type=int, default=None)
        part.add_argument("--out", required=True)
        part.set_defaults(func=handler)
    live = sub.choices["live"]
    live.add_argument("--role", choices=["police", "thief"], default="thief")
    live.add_argument("--state", default="MOVE")
    replay = sub.choices["replay"]
    replay.add_argument("--tamper-step", dest="tamper_step", type=int, default=None)
    replay.add_argument("--expect", default=None, help="abort unless the verdict matches")
    return parser


if __name__ == "__main__":
    _args = build_parser().parse_args()
    raise SystemExit(_args.func(_args))
