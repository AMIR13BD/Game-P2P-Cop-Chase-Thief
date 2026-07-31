"""Pre-game negotiation: sign agreed terms and refuse to play on any mismatch.

Comparison uses canonical serialization (byte-level), never Python dict equality,
so key order does not matter and int 1 != float 1.0. Handshake shape adapted from
the reference negotiation module ((c) GTAI, EULA); re-implemented."""

from typing import Any

from ..exceptions import CryptoError
from .crypto import canonical_json, commit_of, fresh_nonce, verify


class Negotiation:
    def __init__(self, terms: dict[str, Any], identity: dict | None = None) -> None:
        self.terms = terms
        self.identity = identity or {}
        self._nonce = fresh_nonce()

    def signed(self) -> dict:
        return {
            "terms": self.terms,
            "nonce": self._nonce,
            "signature": commit_of(self.terms, self._nonce),
            "identity": self.identity,
        }

    def verify_peer(self, message: dict) -> dict:
        """Verify byte-identical canonical terms + a valid signature; raise otherwise."""
        theirs = message.get("terms", {})
        if canonical_json(theirs) != canonical_json(self.terms):
            raise CryptoError("agreement terms mismatch (canonical); refusing to play")
        verify(theirs, message["nonce"], message["signature"])
        return message.get("identity", {})
