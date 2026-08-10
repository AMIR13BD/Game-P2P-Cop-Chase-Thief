"""Shape the friendly result to the reference submission schema: add top-level
``mutual_agreement``, ``links.github`` and per-sub-game timing (``started_at`` /
``ended_at`` / ``steps`` / ``log_files``). ADDITIVE only — scores, roles, audit and
github_commit are untouched; used for the friendly/demo result export.
"""

import hashlib
from datetime import datetime, timedelta

from ..domain.crypto import canonical_json
from . import ids

# The reference result's final_result keys — the export is pruned to EXACTLY these so the
# demo JSON is key-for-key identical to the reference. Scoring still computes every value;
# we only omit our extra analytics keys from the serialized shape (no calculation change).
_REF_FINAL_KEYS = (
    "series_tie",
    "sub_games_won",
    "ties",
    "tokens_total_series",
    "total_score",
    "winner_group",
)


# Only the mutually-agreed gameplay facts go into the shared fingerprint (never tokens /
# github_commit / timestamps, which are local-only and may legitimately differ or be absent).
_CANON_SUB_KEYS = ("sub_game_number", "result", "winner_group", "roles", "score", "steps")


def _canonical_fingerprint(game_uid: str, sub_games: list) -> str:
    canon = {
        "game_uid": game_uid,
        "sub_games": [{k: row[k] for k in _CANON_SUB_KEYS if k in row} for row in sub_games],
    }
    return hashlib.sha256(canonical_json(canon).encode("utf-8")).hexdigest()


def _mutual_clean(sub_games: list) -> bool:
    """True iff every sub-game's PEER log verified untampered (our post-mortem mutual audit)."""
    return bool(sub_games) and all(
        r["audit"]["log_verified"] and not r["audit"]["tampered"] for r in sub_games
    )


def _ended(started: str, secs) -> str:
    try:
        return (datetime.fromisoformat(started) + timedelta(seconds=float(secs))).isoformat()
    except (ValueError, TypeError):
        return started or ""


def enrich_result(result_doc: dict, summaries: list, own: dict, peer: dict) -> dict:
    """Augment a built friendly result IN PLACE so its structure matches the reference."""
    gid = result_doc["game_id"]
    ours, theirs = result_doc["groups"]
    by_n = {s["sub_game_number"]: s for s in summaries}
    for row in result_doc["sub_games"]:
        n = row["sub_game_number"]
        s = by_n.get(n, {})
        row["started_at"] = s.get("started_at", "")
        row["ended_at"] = _ended(row["started_at"], s.get("duration_seconds", 0))
        row["steps"] = s.get("steps", 0)
        row["log_files"] = {ours: ids.log_name(gid, n), theirs: ids.log_name(gid, n)}
    result_doc["links"]["github"] = {ours: own.get("repos", {}), theirs: peer.get("repos", {})}
    # Mutual agreement (book §5.4) is reached when BOTH peers independently validate the SAME
    # signed series. Each side computes a CANONICAL fingerprint over only the mutually-agreed
    # facts — game_uid + per-sub-game number/result/winner/roles/score/steps — deliberately
    # EXCLUDING local-only fields (tokens, github_commit, timestamps) that legitimately differ
    # or may be unavailable, so both sides hash byte-identical input. ``confirmed`` reflects
    # OUR post-mortem verification of the PEER's revealed records (not our own audit of
    # ourselves): true iff every sub-game's peer log verified untampered. It is never forced —
    # both reports independently reach confirmed=true with the SAME sha256 only when both
    # cleanly verified each other, which is exactly the joint sign-off the lecturer compares.
    result_doc["mutual_agreement"] = {
        "confirmed": _mutual_clean(result_doc["sub_games"]),
        "sha256": _canonical_fingerprint(result_doc["game_uid"], result_doc["sub_games"]),
    }
    fr = result_doc.get("final_result", {})
    result_doc["final_result"] = {k: fr[k] for k in _REF_FINAL_KEYS if k in fr}
    return result_doc
