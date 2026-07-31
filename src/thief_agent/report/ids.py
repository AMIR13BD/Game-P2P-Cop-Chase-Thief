"""Deterministic artifact identifiers and file names derived from game_id."""

import hashlib


def game_uid(game_id: str) -> str:
    """Deterministic 32-hex uid so artifact generation is reproducible."""
    return hashlib.sha256(game_id.encode("utf-8")).hexdigest()[:32]


def declaration_name(gid: str) -> str:
    return f"declaration_{gid}.json"


def config_name(gid: str, nn: int) -> str:
    return f"config_{gid}_g{nn:02d}.json"


def log_name(gid: str, nn: int) -> str:
    return f"log_{gid}_g{nn:02d}.json"


def result_name(gid: str) -> str:
    return f"result_{gid}.json"


def links(gid: str) -> dict:
    return {
        "declaration": declaration_name(gid),
        "config": f"config_{gid}_g<NN>.json",
        "log": f"log_{gid}_g<NN>.json",
        "result": result_name(gid),
    }
