"""One synthetic OFFICIAL six-sub-game result, built through the real production builders
(``build_result`` + ``enrich_result``) so the compliance tests assert on exactly what a future
counted match will email. Roles alternate with amireman starting as Thief."""

from thief_agent.interop.artifacts import build_result
from thief_agent.interop.scoring import role_for
from thief_agent.interop.series import identity_for
from thief_agent.interop.submission import enrich_result

OURS, THEIRS = "amireman", "Orcai-MJ"
OUR_SHA = "1111111111111111111111111111111111111111"
PEER_POLICE_SHA = "2222222222222222222222222222222222222222"  # peer runtime on g1/g3/g5
PEER_THIEF_SHA = "3333333333333333333333333333333333333333"  # peer runtime on g2/g4/g6
SERIES_SHA = "a1" * 32
PEER_REPOS = {
    "cop": "https://github.com/orcai-mj/cop",
    "thief": "https://github.com/orcai-mj/thief",
}


def summaries(num_games: int = 6, tokens: int = 0) -> list:
    """Per-sub-game runtime summaries: alternating roles, alternating peer runtime SHAs."""
    out = []
    for n in range(1, num_games + 1):
        role = role_for("thief", n)  # amireman starts as Thief
        out.append(
            {
                "sub_game_number": n,
                "role": role,
                "result": "survival" if role == "thief" else "capture",
                "winner": "thief" if role == "thief" else "police",
                "steps": 35,
                "records": [],
                "audit": {
                    "log_verified": True,
                    "tampered": False,
                    "local_result_claim": "x",
                    "peer_result_claim": "x",
                    "result_agreed": True,
                },
                "started_at": f"2026-09-01T10:0{n}:00+00:00",
                "duration_seconds": 30.0,
                "tokens_total": tokens,
                "peer_github_commit": PEER_POLICE_SHA if n % 2 else PEER_THIEF_SHA,
            }
        )
    return out


def identities() -> tuple:
    ours = identity_for(
        OURS,
        mcp_servers={"cop": "https://ours.example/mcp", "thief": "https://ours.example/mcp"},
        members=["Member One", "Member Two"],
        github_commit=OUR_SHA,
    )
    theirs = {
        **identity_for(THEIRS, repos=PEER_REPOS, members=["Peer One"], github_commit=""),
        "mcp_servers": {"cop": "https://peer.example/mcp", "thief": "https://peer.example/mcp"},
        "llm_model": "template",
        "spec": {"cpu_cores": 4, "cpu_type": "x86_64"},
    }
    return ours, theirs


def official_result(game_id: str = "G013", num_games: int = 6, tokens: int = 0) -> dict:
    """The exact document a counted run would write to ``result_<game_id>.json``."""
    rows = summaries(num_games, tokens)
    ours, theirs = identities()
    doc = build_result(game_id, "uid-0001", OURS, THEIRS, rows, {OURS: OUR_SHA})
    consensus = {"sha256": SERIES_SHA, "peer_sha256": SERIES_SHA, "sha_match": True}
    return enrich_result(doc, rows, ours, theirs, consensus)
