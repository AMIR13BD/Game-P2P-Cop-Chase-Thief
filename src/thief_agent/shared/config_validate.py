"""Appendix F enforcement: fixed values, minimums (raise-only), negotiable defaults."""

from ..domain.moveset import validate_move_set
from ..exceptions import ConfigError

FIXED = {
    "num_agents": 2,
    "pheromone_center_intensity": 0.9,
    "pheromone_decay": 0.10,
    "pheromone_grid_size": 5,
    "capture_cop": 20,
    "capture_thief": 5,
    "survival_cop": 5,
    "survival_thief": 10,
    "tie_score": 2,
}
MINIMUMS = {"grid_size": 7, "max_barriers": 14, "max_moves": 35, "survival_threshold": 35}
SUB_GAMES = 6  # fixed series length (illustrative num_games=1 does not override)


def _check_fixed(flat: dict) -> None:
    for key, want in FIXED.items():
        if key in flat and flat[key] != want:
            raise ConfigError(f"fixed parameter {key}={flat[key]} must equal {want}")


def _check_min(flat: dict) -> None:
    for key, floor in MINIMUMS.items():
        if key in flat and flat[key] < floor:
            raise ConfigError(f"minimum parameter {key}={flat[key]} below floor {floor}")


def flatten(cfg: dict) -> dict:
    flat: dict = {}
    for val in cfg.values():
        if isinstance(val, dict):
            flat.update(val)
    flat.update({k: v for k, v in cfg.items() if not isinstance(v, dict)})
    return flat


def validate(cfg: dict) -> dict:
    """Validate and return a normalized flat parameter dict (fail closed)."""
    flat = flatten(cfg)
    validate_move_set(flat.get("move_set"))
    _check_fixed(flat)
    _check_min(flat)
    flat.setdefault("map_area", "New York")
    if not flat["map_area"]:
        flat["map_area"] = "New York"
    flat["sub_games"] = SUB_GAMES
    return flat
