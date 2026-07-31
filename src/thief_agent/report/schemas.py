"""Structural schema of record for the four mandatory artifacts (fail closed).

This validator is authoritative for artifact structure; the config game-terms block
additionally conforms to schemas/config.schema.json (checked in the test-suite)."""

from ..exceptions import ArtifactError

GROUP_FIELDS = (
    "group_id",
    "group_name",
    "members",
    "repos",
    "mcp_servers",
    "llm_model",
    "hardware_spec",
    "signature",
)

REQUIRED = {
    "declaration": [
        "schema_version",
        "declaration_type",
        "game_id",
        "game_uid",
        "links",
        "num_sub_games",
        "max_tokens_per_game",
        "groups",
    ],
    "config": [
        "schema_version",
        "agreed_between",
        "board_and_agents",
        "movement_and_barriers",
        "scoring",
        "pheromones",
        "network_and_league",
        "rate_limiter_gatekeeper",
        "game_id",
        "game_uid",
        "sub_game_number",
        "config_name",
        "config_sha256",
    ],
    "log": ["schema_version", "game_id", "game_uid", "sub_game_number", "summary", "records"],
    "result": [
        "schema_version",
        "report_type",
        "game_id",
        "game_uid",
        "groups",
        "num_sub_games",
        "sub_games",
        "final_result",
        "mutual_agreement",
    ],
}


def validate(kind: str, obj: object) -> dict:
    if kind not in REQUIRED:
        raise ArtifactError(f"unknown artifact kind '{kind}'")
    if not isinstance(obj, dict):
        raise ArtifactError(f"{kind} artifact is not an object")
    missing = [k for k in REQUIRED[kind] if k not in obj]
    if missing:
        raise ArtifactError(f"{kind} artifact missing fields {missing}")
    if kind == "declaration":
        groups = obj["groups"]
        if not isinstance(groups, dict) or not groups:
            raise ArtifactError("declaration groups malformed")
        for grp in groups.values():
            if not isinstance(grp, dict) or any(k not in grp for k in GROUP_FIELDS):
                raise ArtifactError("declaration group missing mandated fields")
    if kind == "log":
        s = obj["summary"]
        if not isinstance(s, dict) or "audit" not in s or not isinstance(obj["records"], list):
            raise ArtifactError("log summary/audit/records malformed")
    if kind == "result":
        ma = obj["mutual_agreement"]
        if not isinstance(ma, dict) or "sha256" not in ma or "confirmed" not in ma:
            raise ArtifactError("result mutual_agreement malformed")
    return obj
