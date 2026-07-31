"""Final result artifact: per-sub-game rows, series summary, mutual-agreement hash."""

import hashlib

from ..domain.crypto import canonical_json
from . import ids


def _winner(roles: dict, outcome: str) -> str | None:
    inv = {v: k for k, v in roles.items()}
    if outcome == "capture":
        return inv.get("police")
    if outcome == "survival":
        return inv.get("thief")
    return None


def build_result(
    gid: str, groups: list, sub_games: list, github_commits: dict, repos: dict
) -> dict:
    total = dict.fromkeys(groups, 0)
    won = dict.fromkeys(groups, 0)
    ties = 0
    entries = []
    for sg in sub_games:
        for g in groups:
            total[g] += sg["scores"][g]
        w = _winner(sg["roles"], sg["outcome"])
        tie = sg["outcome"] == "technical"
        ties += 1 if tie else 0
        if w:
            won[w] += 1
        entries.append(
            {
                "sub_game_number": sg["sub_game_number"],
                "roles": sg["roles"],
                "result": sg["outcome"],
                "winner_group": w,
                "tie": tie,
                "github_commit": github_commits,
                "tokens": dict.fromkeys(groups, 0),
                "score": sg["scores"],
                "log_files": dict.fromkeys(groups, sg["log_file"]),
                "config_sha256": sg["config_sha256"],
                "log_sha256": sg["log_sha256"],
                "audit": {"log_verified": sg["audit_passed"], "tampered": not sg["audit_passed"]},
            }
        )
    series_tie = len(set(total.values())) == 1
    final = {
        "total_score": total,
        "sub_games_won": won,
        "ties": ties,
        "winner_group": None if series_tie else max(total, key=total.get),
        "series_tie": series_tie,
        "tokens_total_series": dict.fromkeys(groups, 0),
    }
    res = {
        "schema_version": "1.2",
        "report_type": "final_game_result",
        "game_id": gid,
        "game_uid": ids.game_uid(gid),
        "links": ids.links(gid),
        "timezone": "UTC",
        "groups": list(groups),
        "repos": repos,
        "num_sub_games": len(sub_games),
        "sub_games": entries,
        "final_result": final,
    }
    res["mutual_agreement"] = {
        "sha256": hashlib.sha256(canonical_json(final).encode("utf-8")).hexdigest(),
        "confirmed": True,
    }
    return res
