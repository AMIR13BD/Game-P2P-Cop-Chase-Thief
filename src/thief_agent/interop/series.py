"""A SERIES of N sub-games between two peers with role alternation.

The transport/servers are built once by the caller and reused across sub-games; each
sub-game runs a fresh handshake and runtime. Roles alternate: the natural role on odd
sub-games, the opposite on even ones — so when we are cop the opponent is thief.
"""

import time
from dataclasses import dataclass, field

from ..exceptions import NetworkError
from .consensus import LEGACY, canonical_rows, consensus_sha
from .negotiate import Negotiator
from .runtime import SubGameRuntime
from .scoring import role_for
from .series_parts import (
    _dropped_summary,
    _peer_commit,
    identity_for,
    mcp_servers_for,
)
from .wire import AuditPayload

_CONSENSUS_TAG = "series_consensus"  # exact result_claim tag agreed with the peer


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
    consensus_profile: str = LEGACY  # which settlement envelope this series hashed under


def _exchange_consensus(transport, our_role, peer_role, our_sha, turn_timeout) -> str | None:
    """Send OUR digest and (bounded) wait for the PEER's over the final-audit channel. Envelope
    is the agreed one: sender = OUR wire role, result_claim = ``series_consensus``, records = [].
    Accept the peer's digest ONLY when its envelope matches EXACTLY; else fail safe (-> None)."""
    ours = AuditPayload(our_role, [], _CONSENSUS_TAG, consensus_sha=our_sha).to_wire()
    transport.send_audit(ours)
    deadline = time.monotonic() + min(turn_timeout, 15.0)
    while True:
        if deadline - time.monotonic() <= 0:
            return None
        msg = transport.poll_audit(deadline - time.monotonic())
        if msg is None:
            return None
        peer = AuditPayload.from_wire(msg)
        if peer.consensus_sha is None:
            continue  # a straggler per-sub-game audit (no digest): keep draining
        # The series-consensus envelope is labelled with the peer's WIRE ROLE. Some peers use
        # their NATURAL (sub-game-1) role, others the role they played in the LAST sub-game; for
        # an even-length series those differ (roles alternate), so accept EITHER of the peer's two
        # wire roles. The digest EQUALITY (checked by the caller) is what actually confirms
        # agreement — a role-label convention difference must not drop a valid, matching digest.
        peer_wire_roles = (peer_role, "police" if peer_role == "thief" else "thief")
        ok = (
            peer.result_claim == _CONSENSUS_TAG
            and peer.sender in peer_wire_roles
            and peer.records == []
        )
        return peer.consensus_sha if ok else None  # wrong envelope -> reject; caller checks SHA eq


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
    consensus_profile: str = LEGACY,
) -> SeriesResult:
    """Play our side of a whole series against a real opponent.

    ``game_id`` optionally OVERRIDES the derived filename base with a peer-agreed value
    (Table 20); ``game_uid`` is always the derived crypto id and is never overridden.
    ``consensus_profile`` selects the settlement envelope, agreed per pairing out of band
    and never in the signed terms; ``legacy`` keeps every filed digest reproducible."""
    own_identity = own_identity or identity_for(group, github_commit=github_commit)
    result = SeriesResult(own_identity=own_identity, consensus_profile=consensus_profile)
    known_opponent: str | None = None
    for n in range(1, num_games + 1):
        role = role_for(natural_role, n)
        runtime = None
        try:
            negotiator = Negotiator(terms, own_identity, group, known_opponent)
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
            # THIS sub-game's peer runtime SHA, from the peer's own declaration.
            peer_commit = _peer_commit(agreed.opponent_identity, peer_msg)
            runtime = SubGameRuntime(
                role, terms, transport, group, github_commit, n, seed, listener
            )
            summary = runtime.run(turn_timeout=turn_timeout)
            # Persist per sub-game (reporting only). A peer that declares no commit in its
            # identity still reveals one in its signed Step-0 audit record (book ch.5.5); that
            # reveal is this sub-game's own, so it is used only as a fallback — never invented.
            summary["peer_github_commit"] = peer_commit or summary.get(
                "peer_github_commit_step0", ""
            )
        except NetworkError:  # one sub-game's transport failure must not abort the whole series
            summary = _dropped_summary(n, role, runtime)
        result.summaries.append(summary)
    # After the series: per-sub-game result agreement, then an explicit peer-digest EXCHANGE.
    theirs = result.peer_identity.get("group_id", "")
    rows = canonical_rows(result.summaries, group, theirs)
    gid, guid = result.game_id or "", result.game_uid or ""
    result.consensus_sha = consensus_sha(gid, guid, rows, consensus_profile)
    result.results_agreed = bool(result.summaries) and all(
        s["audit"].get("result_agreed", False) for s in result.summaries
    )
    # The consensus envelope uses WIRE ROLES (not group ids): ours is our natural role.
    peer_role = "thief" if natural_role == "police" else "police"
    result.peer_consensus_sha = _exchange_consensus(
        transport, natural_role, peer_role, result.consensus_sha, turn_timeout
    )
    result.sha_match = (
        result.peer_consensus_sha is not None and result.peer_consensus_sha == result.consensus_sha
    )
    return result


__all__ = ["SeriesResult", "identity_for", "mcp_servers_for", "run_series"]
