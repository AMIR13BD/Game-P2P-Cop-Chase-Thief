"""Command line for the official-protocol interop adapter.

    python -m thief_agent.interop friendly --peer <opponent-mcp-url> [--role police|thief]

FRIENDLY is the only mode this entry point offers: it plays a full official six-sub-game
series against an independent reference-compatible peer and CANNOT email a lecturer (see
``friendly``). A counted/official-reporting mode is a separate, explicit path and is not
reachable from here.
"""

import argparse
import sys
from pathlib import Path

from ..shared.gitinfo import current_commit
from .cli_args import build_parser as _build_parser
from .friendly import run_friendly
from .terms import default_terms, validate_terms


def _friendly(args) -> int:
    terms = default_terms()
    validate_terms(terms)
    token = args.token or None
    # Bind the audit's Step-0 github_commit to the REAL current HEAD (a 40-char SHA the
    # peer's final audit validates); resolved at the CLI boundary, never in domain code.
    commit = args.commit or current_commit(default="0" * 40)
    print(f"match_mode=friendly  group={args.group}  role={args.role}  peer={args.peer}")
    print(f"  bearer_auth={'on' if token else 'off (reference design: none)'}")
    print(f"  github_commit={commit}")
    print(
        "  public_mcp_url="
        + (args.public_mcp_url or "(none — a peer that builds a declaration will refuse)")
    )
    result = run_friendly(
        group=args.group,
        opponent_url=args.peer,
        natural_role=args.role,
        terms=terms,
        out_dir=Path(args.out),
        host=args.host,
        port=args.port,
        token=token,
        github_commit=commit,
        num_games=args.games,
        seed=args.seed,
        turn_timeout=args.turn_timeout,
        public_mcp_url=args.public_mcp_url or None,
        game_id=args.game_id or None,
        consensus_profile=args.consensus_profile,
        listener=lambda e: print(f"  [{e.get('type')}] {e}") if args.verbose else None,
    )
    print(f"\n  game_id  {result.game_id}\n  game_uid {result.game_uid}")
    print("  sub  role     outcome    steps  audit")
    for s in result.summaries:
        a = s["audit"]
        verdict = "SKIP" if a.get("skipped") else ("OK" if a.get("log_verified") else "TAMPER")
        print(
            f"  {s['sub_game_number']:>3}  {s['role']:<7} {s['result']:<10} "
            f"{s['steps']:>4}  {verdict}"
        )
    print(f"  consensus_profile {result.consensus_profile}")
    fr = result.result_doc.get("final_result", {})
    print(f"\n  totals {fr.get('total_score')}  winner {fr.get('winner_group') or 'tie'}")
    print(f"  {len(result.artifacts)} artifacts under {Path(args.out).resolve()}")
    print(f"\n  match_mode={'counted' if args.counted else 'friendly'}")
    out = str(Path(args.out))
    if args.counted:  # OFFICIAL: same friendly transport/flow, then email the lecturer
        if result.clean:
            from .mailer import official_email  # lazy: keep the friendly module mail-free

            official_email(out, result.game_id)
        else:
            print("  NOT EMAILING: series not clean (final audit failed) — artifacts kept")
    else:
        print(f"  lecturer_report_sent={result.lecturer_report_sent}")
        print("  (friendly is structurally unable to email a lecturer — no sender is wired)")
        if args.demo_email_recipient and result.clean:
            from .mailer import demo_email  # lazy

            demo_email(out, result.game_id, args.demo_email_recipient)
    return 0 if result.clean else 6


def build_parser() -> argparse.ArgumentParser:
    """The interop parser, wired to this module's runner (see cli_args for the flags)."""
    return _build_parser(_friendly)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
