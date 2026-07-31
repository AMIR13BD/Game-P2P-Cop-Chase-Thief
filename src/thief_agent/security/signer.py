"""Pluggable Step-0 signer. A dev/test signer is provided (with verify); the
official course-provided key integration is intentionally BLOCKED-EXTERNAL."""

import hashlib
import hmac
from typing import Protocol

from ..domain.crypto import canonical_json

# Clearly-marked NON-SECRET development key. NOT the official course signing key.
DEV_TEST_KEY = b"DEV-TEST-ONLY-NOT-THE-OFFICIAL-STEP0-KEY"


class Signer(Protocol):
    name: str

    def sign(self, payload: dict) -> str: ...

    def verify(self, payload: dict, signature: str) -> bool: ...


class DevTestSigner:
    """Development/test signer. Signatures are labelled 'devtest:'.

    Each instance may carry a distinct per-peer secret key so two peers produce
    independently-verifiable confirmations: a process holding only its own key cannot
    forge the other peer's signature (which is verified under the peer's key)."""

    def __init__(self, name: str = "dev-test", key: bytes = DEV_TEST_KEY) -> None:
        self.name = name
        self._key = key

    def sign(self, payload: dict) -> str:
        mac = hmac.new(self._key, canonical_json(payload).encode(), hashlib.sha256)
        return f"devtest:{mac.hexdigest()}"

    def verify(self, payload: dict, signature: str) -> bool:
        return hmac.compare_digest(signature, self.sign(payload))


def peer_signer(group: str, key: bytes | None = None) -> DevTestSigner:
    """A per-peer dev signer. `key` is that peer's OWN secret (falls back to the shared
    dev key only for local single-process convenience/back-compat)."""
    return DevTestSigner(name=group, key=key if key is not None else DEV_TEST_KEY)


class OfficialSigner:
    """Placeholder for the official Step-0 key. BLOCKED-EXTERNAL until provided."""

    name = "official"

    def sign(self, payload: dict) -> str:
        raise RuntimeError("BLOCKED-EXTERNAL: official Step-0 signing key not provided")

    def verify(self, payload: dict, signature: str) -> bool:
        raise RuntimeError("BLOCKED-EXTERNAL: official Step-0 signing key not provided")
