"""Cryptographic config lock: config_sha256 = SHA256(canonical_json(config) bytes)."""

import hashlib

from ..domain.crypto import canonical_json


def config_sha256(cfg: dict) -> str:
    return hashlib.sha256(canonical_json(cfg).encode("utf-8")).hexdigest()
