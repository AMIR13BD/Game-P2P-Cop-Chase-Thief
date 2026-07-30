"""Cryptographic config lock (config_sha256) over canonical JSON."""

from ..domain.crypto import commit_of


def config_sha256(cfg: dict) -> str:
    """Deterministic hash of the agreed config (nonce fixed empty for a pure digest)."""
    return commit_of(cfg, "")
