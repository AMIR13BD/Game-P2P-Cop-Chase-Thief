"""Series-level identity, MCP declaration, peer-commit resolution and the dropped-sub-game
summary.

Split out of ``series.py`` purely to keep each module inside the repository's 150-line
ceiling. The functions are verbatim; ``series`` re-exports them, so every existing
``from ...interop.series import identity_for`` keeps working and every emitted field is
unchanged.
"""

from ..shared.sysinfo import system_spec
from . import DEFAULT_MEMBERS, commits
from .engine import _now_iso


def _peer_commit(identity: dict, greeting: dict | None = None) -> str:
    """The peer's runtime SHA for THIS sub-game, as the peer itself declared it: from its
    negotiated ``identity`` block, else from the greeting that carried it (peers differ on
    where they put it). Only an exact 40-hex value is accepted, otherwise "" — the existing
    schema's safe empty. Reporting-only: never used in the canonical consensus (which
    excludes github_commit). See ``commits`` for the Step-0 fallback used when both are
    empty."""
    return commits.from_identity(identity, greeting)


def identity_for(
    group: str,
    repos: dict | None = None,
    mcp_servers: dict | None = None,
    members: list | None = None,
    llm_model: str = "template",
    github_commit: str = "",
    role_commits: dict | None = None,
) -> dict:
    """This peer's static per-GROUP identity, exchanged in the handshake (roles alternate).

    ``github_commit`` (== ``git_commit_hash``) is the real 40-char HEAD; it rides in the
    identity (NOT the signed terms) so the peer's declaration binds our commit.
    ``role_commits`` optionally declares the cop/thief repositories' own SHAs alongside it
    (see ``rolecommit``); omitted, the identity is exactly what it always was."""
    identity = {
        "group_id": group,
        "group_name": group,
        "git_commit_hash": github_commit,
        "github_commit": github_commit,
        "members": members if members is not None else list(DEFAULT_MEMBERS),
        "repos": repos
        or {
            "cop": "https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police",
            "thief": "https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Thief",
        },
        "mcp_servers": mcp_servers or {},
        "llm_model": llm_model,
        "spec": system_spec(),
    }
    if role_commits:
        identity["github_commits"] = dict(role_commits)
    return identity


def mcp_servers_for(public_mcp_url: str | None) -> dict:
    """Our public MCP address(es) for the identity, keyed role -> URL (both roles share one
    tunnel). A RUNTIME input, never hardcoded; empty when unset (preserves the prior wire
    shape). A peer that builds a pre-game declaration refuses an empty ``mcp_servers``."""
    if not public_mcp_url:
        return {}
    return {"cop": public_mcp_url, "thief": public_mcp_url}


def _dropped_summary(n: int, role: str, runtime) -> dict:
    """A sub-game whose TRANSPORT failed (peer/tunnel unreachable): recorded as a timeout --
    NEVER a fabricated capture/survival -- so the series continues and the peer can recover for
    later sub-games instead of the whole run crashing on one send/handshake failure."""
    return {
        "sub_game_number": n,
        "role": role,
        "result": "timeout",
        "winner": role,
        "steps": runtime.engine.step if runtime is not None else 0,
        "records": runtime.engine.records if runtime is not None else [],
        "audit": {
            "passed": False,
            "log_verified": False,
            "tampered": False,
            "verified_steps": 0,
            "failed_steps": [],
            "skipped": True,
            "local_result_claim": "timeout",
            "peer_result_claim": None,
            "result_agreed": False,
        },
        "started_at": _now_iso(),
        "duration_seconds": 0.0,
        "tokens_total": 0,
        "peer_github_commit": "",
    }
