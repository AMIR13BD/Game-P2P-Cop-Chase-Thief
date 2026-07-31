"""Strict Appendix F validation. Fail closed on missing/unknown fields, wrong fixed
values, or below-floor minimums. Fills negotiable defaults and returns a flat dict."""

from ..domain.moveset import validate_move_set
from ..exceptions import ConfigError
from . import config_spec as spec


def _require_structure(cfg: dict) -> None:
    for cat, fields in spec.REQUIRED.items():
        if cat not in cfg or not isinstance(cfg[cat], dict):
            raise ConfigError(f"missing required config category '{cat}'")
        present = set(cfg[cat])
        missing = set(fields) - present
        if missing:
            raise ConfigError(f"category '{cat}' missing fields {sorted(missing)}")
        unknown = present - set(fields)
        if unknown:
            raise ConfigError(f"category '{cat}' has unknown fields {sorted(unknown)}")


def flatten(cfg: dict) -> dict:
    flat: dict = {}
    for val in cfg.values():
        if isinstance(val, dict):
            flat.update(val)
    return flat


def _check_values(flat: dict) -> None:
    validate_move_set(flat.get("move_set"))
    for key, want in spec.FIXED.items():
        if flat[key] != want:
            raise ConfigError(f"fixed parameter {key}={flat[key]} must equal {want}")
    for key, floor in spec.MINIMUMS.items():
        if flat[key] < floor:
            raise ConfigError(f"minimum parameter {key}={flat[key]} below floor {floor}")


def _check_positions(flat: dict) -> None:
    n = flat["grid_size"]
    for key in ("thief_start", "cop_start"):
        pos = flat[key]
        if (
            not isinstance(pos, (list, tuple))
            or len(pos) != 2
            or not all(isinstance(v, int) and 0 <= v < n for v in pos)
        ):
            raise ConfigError(f"{key}={pos} is not a valid cell on a {n}x{n} board")


def validate(cfg: dict) -> dict:
    _require_structure(cfg)
    flat = flatten(cfg)
    _check_values(flat)
    _check_positions(flat)
    if not flat.get("map_area"):
        flat["map_area"] = spec.NEG_DEFAULTS["map_area"]
    flat["sub_games"] = spec.SUB_GAMES
    return flat
