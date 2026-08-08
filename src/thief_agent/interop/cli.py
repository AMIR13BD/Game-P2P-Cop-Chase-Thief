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

from . import DEFAULT_GROUP_ID
from .friendly import run_friendly
from .terms import default_terms, validate_terms


def _friendly(args) -> int:
    terms = default_terms()
    validate_terms(terms)
    token = args.token or None
    print(f"match_mode=friendly  group={args.group}  role={args.role}  peer={args.peer}")
    print(f"  bearer_auth={'on' if token else 'off (reference design: none)'}")
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
        github_commit=args.commit,
        num_games=args.games,
        seed=args.seed,
        turn_timeout=args.turn_timeout,
        public_mcp_url=args.public_mcp_url or None,
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
    fr = result.result_doc.get("final_result", {})
    print(f"\n  totals {fr.get('total_score')}  winner {fr.get('winner_group') or 'tie'}")
    print(f"  {len(result.artifacts)} artifacts under {Path(args.out).resolve()}")
    print(f"\n  match_mode=friendly\n  lecturer_report_sent={result.lecturer_report_sent}")
    print("  (friendly is structurally unable to email a lecturer — no sender is wired)")
    return 0 if result.clean else 6


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m thief_agent.interop",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("friendly", help="play a full official friendly series (no email)")
    p.add_argument("--peer", required=True, help="the opponent's MCP URL")
    p.add_argument("--group", default=DEFAULT_GROUP_ID)
    p.add_argument(
        "--role",
        default="police",
        choices=["police", "thief"],
        help="our natural role in sub-game 1 (roles alternate); use the side "
        "COMPLEMENTARY to the opponent's",
    )
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8901)
    p.add_argument("--token", default="", help="optional shared bearer token (off by default)")
    p.add_argument(
        "--public-mcp-url",
        default="",
        help="our PUBLIC MCP URL (e.g. the Cloudflare tunnel) to advertise in the "
        "negotiation identity's mcp_servers; required by peers that build a pre-game "
        "declaration (e.g. sharNamr). Runtime value — never hardcoded.",
    )
    p.add_argument("--out", default="runs/interop")
    p.add_argument("--games", type=int, default=6)
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--commit", default="local")
    p.add_argument("--turn-timeout", type=float, default=180.0)
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_friendly)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
