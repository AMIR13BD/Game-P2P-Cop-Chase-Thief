"""The mandatory field lists an official ``result_<game_id>.json`` must carry.

Split out of ``compliance.py`` purely to keep each module inside the repository's
150-line ceiling. The tuples are verbatim, so exactly the same fields are required and
exactly the same reports pass or fail. Sources are cited in ``compliance.py``.
"""

REQUIRED_TOP = (
    "schema_version",
    "report_type",
    "game_id",
    "game_uid",
    "groups",
    "num_sub_games",
    "sub_games",
    "final_result",
    "mutual_agreement",
    "links",
    "timezone",
    "game_started_at",
    "game_ended_at",
    "group_details",
)
REQUIRED_ROW = (
    "sub_game_number",
    "roles",
    "result",
    "winner_group",
    "score",
    "tokens",
    "github_commit",
    "audit",
    "steps",
    "started_at",
    "ended_at",
    "log_files",
)
REQUIRED_FINAL = (
    "total_score",
    "sub_games_won",
    "ties",
    "winner_group",
    "series_tie",
    "tokens_total_series",
)
REQUIRED_AGREEMENT = ("sha256", "peer_sha256", "sha_match", "results_agreed", "confirmed")
GROUP_DETAIL_FIELDS = ("members", "repos", "mcp_servers", "hardware_spec")  # §9.3.3
OFFICIAL_SUB_GAMES = 6  # App. F table 18 row 1 (status: fixed)
