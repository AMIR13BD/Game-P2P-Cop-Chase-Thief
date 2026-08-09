"""Builders for the declaration, config, and log artifacts (mandatory field sets)."""

import hashlib

from ..domain.crypto import canonical_json
from ..shared.config_hash import config_sha256
from ..shared.sysinfo import system_spec
from . import ids

TERMS = (
    "board_and_agents",
    "world",
    "movement_and_barriers",
    "scoring",
    "pheromones",
    "network_and_league",
    "rate_limiter_gatekeeper",
)


def terms_of(cfg: dict) -> dict:
    return {k: cfg[k] for k in TERMS if k in cfg}


def log_sha256(records: list) -> str:
    return hashlib.sha256(canonical_json({"records": records}).encode("utf-8")).hexdigest()


def build_declaration(
    gid: str,
    groups: dict,
    num_sub_games: int = 6,
    max_tokens: int = 200000,
    started: str = "",
    ended: str = "",
) -> dict:
    return {
        "schema_version": "1.2",
        "declaration_type": "pre_game_declaration",
        "game_id": gid,
        "game_uid": ids.game_uid(gid),
        "links": ids.links(gid),
        "timezone": "Asia/Jerusalem",
        "game_started_at": started,
        "game_ended_at": ended,
        "num_sub_games": num_sub_games,
        "max_tokens_per_game": max_tokens,
        "groups": groups,
    }


def build_config(gid: str, nn: int, cfg: dict) -> dict:
    terms = terms_of(cfg)
    return {
        "schema_version": "1.2",
        "agreed_between": cfg.get("agreed_between", []),
        **terms,
        "game_id": gid,
        "game_uid": ids.game_uid(gid),
        "sub_game_number": nn,
        "links": ids.links(gid),
        "config_name": ids.config_name(gid, nn),
        "config_sha256": config_sha256(terms),
    }


def build_log(gid: str, nn: int, summary: dict, records: list) -> dict:
    return {
        "schema_version": "1.2",
        "game_id": gid,
        "game_uid": ids.game_uid(gid),
        "sub_game_number": nn,
        "links": ids.links(gid),
        "summary": summary,
        "records": records,
    }


def group_ident(group: str, repos: dict, signer, commit: str) -> dict:
    """Per-group Step-0 declaration identity, signed over all fields (incl commit)."""
    base = {
        "group_id": group,
        "group_name": group,
        "members": [],
        "github_commit": commit,
        "repos": repos.get(group, {"cop": "local", "thief": "local"}),
        "mcp_servers": {"cop": "", "thief": ""},
        "llm_model": "template",
        "hardware_spec": system_spec(),
    }
    return {**base, "signature": signer.sign(base)}
