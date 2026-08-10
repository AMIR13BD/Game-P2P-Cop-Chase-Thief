"""Series-level consensus digest: the canonical SHA-256 that BOTH peers independently
compute AND explicitly exchange before ``mutual_agreement.confirmed`` may become true.

AGREED preimage (verbatim with uoh-ay26): the top-level object is EXACTLY
``{game_id, game_uid, sub_games}`` and each sub-game is EXACTLY
``{sub_game_number, result, roles, score, winner_group}`` — ordered strictly g01->g06.
It deliberately EXCLUDES steps, tie, timestamps, tokens, filenames, git commits, audit
metadata, capture evidence and final totals (all local-only or derivable). ``roles`` and
``score`` are keyed by GROUP so sorted-key JSON is byte-identical on both sides. A local
hash is never sufficient: confirmation needs the PEER's digest to arrive and match ours.
"""

import hashlib

from ..domain.crypto import canonical_json
from .scoring import score_for

# EXACTLY these five keys per sub-game, in the agreed consensus preimage (never steps/tie).
CANON_SUB_KEYS = ("sub_game_number", "result", "roles", "score", "winner_group")


def canonical_rows(summaries: list, ours: str, theirs: str) -> list:
    """The per-sub-game consensus facts, keyed by GROUP so both peers hash identically."""
    rows = []
    for s in summaries:
        outcome, our_role = s["result"], s["role"]
        their_role = "thief" if our_role == "police" else "police"
        so, st = score_for(outcome, our_role), score_for(outcome, their_role)
        rows.append(
            {
                "sub_game_number": s["sub_game_number"],
                "result": outcome,
                "roles": {ours: our_role, theirs: their_role},
                "score": {ours: so, theirs: st},
                "winner_group": (ours if so > st else (theirs if st > so else None)),
            }
        )
    return rows


def preimage(game_id: str, game_uid: str, rows: list) -> dict:
    """The AGREED consensus object: EXACTLY {game_id, game_uid, sub_games}, each sub-game
    reduced to EXACTLY ``CANON_SUB_KEYS`` and the array ordered strictly g01->g06. ``rows``
    may carry extra keys (e.g. full result rows); everything outside the agreed keys is dropped.
    """
    sub_games = [
        {k: r[k] for k in CANON_SUB_KEYS} for r in sorted(rows, key=lambda r: r["sub_game_number"])
    ]
    return {"game_id": game_id, "game_uid": game_uid, "sub_games": sub_games}


def consensus_sha(game_id: str, game_uid: str, rows: list) -> str:
    """SHA-256 over the canonical bytes of the AGREED preimage (identical on both peers)."""
    canon = preimage(game_id, game_uid, rows)
    return hashlib.sha256(canonical_json(canon).encode("utf-8")).hexdigest()
