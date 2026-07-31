"""CLI command handlers (kept separate so cli.py stays within the line limit).

Every business operation is invoked through the AgentSDK facade; handlers only
parse arguments, build the shared config, and format output."""

import argparse

from .constants import Role
from .exceptions import ConfigError
from .sdk.sdk import AgentSDK
from .security.signer import DevTestSigner
from .shared.config_validate import validate
from .shared.defaults import DEFAULT_GAME_CONFIG
from .shared.gitinfo import current_commit

NATURAL_ROLE = Role.THIEF
GROUP_NAME = "amireman-thief"


def _sdk() -> AgentSDK:
    return AgentSDK(NATURAL_ROLE, GROUP_NAME, DevTestSigner(), current_commit())


def cmd_series(args: argparse.Namespace) -> int:
    try:
        cfg = validate(DEFAULT_GAME_CONFIG)
    except ConfigError as exc:
        print(f"technical-loss (config): {exc}")
        return 0
    res = _sdk().local_series(cfg, seed=args.seed)
    outs = [s["outcome"] for s in res["sub_games"]]
    print(f"role_sequence={res['role_sequence']}")
    print(f"outcomes={outs}")
    print(f"self_total={res['self_total']} opp_total={res['opp_total']} winner={res['winner']}")
    print(f"audit_all_passed={all(o != 'technical' for o in outs)}")
    print(f"github_commit={current_commit()}")
    return 0


def cmd_artifacts(args: argparse.Namespace) -> int:
    sdk = _sdk()
    series = sdk.local_series(validate(DEFAULT_GAME_CONFIG), seed=args.seed)
    v = sdk.emit_and_verify(args.out, args.game_id, args.opponent, series, DEFAULT_GAME_CONFIG)
    print(
        f"artifacts_dir={args.out} game_id={args.game_id} "
        f"audit_passed={v['passed']} failures={v['failures']}"
    )
    return 0 if v["passed"] else 1


def cmd_serve(args: argparse.Namespace) -> int:
    from .infra.serve import run

    valid = [t for t in args.token.split(",") if t]
    revoked = [t for t in args.revoked.split(",") if t] if args.revoked else []
    run("127.0.0.1", args.port, args.group, valid, revoked, seed=args.seed, grid=args.grid)
    return 0


def cmd_netplay(args: argparse.Namespace) -> int:
    import anyio

    sdk = _sdk()
    cfg = validate(DEFAULT_GAME_CONFIG)
    series = anyio.run(
        sdk.networked_series, args.opponent_url, args.token, cfg, args.seed, DEFAULT_GAME_CONFIG
    )
    v = sdk.emit_and_verify(
        args.out,
        args.game_id,
        args.opponent,
        series,
        DEFAULT_GAME_CONFIG,
        peer_commit=series.get("peer_commit"),
        peer_ident=series.get("peer_ident"),
    )
    print(f"role_sequence={series['role_sequence']}")
    print(f"outcomes={[s['outcome'] for s in series['sub_games']]}")
    print(f"audit_passed={v['passed']} failures={v['failures']}")
    if getattr(args, "counted", False):
        m = sdk.verify_match(args.out, args.game_id)
        print(f"match_audit_passed={m['passed']} failures={m['failures']}")
        return 0 if m["passed"] else 1
    return 0 if v["passed"] else 1


def cmd_simulate(args: argparse.Namespace) -> int:
    print(_sdk().simulate(validate(DEFAULT_GAME_CONFIG), turns=args.turns))
    return 0
