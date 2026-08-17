"""The official pre-game gate: agree on terms, exchange mutual SHA-256 signatures.

Each peer signs ``SHA256(canonical(terms)|nonce)`` (our commit-reveal primitive, which
reproduces the reference/kit ``terms_signature`` byte-for-byte) and verifies the
opponent signed the SAME terms. Play starts only after both verifications pass; the
shared ``game_id``/``game_uid`` are then derived from data both peers hold.
"""

from dataclasses import dataclass

from ..domain.crypto import commit_of, fresh_nonce, verify
from ..exceptions import ConfigError, CryptoError
from .guard import check_group_id
from .ids import derive_game_ids
from .terms import TERMS_KEYS
from .wire import Negotiation


class NegotiationRefusedError(Exception):
    """A greeting we refuse on the record: terms mismatch, bad signature, or no group."""


@dataclass(frozen=True)
class Agreed:
    game_id: str
    game_uid: str
    opponent_group: str
    opponent_role: str | None
    opponent_identity: dict
    terms: dict


class Negotiator:
    """One peer's side of the agreement handshake for a single sub-game."""

    def __init__(
        self, terms: dict, identity: dict, group_id: str, expect_opponent: str | None = None
    ):
        self.terms = terms
        self.identity = identity
        self.group_id = group_id
        # Once a series knows who it is playing, a later greeting naming someone else would
        # silently re-key every artifact and split the match across two game_ids.
        self.expect_opponent = expect_opponent
        self._nonce = fresh_nonce()

    def signed(
        self, role: str, sub_game_number: int, opponent_group: str | None = None
    ) -> Negotiation:
        """My agreement message: signed terms + identity + pairing fields."""
        return Negotiation(
            terms=self.terms,
            nonce=self._nonce,
            signature=commit_of(self.terms, self._nonce),
            group_id=self.group_id,
            role=role,
            sub_game_number=sub_game_number,
            identity=self.identity,
            game_uid=(
                derive_game_ids(self.terms, self.group_id, opponent_group)[1]
                if opponent_group
                else None
            ),
        )

    def verify_peer(self, raw: dict) -> Agreed:
        """Check an inbound greeting; raise NegotiationRefusedError with a diagnosis, or Agree."""
        if not isinstance(raw, dict) or not isinstance(raw.get("terms"), dict):
            raise NegotiationRefusedError("greeting carries no object `terms` (SPEC §4)")
        peer_terms = raw["terms"]
        missing = sorted(set(TERMS_KEYS) - set(peer_terms))
        if missing:
            raise NegotiationRefusedError(f"opponent terms incomplete; missing {missing}")
        if peer_terms != self.terms:
            diff = [k for k in TERMS_KEYS if self.terms.get(k) != peer_terms.get(k)]
            raise NegotiationRefusedError(f"terms mismatch on {diff}: constitution disagreement")
        nonce, signature = raw.get("nonce"), raw.get("signature")
        if not nonce or not signature:
            raise NegotiationRefusedError("greeting carries no nonce/signature to verify")
        try:
            verify(peer_terms, nonce, signature)
        except CryptoError as exc:
            raise NegotiationRefusedError(f"terms signature does not verify: {exc}") from exc
        opponent = raw.get("group_id") or (raw.get("identity") or {}).get("group_id")
        if not opponent:
            raise NegotiationRefusedError("greeting names no group_id; no game_id derivable")
        # The signature above covers the TERMS, never this name — and this name becomes the
        # artifact filename base. Refuse a hostile one rather than rewriting it (guard.py).
        try:
            opponent = check_group_id(opponent, self.group_id)
        except ConfigError as exc:
            raise NegotiationRefusedError(str(exc)) from exc
        if self.expect_opponent and opponent != self.expect_opponent:
            raise NegotiationRefusedError(
                f"opponent identity changed mid-series: expected {self.expect_opponent!r}, "
                f"this greeting names {opponent!r}"
            )
        game_id, game_uid = derive_game_ids(self.terms, self.group_id, opponent)
        declared = raw.get("game_uid")
        if isinstance(declared, str) and declared != game_uid:
            raise NegotiationRefusedError(
                f"game_uid mismatch: we derive {game_uid}, they declared {declared} "
                f"(wider-input derivation? WARNINGS §2)"
            )
        return Agreed(
            game_id, game_uid, opponent, raw.get("role"), raw.get("identity") or {}, peer_terms
        )
