"""Shape the internal counted result into the ONE final submission result — structurally
identical to the reference result schema.

Our audit-only keys (per-sub-game ``config_sha256``/``log_sha256``, ``mutual_agreement``
``mode``/``confirmations``/``signatures``, and top-level ``repos``) are dropped from the
FINAL result. They remain in the config/log/declaration artifacts and are verified BEFORE
this runs, so no audit check is weakened. The reference's ``links.github`` and per-sub-game
timing keys are added; per-game timestamps are not tracked by the counted path, so they are
left empty (never fabricated). ``steps`` is real (from the series).
"""

_SUB_KEEP = (
    "sub_game_number",
    "roles",
    "result",
    "winner_group",
    "tie",
    "github_commit",
    "tokens",
    "score",
    "log_files",
    "audit",
)


def shape_official_result(full: dict, steps_by_n: dict) -> dict:
    groups = list(full["groups"])
    subs = []
    for e in full["sub_games"]:
        row = {k: e[k] for k in _SUB_KEEP if k in e}
        row["started_at"] = ""  # not tracked by the counted path — never fabricated
        row["ended_at"] = ""
        row["steps"] = int(steps_by_n.get(e["sub_game_number"], 0))
        subs.append(row)
    links = dict(full["links"])
    links["github"] = {g: full.get("repos", {}).get(g, {}) for g in groups}
    ma = full["mutual_agreement"]
    return {
        "final_result": full["final_result"],
        "game_id": full["game_id"],
        "game_uid": full["game_uid"],
        "groups": groups,
        "links": links,
        "mutual_agreement": {"confirmed": ma["confirmed"], "sha256": ma["sha256"]},
        "num_sub_games": full["num_sub_games"],
        "report_type": full["report_type"],
        "schema_version": full["schema_version"],
        "sub_games": subs,
        "timezone": full["timezone"],
    }
