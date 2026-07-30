"""Pluggable Step-0 signer. A dev/test signer is provided; the official
course-provided key integration is intentionally BLOCKED-EXTERNAL."""

import hashlib
import hmac
from typing import Protocol

from ..domain.crypto import canonical_json

# Clearly-marked NON-SECRET development key. NOT the official course signing key.
DEV_TEST_KEY = b"DEV-TEST-ONLY-NOT-THE-OFFICIAL-STEP0-KEY"


class Signer(Protocol):
    name: str

    def sign(self, payload: dict) -> str: ...


class DevTestSigner:
    """Development/test signer. Its signatures are explicitly labelled dev-test."""

    name = "dev-test"

    def sign(self, payload: dict) -> str:
        mac = hmac.new(DEV_TEST_KEY, canonical_json(payload).encode(), hashlib.sha256)
        return f"devtest:{mac.hexdigest()}"


class OfficialSigner:
    """Placeholder for the official Step-0 key. BLOCKED-EXTERNAL until provided."""

    name = "official"

    def sign(self, payload: dict) -> str:
        raise RuntimeError("BLOCKED-EXTERNAL: official Step-0 signing key not provided")
