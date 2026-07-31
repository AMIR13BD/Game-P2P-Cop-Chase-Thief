"""True two-peer final confirmation (P22).

Each peer signs its OWN canonical result hash with its OWN key; confirmations are
exchanged over the real peer protocol and verified against the PEER's key. A process
holding only its own key cannot fabricate the other peer's confirmation, because a
signature made with the wrong key fails verification under the peer's key. Every
mismatch, forgery, missing, duplicate, or reordered confirmation fails closed."""

import hashlib

from ..domain.crypto import canonical_json


def final_hash(final: dict) -> str:
    """Canonical SHA-256 of the final result summary both peers must agree on."""
    return hashlib.sha256(canonical_json(final).encode("utf-8")).hexdigest()


def make_confirmation(group: str, fhash: str, signer) -> dict:
    """A peer's signed confirmation of the final result hash."""
    body = {"group": group, "final_sha256": fhash}
    return {**body, "signature": signer.sign(body)}


def confirmation_summary(series: dict, self_group: str, opp_group: str) -> dict:
    """Role-symmetric canonical final both peers hash identically (group-keyed)."""
    subs = [
        {
            "sub_game": row["sub_game"],
            "outcome": row["outcome"],
            "scores": {self_group: row["self_score"], opp_group: row["opp_score"]},
        }
        for row in series["sub_games"]
    ]
    return {
        "sub_games": subs,
        "totals": {self_group: series["self_total"], opp_group: series["opp_total"]},
    }


def responder_confirmation(group: str, payload, signer) -> dict:
    """Responder-side `confirm` handler: independently HASH the canonical final and
    sign it with THIS peer's own key (it does not trust any presented hash string)."""
    if not isinstance(payload, dict) or not isinstance(payload.get("final"), dict):
        raise ValueError("malformed confirm payload")
    return {
        "confirmation": make_confirmation(group, final_hash(payload["final"]), signer),
        "group": group,
    }


def verify_confirmation(conf, signer) -> bool:
    """True iff `conf` carries a valid signature under `signer`'s key."""
    if not isinstance(conf, dict):
        return False
    group, fhash = conf.get("group"), conf.get("final_sha256")
    if group is None or fhash is None:
        return False
    return signer.verify({"group": group, "final_sha256": fhash}, conf.get("signature", ""))


def verify_mutual(conf_self, conf_peer, signer_self, signer_peer, expected_hash=None) -> dict:
    """Both confirmations must be present, signed under their OWN distinct keys, from
    two distinct peers, and agree on the final hash. Fails closed otherwise."""
    fails: list[str] = []
    if not conf_self or not conf_peer:
        return {"passed": False, "failures": ["missing confirmation"]}
    if not verify_confirmation(conf_self, signer_self):
        fails.append("self confirmation signature invalid")
    if not verify_confirmation(conf_peer, signer_peer):
        fails.append("peer confirmation signature invalid or locally fabricated")
    if conf_self.get("group") == conf_peer.get("group"):
        fails.append("confirmations are not from two distinct peers (duplicate/reordered)")
    if conf_self.get("final_sha256") != conf_peer.get("final_sha256"):
        fails.append("final result hashes disagree")
    if expected_hash is not None and conf_self.get("final_sha256") != expected_hash:
        fails.append("final hash does not match the local result")
    return {"passed": not fails, "failures": fails}
