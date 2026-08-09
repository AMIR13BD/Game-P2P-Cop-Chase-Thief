"""The friendly/demo result, after submission-shaping, matches the reference result
schema (STRUCTURE only): top-level keys, links, mutual_agreement and each sub_games item.
Key sets are pinned here (from the reference result_G002.json) so the test is CI-safe."""

from thief_agent.interop.artifacts import build_result
from thief_agent.interop.submission import enrich_result

TOP = {
    "final_result",
    "game_id",
    "game_uid",
    "groups",
    "links",
    "mutual_agreement",
    "num_sub_games",
    "report_type",
    "schema_version",
    "sub_games",
    "timezone",
}
LINKS = {"config", "declaration", "github", "log", "result"}
MA = {"confirmed", "sha256"}
FINAL = {
    "series_tie",
    "sub_games_won",
    "ties",
    "tokens_total_series",
    "total_score",
    "winner_group",
}
SUB = {
    "audit",
    "ended_at",
    "github_commit",
    "log_files",
    "result",
    "roles",
    "score",
    "started_at",
    "steps",
    "sub_game_number",
    "tie",
    "tokens",
    "winner_group",
}


def _summaries():
    return [
        {
            "sub_game_number": i + 1,
            "result": "capture",
            "role": "police" if i % 2 == 0 else "thief",
            "audit": {"log_verified": True, "tampered": False},
            "started_at": "2026-01-01T00:00:00+00:00",
            "duration_seconds": 5,
            "steps": 12,
        }
        for i in range(6)
    ]


def _ident(group):
    return {"group_id": group, "repos": {"cop": "u", "thief": "v"}, "github_commit": "a" * 40}


def _enriched():
    doc = build_result(
        "G", "U", "amireman", "opp", _summaries(), {"amireman": "a" * 40, "opp": "b" * 40}
    )
    return enrich_result(doc, _summaries(), _ident("amireman"), _ident("opp"))


def test_enriched_result_matches_reference_top_and_nesting():
    doc = _enriched()
    assert set(doc) == TOP
    assert set(doc["links"]) == LINKS
    assert set(doc["mutual_agreement"]) == MA
    assert set(doc["final_result"]) == FINAL  # no extra analytics keys in the export


def test_enriched_sub_games_item_matches_reference():
    row = _enriched()["sub_games"][0]
    assert set(row) == SUB
    assert set(row["github_commit"]) == {"amireman", "opp"}
    assert set(row["roles"]) == {"amireman", "opp"}
    assert set(row["log_files"]) == {"amireman", "opp"}


def test_links_github_is_per_group_repo_map():
    gh = _enriched()["links"]["github"]
    assert set(gh) == {"amireman", "opp"}
    assert set(gh["amireman"]) == {"cop", "thief"}
