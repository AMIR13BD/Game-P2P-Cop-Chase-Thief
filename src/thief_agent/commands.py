"""CLI command handlers (kept separate so cli.py stays within the line limit).

Every business operation is invoked through the AgentSDK facade; handlers only
parse arguments, build the shared config, and format output."""

import argparse

from .constants import Role
from .exceptions import ConfigError
from .sdk.sdk import AgentSDK
from .security.signer import signer_from_env
from .shared.config_validate import validate
from .shared.defaults import DEFAULT_GAME_CONFIG
from .shared.gitinfo import current_commit

NATURAL_ROLE = Role.THIEF
GROUP_NAME = "amireman-thief"


def _sdk() -> AgentSDK:
    return AgentSDK(NATURAL_ROLE, GROUP_NAME, signer_from_env(GROUP_NAME), current_commit())


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
    reasons = [
        (s["sub_game"], s["reason"])
        for s in series["sub_games"]
        if s["outcome"] == "technical" and s.get("reason")
    ]
    if reasons:
        print(f"technical_reasons={reasons}")
    print(f"audit_passed={v['passed']} failures={v['failures']}")
    if getattr(args, "counted", False):
        m = sdk.verify_match(args.out, args.game_id)
        print(f"match_audit_passed={m['passed']} failures={m['failures']}")
        if not (v["passed"] and m["passed"]):
            return 1
        return _official_email(args, series)  # audited: shape ONE result + mail lecturer
    return 0 if v["passed"] else 1


def _official_email(args: argparse.Namespace, series: dict) -> int:
    """After the counted audit passes, write the ONE reference-shaped result and email it.

    The audit ran on the FULL artifacts; we gate once more with the existing counted
    ``should_send()`` on that full result, then strip it to the reference result SHAPE
    (audit-only keys stay in the config/log artifacts), write the ONE final result JSON, and
    email THAT exact file once to the lecturer. Any Gmail failure keeps all artifacts."""
    import json
    import os

    from .infra import gmail_auth as ga
    from .infra import gmail_cli as gc
    from .infra import gmail_report as gr
    from .report import ids, schemas
    from .report.official_result import shape_official_result

    full = gr.load_result(args.out, args.game_id)
    ok, reason = gr.should_send(full)  # counted safety gate on the FULL audited result
    if not ok:
        print(f"EMAIL FAILED (gate): {reason}; artifacts kept, nothing sent.")
        return 3
    steps = {sg["sub_game"]: sg.get("steps", 0) for sg in series.get("sub_games", [])}
    shaped = schemas.validate("result", shape_official_result(full, steps))
    with open(os.path.join(args.out, ids.result_name(args.game_id)), "w", encoding="utf-8") as fh:
        json.dump(shaped, fh, indent=2, sort_keys=True)  # THE one final result JSON
    name, blob = gr.report_attachment(args.out, args.game_id)  # that exact file
    gr.validate_attachment(blob)
    st = ga.email_settings(None, "send")  # lecturer default recipient
    msg = gr.build_message(
        "me", st["recipient"], gc._subject(args.game_id), gc._body(args.game_id), name, blob
    )
    try:
        service = ga.build_service()
    except RuntimeError as exc:
        print(f"EMAIL FAILED: {exc}; final result saved, nothing sent.")
        return 3
    marker = os.path.join(args.out, f"gmail_sent_{args.game_id}.json")
    res = gr.send_report(service, msg, marker)  # idempotent: exactly one email
    print(f"lecturer_report_sent={res['status']} id={res.get('message_id')} to={st['recipient']}")
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    print(_sdk().simulate(validate(DEFAULT_GAME_CONFIG), turns=args.turns))
    return 0


# Reporting/visualization handlers live in commands_report.py (keeps this file small);
# re-exported here so the CLI can reference them uniformly as commands.cmd_*.
from .commands_report import cmd_gmail, cmd_replay, cmd_tournament, cmd_view  # noqa: E402,F401
