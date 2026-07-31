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
    """Development/test signer. Signatures are explicitly labelled 'devtest:'."""

    name = "dev-test"

    def sign(self, payload: dict) -> str:
        mac = hmac.new(DEV_TEST_KEY, canonical_json(payload).encode(), hashlib.sha256)
        return f"devtest:{mac.hexdigest()}"

    def verify(self, payload: dict, signature: str) -> bool:
        return hmac.compare_digest(signature, self.sign(payload))


class OfficialSigner:
    """Placeholder for the official Step-0 key. BLOCKED-EXTERNAL until provided."""

    name = "official"

    def sign(self, payload: dict) -> str:
        raise RuntimeError("BLOCKED-EXTERNAL: official Step-0 signing key not provided")

    def verify(self, payload: dict, signature: str) -> bool:
        raise RuntimeError("BLOCKED-EXTERNAL: official Step-0 signing key not provided")
