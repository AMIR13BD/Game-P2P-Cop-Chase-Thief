"""A SERIES of N sub-games between two peers with role alternation.

The transport/servers are built once by the caller and reused across sub-games. Each
sub-game runs a fresh handshake (mutual signed terms, matching the reference/kit which
re-greet per sub-game) and a fresh runtime. Roles alternate: the natural role on odd
sub-games, the opposite on even ones — so when we are cop the opponent is thief.
"""

import time
from dataclasses import dataclass, field

from ..shared.sysinfo import system_spec
from . import DEFAULT_MEMBERS
from .consensus import canonical_rows, consensus_sha
from .negotiate import Negotiator
from .runtime import SubGameRuntime
from .scoring import role_for
from .wire import AuditPayload

_CONSENSUS_TAG = "__consensus__"


def identity_for(
    group: str,
    repos: dict | None = None,
    mcp_servers: dict | None = None,
    members: list | None = None,
    llm_model: str = "template",
    github_commit: str = "",
) -> dict:
    """This peer's static per-GROUP identity, exchanged in the handshake (roles alternate).

    ``github_commit`` (== ``git_commit_hash``) is the real 40-char HEAD; it rides in the
    identity (NOT the signed terms) so the peer's declaration binds our commit."""
    return {
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


def mcp_servers_for(public_mcp_url: str | None) -> dict:
    """Our public MCP address(es) for the identity, keyed role -> URL (both roles share one
    tunnel). A RUNTIME input, never hardcoded; empty when unset (preserves the prior wire
    shape). A peer that builds a pre-game declaration refuses an empty ``mcp_servers``."""
    if not public_mcp_url:
        return {}
    return {"cop": public_mcp_url, "thief": public_mcp_url}


@dataclass
class SeriesResult:
    summaries: list = field(default_factory=list)
    own_identity: dict = field(default_factory=dict)
    peer_identity: dict = field(default_factory=dict)
    game_id: str | None = None
    game_uid: str | None = None
    consensus_sha: str | None = None  # OUR canonical series digest
    peer_consensus_sha: str | None = None  # the peer's digest, as actually received (else None)
    sha_match: bool = False  # peer digest received AND byte-identical to ours
    results_agreed: bool = False  # every sub-game's local vs peer result_claim matched


def _exchange_consensus(transport, sender: str, our_sha: str, turn_timeout: float) -> str | None:
    """Send OUR digest and wait (bounded) for the PEER's over the same final-audit channel, so
    ``confirmed`` needs a real peer match — never a local hash. A non-participating peer yields
    ``None`` (confirmed stays false). No new transport is created."""
    transport.send_audit(AuditPayload(sender, [], _CONSENSUS_TAG, consensus_sha=our_sha).to_wire())
    deadline = time.monotonic() + min(turn_timeout, 15.0)
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        msg = transport.poll_audit(remaining)
        if msg is None:
            return None
        digest = AuditPayload.from_wire(msg).consensus_sha
        if digest is not None:  # skip any straggler per-sub-game audit; take the digest message
            return digest


def run_series(
    terms: dict,
    natural_role: str,
    transport,
    group: str,
    github_commit: str,
    own_identity: dict | None = None,
    num_games: int = 6,
    seed: int = 1234,
    listener=None,
    turn_timeout: float = 180.0,
    game_id: str | None = None,
) -> SeriesResult:
    """Play our side of a whole series against a real opponent.

    ``game_id`` optionally OVERRIDES the derived filename base with a peer-agreed value
    (Table 20); ``game_uid`` is always the derived crypto id and is never overridden."""
    own_identity = own_identity or identity_for(group, github_commit=github_commit)
    result = SeriesResult(own_identity=own_identity)
    known_opponent: str | None = None
    for n in range(1, num_games + 1):
        role = role_for(natural_role, n)
        negotiator = Negotiator(terms, own_identity, group)
        peer_msg = transport.exchange_agreement(
            negotiator.signed(role, n, opponent_group=known_opponent).to_wire()
        )
        agreed = negotiator.verify_peer(peer_msg)
        result.game_id, result.game_uid = game_id or agreed.game_id, agreed.game_uid
        known_opponent = agreed.opponent_group
        result.peer_identity = agreed.opponent_identity or result.peer_identity
        if listener is not None:
            listener(
                {
                    "type": "negotiated",
                    "sub_game": n,
                    "role": role,
                    "game_id": agreed.game_id,
                    "game_uid": agreed.game_uid,
                }
            )
        runtime = SubGameRuntime(role, terms, transport, group, github_commit, n, seed, listener)
        result.summaries.append(runtime.run(turn_timeout=turn_timeout))
    # After the series: per-sub-game result agreement, then an explicit digest EXCHANGE so
    # mutual confirmation needs a real peer SHA match (a locally-computed hash is never enough).
    theirs = result.peer_identity.get("group_id", "")
    rows = canonical_rows(result.summaries, group, theirs)
    result.consensus_sha = consensus_sha(result.game_id or "", result.game_uid or "", rows)
    result.results_agreed = bool(result.summaries) and all(
        s["audit"].get("result_agreed", False) for s in result.summaries
    )
    result.peer_consensus_sha = _exchange_consensus(
        transport, group, result.consensus_sha, turn_timeout
    )
    result.sha_match = (
        result.peer_consensus_sha is not None and result.peer_consensus_sha == result.consensus_sha
    )
    return result
