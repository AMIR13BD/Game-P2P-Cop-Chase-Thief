"""Series-level consensus digest: the canonical SHA-256 that BOTH peers independently
compute AND explicitly exchange before ``mutual_agreement.confirmed`` may become true.

The per-sub-game row is the same five keys in every profile — ``CANON_SUB_KEYS``, which
is also the lecturer reference's own symmetric row. It deliberately EXCLUDES steps, tie,
timestamps, tokens, filenames, git commits, audit metadata, capture evidence and final
totals (all local-only or derivable). ``roles`` and ``score`` are keyed by GROUP so
sorted-key JSON is byte-identical on both sides. A local hash is never sufficient:
confirmation needs the PEER's digest to arrive and match ours.

What a profile selects is the ENVELOPE around that row, and there are two live ones. They
differ in two independent ways at once, which is the trap — changing only one of the two
produces a third digest that matches nobody:

* ``legacy`` — ``{game_id, game_uid, sub_games}`` under the compact §2 form. This is what
  our filed counted series (G002, G020) settled under and what those opponents agreed. It
  is the DEFAULT and must stay that way: moving it would invalidate reports already sent.
* ``official_reference_v1`` — ``{game_id, aggregate, sub_games}`` serialized with
  ``json.dumps(sort_keys=True, ensure_ascii=False)`` and its DEFAULT (spaced) separators,
  reproducing the lecturer reference's ``report_writer.consensus_signature`` exactly.

The profile is agreed per pairing and travels out of band, never inside the 14 signed
terms — adding a key there would break the terms signature for both peers.
"""

import hashlib
import json

from ..domain.crypto import canonical_json
from .scoring import TIE_SCORE, score_for

# EXACTLY these five keys per sub-game, in every profile (never steps/tie).
CANON_SUB_KEYS = ("sub_game_number", "result", "roles", "score", "winner_group")

LEGACY = "legacy"
OFFICIAL_REFERENCE_V1 = "official_reference_v1"
PROFILES = (LEGACY, OFFICIAL_REFERENCE_V1)

# The reference's aggregate block, in its own key order-independent form.
_AGG_KEYS = ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")


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


def reference_aggregate(rows: list) -> dict:
    """The lecturer reference's series aggregate, re-derived from the consensus rows.

    Independently re-implemented from the reference's documented algorithm, and it is NOT
    our own ``scoring.aggregate``: the reference counts ANY equal-score row as a tie
    (a 0-0 timeout included), while ours excludes zeroed outcomes. That difference is
    invisible on a clean series and decides the digest on one that timed out, so the
    reference profile must use the reference's own counting to reproduce its bytes.
    """
    scores = [r.get("score", {}) for r in rows]
    groups = sorted({g for s in scores for g in s})
    total = {g: sum(s.get(g, 0) for s in scores) for g in groups}
    won = dict.fromkeys(groups, 0)
    ties = 0
    for s in scores:
        if not s:
            continue
        top = max(s.values())
        winners = [g for g, v in s.items() if v == top]
        if len(winners) == 1:
            won[winners[0]] += 1
        else:
            ties += 1
    if len(groups) == 2 and total[groups[0]] == total[groups[1]]:
        return {
            "total_score": {g: v + TIE_SCORE for g, v in total.items()},
            "sub_games_won": won,
            "ties": ties,
            "winner_group": None,
            "series_tie": True,
        }
    winner = max(total, key=lambda k: total[k]) if total else None
    return {
        "total_score": total,
        "sub_games_won": won,
        "ties": ties,
        "winner_group": winner,
        "series_tie": False,
    }


def preimage(game_id: str, game_uid: str, rows: list, profile: str = LEGACY) -> dict:
    """The agreed consensus object for ``profile``, rows reduced to ``CANON_SUB_KEYS``
    and ordered strictly g01->g06. ``rows`` may carry extra keys; they are dropped."""
    if profile not in PROFILES:
        raise ValueError(f"unknown consensus profile {profile!r}; expected one of {PROFILES}")
    ordered = sorted(rows, key=lambda r: r["sub_game_number"])
    sub_games = [{k: r[k] for k in CANON_SUB_KEYS} for r in ordered]
    if profile == OFFICIAL_REFERENCE_V1:
        aggregate = {k: reference_aggregate(ordered)[k] for k in _AGG_KEYS}
        return {"game_id": game_id, "aggregate": aggregate, "sub_games": sub_games}
    return {"game_id": game_id, "game_uid": game_uid, "sub_games": sub_games}


def serialize(canon: dict, profile: str = LEGACY) -> str:
    """The profile's serialization. The reference signs a SPACED form — the only hash in
    the release that does not use the compact §2 separators."""
    if profile == OFFICIAL_REFERENCE_V1:
        return json.dumps(canon, sort_keys=True, ensure_ascii=False)
    return canonical_json(canon)


def consensus_sha(game_id: str, game_uid: str, rows: list, profile: str = LEGACY) -> str:
    """SHA-256 over the canonical bytes of the agreed preimage (identical on both peers)."""
    canon = preimage(game_id, game_uid, rows, profile)
    return hashlib.sha256(serialize(canon, profile).encode("utf-8")).hexdigest()
