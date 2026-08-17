"""Shape the result to the mandatory report schema of book ch.9: top-level
``mutual_agreement`` (SHA-256 backed), the four GitHub links of both groups (App. E rule 49),
each group's identity / MCP / hardware declaration (§9.3.3), the game timestamps, and
per-sub-game timing (``started_at`` / ``ended_at`` / ``steps`` / ``log_files``). ADDITIVE
only — scores, roles, audit, tokens and github_commit are untouched, and nothing here enters
the canonical consensus preimage.
"""

from datetime import datetime, timedelta

from . import ids
from .artifacts import group_block
from .consensus import LEGACY, consensus_sha

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


def _canonical_fingerprint(gid: str, guid: str, sub_games: list, profile: str = LEGACY) -> str:
    """OUR side of the AGREED consensus digest; the shared ``interop.consensus`` builder is the
    single source of truth (identical bytes on both peers) and owns the per-pairing profile."""
    return consensus_sha(gid, guid, sub_games, profile)


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


def _results_agreed(sub_games: list) -> bool:
    """True iff EVERY sub-game's local result_claim equalled the peer's (recorded in audit)."""
    return bool(sub_games) and all(r["audit"].get("result_agreed") for r in sub_games)


def enrich_result(
    result_doc: dict, summaries: list, own: dict, peer: dict, consensus: dict | None = None
) -> dict:
    """Augment a built friendly result IN PLACE so its structure matches the reference.

    ``consensus`` carries the SERIES digest exchange (our sha, the peer's received sha, and
    whether they matched). ``confirmed`` requires ALL of: every peer log verified untampered,
    every sub-game's result mutually agreed, AND an actually-received peer digest that matches
    ours — a locally-computed hash alone is never sufficient (book §5.4 mutual sign-off).
    """
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
    # App. E rule 49 / §9.4: the attached JSON carries FOUR repository links — each group's
    # cop and thief repo — taken from the identity each side declared in the handshake.
    result_doc["links"]["github"] = {ours: own.get("repos", {}), theirs: peer.get("repos", {})}
    # §9.3.3: the mandatory report also carries each group's identity, MCP addresses, hardware
    # declaration and model, plus the game timestamps. Same blocks as the declaration.
    result_doc["group_details"] = {"group_1": group_block(own), "group_2": group_block(peer)}
    rows = result_doc["sub_games"]
    result_doc["game_started_at"] = rows[0]["started_at"] if rows else ""
    result_doc["game_ended_at"] = rows[-1]["ended_at"] if rows else ""
    c = consensus or {}
    logs_clean = _mutual_clean(result_doc["sub_games"])
    results_agreed = _results_agreed(result_doc["sub_games"])
    sha_match = bool(c.get("sha_match"))
    local_sha = c.get("sha256") or _canonical_fingerprint(
        result_doc["game_id"],
        result_doc["game_uid"],
        result_doc["sub_games"],
        c.get("profile", LEGACY),
    )
    result_doc["mutual_agreement"] = {
        "confirmed": logs_clean and results_agreed and sha_match,
        "sha256": local_sha,
        "peer_sha256": c.get("peer_sha256"),
        "sha_match": sha_match,
        "results_agreed": results_agreed,
    }
    fr = result_doc.get("final_result", {})
    result_doc["final_result"] = {k: fr[k] for k in _REF_FINAL_KEYS if k in fr}
    return result_doc
