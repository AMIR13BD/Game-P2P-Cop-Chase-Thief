"""CLI command handlers (kept separate so cli.py stays within the line limit)."""

import argparse

from .constants import Role
from .exceptions import ConfigError
from .sdk.series import run_series
from .security.signer import DevTestSigner
from .shared.config_validate import validate
from .shared.defaults import DEFAULT_GAME_CONFIG
from .shared.gitinfo import current_commit

NATURAL_ROLE = Role.THIEF
GROUP_NAME = "amireman-thief"


def cmd_series(args: argparse.Namespace) -> int:
    try:
        cfg = validate(DEFAULT_GAME_CONFIG)
    except ConfigError as exc:
        print(f"technical-loss (config): {exc}")
        return 0
    res = run_series(
        cfg,
        NATURAL_ROLE,
        GROUP_NAME,
        DevTestSigner(),
        seed=args.seed,
        github_commit=current_commit(),
    )
    outs = [s["outcome"] for s in res["sub_games"]]
    print(f"role_sequence={res['role_sequence']}")
    print(f"outcomes={outs}")
    print(f"self_total={res['self_total']} opp_total={res['opp_total']} winner={res['winner']}")
    print(f"audit_all_passed={all(o != 'technical' for o in outs)}")
    print(f"github_commit={current_commit()}")
    return 0


def cmd_artifacts(args: argparse.Namespace) -> int:
    from .report.emit import emit_series
    from .report.verify import verify_series

    cfg = validate(DEFAULT_GAME_CONFIG)
    gid = args.game_id
    series = run_series(
        cfg,
        NATURAL_ROLE,
        GROUP_NAME,
        DevTestSigner(),
        seed=args.seed,
        github_commit=current_commit(),
    )
    repos = {
        GROUP_NAME: {"cop": "local", "thief": "local"},
        args.opponent: {"cop": "local", "thief": "local"},
    }
    emit_series(
        args.out,
        gid,
        {**DEFAULT_GAME_CONFIG, "agreed_between": [GROUP_NAME, args.opponent]},
        GROUP_NAME,
        args.opponent,
        series,
        current_commit(),
        repos,
        DevTestSigner(),
    )
    v = verify_series(args.out, gid, DevTestSigner())
    print(
        f"artifacts_dir={args.out} game_id={gid} audit_passed={v['passed']} failures={v['failures']}"
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

    from .peer.net_runtime import run_networked
    from .report.emit import emit_series
    from .report.verify import verify_match, verify_series

    cfg = validate(DEFAULT_GAME_CONFIG)
    series = anyio.run(
        run_networked,
        args.opponent_url,
        args.token,
        cfg,
        NATURAL_ROLE,
        GROUP_NAME,
        current_commit(),
        DevTestSigner(),
        args.seed,
        DEFAULT_GAME_CONFIG,
    )
    repos = {
        GROUP_NAME: {"cop": "local", "thief": "local"},
        args.opponent: {"cop": "local", "thief": "local"},
    }
    emit_series(
        args.out,
        args.game_id,
        {**DEFAULT_GAME_CONFIG, "agreed_between": [GROUP_NAME, args.opponent]},
        GROUP_NAME,
        args.opponent,
        series,
        current_commit(),
        repos,
        DevTestSigner(),
        peer_commit=series.get("peer_commit"),
        peer_ident=series.get("peer_ident"),
    )
    v = verify_series(args.out, args.game_id, DevTestSigner())
    print(f"role_sequence={series['role_sequence']}")
    print(f"outcomes={[s['outcome'] for s in series['sub_games']]}")
    print(f"audit_passed={v['passed']} failures={v['failures']}")
    if getattr(args, "counted", False):
        m = verify_match(args.out, args.game_id, DevTestSigner())
        print(f"match_audit_passed={m['passed']} failures={m['failures']}")
        return 0 if m["passed"] else 1
    return 0 if v["passed"] else 1


def cmd_simulate(args: argparse.Namespace) -> int:
    from .sim.batch import run_batch

    print(run_batch(validate(DEFAULT_GAME_CONFIG), min_turns=args.turns))
    return 0
