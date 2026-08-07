"""The four official submission artifacts (book App. F table 20): declaration, config,
log, result — written as canonical bytes, joinable on the shared game_id/game_uid. The
result's per-sub-game scores and aggregates use the official scoring so two peers' result
files agree on the cross-team join (kit ``tools/check_artifacts.py``).
"""

import hashlib

from ..domain.crypto import canonical_json
from . import ids
from .scoring import aggregate, is_tie_row, score_for

SCHEMA_VERSION = "1.1"


def _canon_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _hw(spec: dict) -> dict:
    return {
        "cpu_type": spec.get("cpu_type"),
        "cpu_freq_mhz": spec.get("cpu_freq_mhz"),
        "cpu_cores": spec.get("cpu_cores"),
        "ram_gb": spec.get("ram_gb"),
        "gpu_model": spec.get("gpu_type"),
        "vram_gb": spec.get("vram_gb"),
    }


def _group_block(identity: dict) -> dict:
    return {
        "group_id": identity["group_id"],
        "group_name": identity.get("group_name", ""),
        "members": identity.get("members", []),
        "repos": identity.get("repos", {}),
        "mcp_servers": identity.get("mcp_servers", {}),
        "llm_model": identity.get("llm_model", ""),
        "hardware_spec": _hw(identity.get("spec", {})),
    }


def build_declaration(gid, guid, own, peer, num_sub_games, started="", ended="") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "declaration_type": "pre_game_declaration",
        "game_id": gid,
        "game_uid": guid,
        "links": ids.links(gid),
        "timezone": "UTC",
        "game_started_at": started,
        "game_ended_at": ended,
        "num_sub_games": num_sub_games,
        "max_tokens_per_game": 0,
        "groups": {"group_1": _group_block(own), "group_2": _group_block(peer)},
    }


def build_config(terms, gid, guid, n) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "game_id": gid,
        "game_uid": guid,
        "sub_game_number": n,
        "links": ids.links(gid),
        "terms": terms,
        "config_name": ids.config_name(gid, n),
        "config_sha256": _canon_hash(terms),
    }


def build_log(summary, gid, guid, group_id, opponent) -> dict:
    records = summary["records"]
    audit = summary["audit"]
    log_summary = {
        "sub_game_number": summary["sub_game_number"],
        "group_id": group_id,
        "role": summary["role"],
        "opponent_group_id": opponent,
        "result": summary["result"],
        "winner_role": summary["winner"],
        "steps": summary["steps"],
        "started_at": summary["started_at"],
        "duration_seconds": summary["duration_seconds"],
        "tokens_total": summary["tokens_total"],
        "audit": audit,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "game_id": gid,
        "game_uid": guid,
        "links": ids.links(gid),
        "summary": log_summary,
        "records": records,
        "mutual_agreement": {
            "opponent_group_id": opponent,
            "sha256": _canon_hash({"records": records}),
            "confirmed": bool(audit.get("log_verified")),
        },
    }


def _result_rows(summaries, ours, theirs) -> list:
    rows = []
    for s in summaries:
        outcome, our_role = s["result"], s["role"]
        their_role = "thief" if our_role == "police" else "police"
        so, st = score_for(outcome, our_role), score_for(outcome, their_role)
        rows.append(
            {
                "sub_game_number": s["sub_game_number"],
                "roles": {ours: our_role, theirs: their_role},
                "result": outcome,
                "score": {ours: so, theirs: st},
                "winner_group": (ours if so > st else (theirs if st > so else None)),
                "tie": is_tie_row(outcome, so, st),
                "tokens": {ours: 0, theirs: 0},
                "audit": {
                    "log_verified": bool(s["audit"].get("log_verified")),
                    "tampered": bool(s["audit"].get("tampered")),
                },
            }
        )
    return rows


def build_result(gid, guid, ours, theirs, summaries) -> dict:
    rows = _result_rows(summaries, ours, theirs)
    final = {
        **aggregate(rows, ours, theirs),
        "games_played_including_this": {ours: 0, theirs: None},
        "first_meeting_between_groups": True,
        "diversity_reward_applied": {ours: False, theirs: False},
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "report_type": "final_game_result",
        "game_id": gid,
        "game_uid": guid,
        "links": ids.links(gid),
        "timezone": "UTC",
        "groups": [ours, theirs],
        "num_sub_games": len(rows),
        "sub_games": rows,
        "final_result": final,
    }
