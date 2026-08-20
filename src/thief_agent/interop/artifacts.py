"""The four official submission artifacts (App. F table 20) — declaration, config, log,
result — canonical bytes joinable on game_id/game_uid; official scoring so peers agree."""

from . import ids
from .artifacts_util import canon_hash, hardware_block
from .scoring import aggregate, is_tie_row, score_for

SCHEMA_VERSION = "1.1"
# The agreed LLM token ceiling for a series (book App. F table 18, [aomdan tokens la-sidra];
# the same value the shared config/game.json carries as token_budget_per_series). It is the
# DECLARED cap — actual consumption is reported per sub-game and per series in the result.
AGREED_TOKEN_BUDGET = 200_000


def group_block(identity: dict) -> dict:
    """One group's static declaration block: identity, members, repos, MCP servers, model and
    hardware spec (book §9.3.3 — the mandatory report carries these for both groups)."""
    commit = identity.get("github_commit") or identity.get("git_commit_hash", "")
    return {
        "group_id": identity.get("group_id", ""),  # never crash artifact emission on a thin peer
        "group_name": identity.get("group_name", ""),
        "git_commit_hash": commit,
        "github_commit": commit,
        # Additive (see ``rolecommit``): each role's own repo SHA, as that side declared them.
        "github_commits": identity.get("github_commits", {}),
        "members": identity.get("members", []),
        "repos": identity.get("repos", {}),
        "mcp_servers": identity.get("mcp_servers", {}),
        "llm_model": identity.get("llm_model", ""),
        "hardware_spec": hardware_block(identity.get("spec", {})),
    }


def build_declaration(
    gid, guid, own, peer, num_sub_games, started="", ended="", max_tokens=AGREED_TOKEN_BUDGET
) -> dict:
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
        "max_tokens_per_game": max_tokens,  # the agreed ceiling (book ch.9 pre-game declaration)
        "groups": {"group_1": group_block(own), "group_2": group_block(peer)},
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
        "config_sha256": canon_hash(terms),
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
            "sha256": canon_hash({"records": records}),
            "confirmed": bool(audit.get("log_verified")),
        },
    }


def _result_rows(summaries, ours, theirs, commits) -> list:
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
                # Our real consumption for this sub-game (book App. E rule 54). The peer
                # reports its own in its own result: we never invent a number for it.
                "tokens": {ours: int(s.get("tokens_total") or 0), theirs: 0},
                # Both sides per SUB-GAME (rule 53): the SHA of the repo that played THIS
                # role. Ours is stamped by the series; the series-wide value is the fallback.
                "github_commit": {
                    ours: s.get("own_github_commit") or commits.get(ours, ""),
                    theirs: s.get("peer_github_commit") or commits.get(theirs, ""),
                },
                "audit": {
                    "log_verified": bool(s["audit"].get("log_verified")),
                    "tampered": bool(s["audit"].get("tampered")),
                    "local_result_claim": s["audit"].get("local_result_claim"),
                    "peer_result_claim": s["audit"].get("peer_result_claim"),
                    "result_agreed": bool(s["audit"].get("result_agreed")),
                },
            }
        )
    return rows


def build_result(gid, guid, ours, theirs, summaries, commits=None) -> dict:
    rows = _result_rows(summaries, ours, theirs, commits or {})
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
