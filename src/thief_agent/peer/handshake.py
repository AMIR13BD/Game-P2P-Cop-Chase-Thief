"""Pure handshake/negotiation logic: version & schema compatibility, canonical
config-hash agreement, and mismatch refusal (no I/O, no network)."""

from ..exceptions import ConfigError
from ..shared.config_hash import config_sha256
from ..shared.version import CODE_VERSION

PROTOCOL_VERSION = "d2p1"
SCHEMA_VERSION = "1.2"


def local_hello(group: str, terms: dict) -> dict:
    return {
        "group": group,
        "code_version": CODE_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "schema_version": SCHEMA_VERSION,
        "config_sha256": config_sha256(terms),
    }


def check_compatibility(peer_hello: dict) -> None:
    """Raise ConfigError on protocol or schema mismatch."""
    if peer_hello.get("protocol_version") != PROTOCOL_VERSION:
        raise ConfigError(f"protocol mismatch: {peer_hello.get('protocol_version')}")
    if peer_hello.get("schema_version") != SCHEMA_VERSION:
        raise ConfigError(f"schema mismatch: {peer_hello.get('schema_version')}")


def agree_config(local_terms: dict, peer_hash: str) -> str:
    """Return the agreed config hash; raise ConfigError on canonical mismatch."""
    local = config_sha256(local_terms)
    if local != peer_hash:
        raise ConfigError(f"config hash mismatch: local {local[:12]} != peer {peer_hash[:12]}")
    return local
