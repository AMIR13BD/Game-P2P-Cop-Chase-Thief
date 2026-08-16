"""Reporting CLI handlers (tournament, Gmail).

Kept separate from commands.py so both stay within the line limit. These are
role-agnostic; they read the shared config and delegate to the relevant modules.
`cmd_view` and `cmd_replay` moved to commands_gui.py when the Tk presentation layer
landed; they are re-exported here so existing import sites keep working."""

import argparse

from .commands_gui import cmd_replay, cmd_view  # noqa: F401  (re-export)
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


def cmd_gmail(args: argparse.Namespace) -> int:
    from .infra.gmail_cli import run

    return run(args)
