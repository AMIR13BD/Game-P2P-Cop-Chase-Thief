"""CLI entry: run a local six-sub-game series or a headless batch simulation."""

import argparse

from .constants import Role
from .peer.audit import run_audit
from .sdk.series import run_series
from .security.signer import DevTestSigner
from .shared.config_validate import validate
from .shared.defaults import DEFAULT_GAME_CONFIG

NATURAL_ROLE = Role.THIEF
GROUP_NAME = "amireman-thief"


def _cfg() -> dict:
    return validate(DEFAULT_GAME_CONFIG)


def cmd_series(args: argparse.Namespace) -> int:
    res = run_series(_cfg(), NATURAL_ROLE, GROUP_NAME, DevTestSigner(), seed=args.seed)
    audits = [run_audit(s["records"])["passed"] for s in res["sub_games"]]
    print(f"role_sequence={res['role_sequence']}")
    print(f"outcomes={[s['outcome'] for s in res['sub_games']]}")
    print(f"self_total={res['self_total']} opp_total={res['opp_total']} winner={res['winner']}")
    print(f"audit_all_passed={all(audits)}")
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    from .sim.batch import run_batch

    r = run_batch(_cfg(), min_turns=args.turns)
    print(r)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="thief_agent", description="Thief peer (Day-1 core).")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("series", help="run a local six-sub-game series")
    s.add_argument("--seed", type=int, default=1234)
    s.set_defaults(func=cmd_series)
    m = sub.add_parser("simulate", help="run a deterministic headless batch")
    m.add_argument("--turns", type=int, default=10000)
    m.set_defaults(func=cmd_simulate)
    args = p.parse_args(argv)
    return args.func(args)
