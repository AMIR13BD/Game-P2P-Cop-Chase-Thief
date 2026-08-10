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
    # Mutual agreement is a JOINT property (book §5.4): it is true only when BOTH peers
    # independently validate the SAME signed series. One team cannot assert it, so a
    # unilaterally-generated friendly/demo report NEVER forces confirmed=true from our own
    # clean audit — it stays False until a real two-peer confirmation exchange proves it.
    # sha256 is our aggregate's fingerprint, published for the peer to compare against theirs.
    result_doc["mutual_agreement"] = {
        "confirmed": False,
        "sha256": hashlib.sha256(
            canonical_json({"sub_games": result_doc["sub_games"]}).encode("utf-8")
        ).hexdigest(),
    }
    fr = result_doc.get("final_result", {})
    result_doc["final_result"] = {k: fr[k] for k in _REF_FINAL_KEYS if k in fr}
    return result_doc
