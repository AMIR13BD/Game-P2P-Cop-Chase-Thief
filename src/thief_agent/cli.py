"""CLI entry point: argparse wiring only (handlers live in commands.py)."""

import argparse

from . import commands


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="thief_agent", description="Thief peer (Day-1/2 core).")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("series", help="run a local six-sub-game series")
    s.add_argument("--seed", type=int, default=1234)
    s.set_defaults(func=commands.cmd_series)

    a = sub.add_parser("artifacts", help="run a local series and emit+verify the 4 artifacts")
    a.add_argument("--out", default="artifacts")
    a.add_argument("--game-id", dest="game_id", default="amireman-police-vs-opponent")
    a.add_argument("--opponent", default="opponent")
    a.add_argument("--seed", type=int, default=1234)
    a.set_defaults(func=commands.cmd_artifacts)

    sv = sub.add_parser("serve", help="run this peer as a FastMCP server process")
    sv.add_argument("--port", type=int, required=True)
    sv.add_argument("--token", required=True, help="comma-separated valid bearer tokens")
    sv.add_argument("--revoked", default="")
    sv.add_argument("--group", default=commands.GROUP_NAME)
    sv.add_argument("--seed", type=int, default=1234)
    sv.add_argument("--grid", type=int, default=None)
    sv.set_defaults(func=commands.cmd_serve)

    np = sub.add_parser("netplay", help="drive a networked six-sub-game series")
    np.add_argument("--opponent-url", dest="opponent_url", required=True)
    np.add_argument("--token", required=True)
    np.add_argument("--out", default="artifacts_net")
    np.add_argument("--game-id", dest="game_id", default="amireman-police-vs-opponent")
    np.add_argument("--opponent", default="opponent")
    np.add_argument("--seed", type=int, default=1234)
    np.set_defaults(func=commands.cmd_netplay)

    m = sub.add_parser("simulate", help="run a deterministic headless batch")
    m.add_argument("--turns", type=int, default=10000)
    m.set_defaults(func=commands.cmd_simulate)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
