"""Argument parsing for the interop CLI.

The subcommand handler is injected by ``cli.py`` rather than imported, so the parser
definition carries no dependency on the runner it configures.

Split out of ``cli.py`` to keep both modules inside the repository's 150-line
ceiling. Flags, defaults and help text are unchanged.
"""

import argparse

from . import DEFAULT_GROUP_ID
from .consensus import LEGACY, PROFILES


def build_parser(handler) -> argparse.ArgumentParser:
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
    p.add_argument(
        "--game-id",
        dest="game_id",
        default=None,
        help="game_id AGREED WITH THE PEER out-of-band as the artifact filename base (e.g. "
        "'G002'); omit to derive '<groupA>-vs-<groupB>' locally. game_uid is always derived.",
    )
    p.add_argument(
        "--consensus-profile",
        dest="consensus_profile",
        choices=list(PROFILES),
        default=LEGACY,
        help="settlement digest envelope, AGREED WITH THE PEER out of band (never in the "
        "signed terms). 'legacy' (default) is what our filed series settled under; "
        "'official_reference_v1' reproduces the lecturer reference's own signature.",
    )
    p.add_argument("--games", type=int, default=6)
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument(
        "--commit",
        default=None,
        help="github_commit for the audit Step-0 record; default is the real HEAD SHA",
    )
    p.add_argument("--turn-timeout", type=float, default=180.0)
    p.add_argument(
        "--counted",
        action="store_true",
        help="OFFICIAL: same friendly flow; after a clean final audit, email the result JSON",
    )
    p.add_argument(
        "--demo-email-recipient",
        dest="demo_email_recipient",
        default=None,
        help="DEMO ONLY: after a clean 6-game run, auto-email the generated result JSON to "
        "this address (never the lecturer). Omit to send nothing.",
    )
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=handler)
    return ap
