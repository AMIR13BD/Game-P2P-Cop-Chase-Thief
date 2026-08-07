"""A SERIES of N sub-games between two peers with role alternation.

The transport/servers are built once by the caller and reused across sub-games. Each
sub-game runs a fresh handshake (mutual signed terms, matching the reference/kit which
re-greet per sub-game) and a fresh runtime. Roles alternate: the natural role on odd
sub-games, the opposite on even ones — so when we are cop the opponent is thief.
"""

from dataclasses import dataclass, field

from ..shared.sysinfo import system_spec
from .negotiate import Negotiator
from .runtime import SubGameRuntime
from .scoring import role_for


def identity_for(
    group: str,
    repos: dict | None = None,
    mcp_servers: dict | None = None,
    members: list | None = None,
    llm_model: str = "template",
) -> dict:
    """This peer's static per-GROUP identity, exchanged in the handshake (roles alternate)."""
    return {
        "group_id": group,
        "group_name": group,
        "members": members or [],
        "repos": repos or {"cop": "local", "thief": "local"},
        "mcp_servers": mcp_servers or {},
        "llm_model": llm_model,
        "spec": system_spec(),
    }


@dataclass
class SeriesResult:
    summaries: list = field(default_factory=list)
    own_identity: dict = field(default_factory=dict)
    peer_identity: dict = field(default_factory=dict)
    game_id: str | None = None
    game_uid: str | None = None


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
) -> SeriesResult:
    """Play our side of a whole series against a real opponent."""
    own_identity = own_identity or identity_for(group)
    result = SeriesResult(own_identity=own_identity)
    known_opponent: str | None = None
    for n in range(1, num_games + 1):
        role = role_for(natural_role, n)
        negotiator = Negotiator(terms, own_identity, group)
        peer_msg = transport.exchange_agreement(
            negotiator.signed(role, n, opponent_group=known_opponent).to_wire()
        )
        agreed = negotiator.verify_peer(peer_msg)
        result.game_id, result.game_uid = agreed.game_id, agreed.game_uid
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
    return result
