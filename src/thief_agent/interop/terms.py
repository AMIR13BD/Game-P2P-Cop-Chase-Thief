"""The signed 14-key agreement terms (reference-v3) and the mapping to our engine.

``terms`` are the flat, closed, byte-identical set both peers sign (SPEC §4). They
are deliberately NOT our rich internal config: adding a key would break the
signature. ``to_flat_cfg`` translates the agreed terms into the key names our
existing gameplay engine (``peer.net_engine.PeerHalf``) already consumes, so the
strategy code is reached unchanged.
"""

from ..exceptions import ConfigError

TERMS_KEYS = (
    "board_size",
    "smell_grid_size",
    "decay_per_step",
    "emit_intensity",
    "min_center_intensity",
    "max_steps",
    "barriers_max",
    "setting",
    "hint_max_words",
    "axis_origin_corner",
    "axis_start_index",
    "thief_start",
    "cop_start",
    "num_games",
)

# Book App. F defaults (also the kit's), so a peer that agrees the standard match
# produces byte-identical terms and the signature verifies with no negotiation drift.
DEFAULTS: dict = {
    "board_size": 7,
    "smell_grid_size": 5,
    "decay_per_step": 0.1,
    "emit_intensity": 0.9,
    "min_center_intensity": 0.5,
    "max_steps": 35,
    "barriers_max": 14,
    "setting": "Haifa",
    "hint_max_words": 15,
    "axis_origin_corner": "top-left",
    "axis_start_index": 0,
    "thief_start": [3, 3],
    "cop_start": [0, 0],
    "num_games": 6,
}


def default_terms(**overrides) -> dict:
    """The standard agreed terms, with optional per-key overrides (both peers must match)."""
    terms = {k: (list(v) if isinstance(v, list) else v) for k, v in DEFAULTS.items()}
    terms.update(overrides)
    return terms


def terms_from_config(cfg: dict | None) -> dict:
    """Extract exactly the 14 flat terms from a (possibly wider) config, filling defaults."""
    cfg = cfg or {}
    return {k: cfg.get(k, DEFAULTS[k]) for k in TERMS_KEYS}


def validate_terms(terms: dict) -> None:
    """Fail fast (before any port opens) if the flat agreed set is incomplete."""
    missing = [k for k in TERMS_KEYS if terms.get(k) is None]
    if missing:
        raise ConfigError("missing required agreed term(s): " + ", ".join(missing))


def to_flat_cfg(terms: dict, seed: int = 1234) -> dict:
    """Reference terms -> the flat config key names our gameplay engine consumes."""
    return {
        "grid_size": terms["board_size"],
        "cop_start": list(terms["cop_start"]),
        "thief_start": list(terms["thief_start"]),
        "pheromone_decay": terms["decay_per_step"],
        "max_barriers": terms["barriers_max"],
        "survival_threshold": terms["max_steps"],
        "max_steps": terms["max_steps"],
        "seed": seed,
    }
