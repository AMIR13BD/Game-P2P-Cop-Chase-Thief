"""Pre-game negotiation: sign agreed terms and refuse to play on any mismatch.

Handshake shape adapted from the reference implementation's negotiation module
((c) GTAI, Educational-Use EULA); re-implemented. See docs/REUSE-REGISTER.md.
"""

from typing import Any

from ..exceptions import CryptoError
from .crypto import commit_of, fresh_nonce, verify


class Negotiation:
    def __init__(self, terms: dict[str, Any], identity: dict | None = None) -> None:
        self.terms = terms
        self.identity = identity or {}
        self._nonce = fresh_nonce()

    def signed(self) -> dict:
        """My agreement message: terms + nonce + signature over both + identity."""
        return {
            "terms": self.terms,
            "nonce": self._nonce,
            "signature": commit_of(self.terms, self._nonce),
            "identity": self.identity,
        }

    def verify_peer(self, message: dict) -> dict:
        """Verify the opponent signed byte-identical terms; raise on mismatch."""
        if message.get("terms") != self.terms:
            raise CryptoError("agreement terms mismatch; refusing to play")
        verify(message["terms"], message["nonce"], message["signature"])
        return message.get("identity", {})
