"""Load the shared signed game.json and (optionally) the private game.toml.

game.json values override any parallel key in game.toml, so the private file can
never weaken a signed term."""

import json
import tomllib
from pathlib import Path
from typing import Any

from .version import check_config_version


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a shared game config, validating its declared version at startup (§8.1).

    `check_config_version` treats a missing `version` key as the current version, so an
    opponent's Appendix-F contract file still loads; only an explicitly unsupported
    version fails closed.
    """
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    check_config_version(cfg)
    return cfg


def load_toml(path: str | Path) -> dict[str, Any]:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def merge(private: dict[str, Any], shared: dict[str, Any]) -> dict[str, Any]:
    """Shallow merge where shared (signed) keys win over private keys."""
    out = dict(private)
    for key, val in shared.items():
        out[key] = val
    return out
