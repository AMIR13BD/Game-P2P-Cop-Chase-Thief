"""P22 true two-peer final confirmation: each peer signs its own result hash with its
own key; a process cannot fabricate the other peer's confirmation; every mismatch,
forgery, missing, duplicate, or reordered confirmation fails closed."""

import pytest

from thief_agent.report.confirm import (
    confirmation_summary,
    final_hash,
    make_confirmation,
    responder_confirmation,
    verify_confirmation,
    verify_mutual,
)
from thief_agent.security.signer import DevTestSigner

POLICE = DevTestSigner("amireman-police", key=b"police-secret-key-A")
THIEF = DevTestSigner("amireman-thief", key=b"thief-secret-key-B")


def _summary():
    series = {
        "sub_games": [{"sub_game": 1, "outcome": "capture", "self_score": 20, "opp_score": 5}],
        "self_total": 20,
        "opp_total": 5,
    }
    return confirmation_summary(series, "amireman-police", "amireman-thief")


def test_distinct_peer_confirmations_agree():
    h = final_hash(_summary())
    cp = make_confirmation("amireman-police", h, POLICE)
    ct = make_confirmation("amireman-thief", h, THIEF)
    assert verify_mutual(cp, ct, POLICE, THIEF, expected_hash=h)["passed"] is True


def test_one_process_cannot_fabricate_peer_confirmation():
    h = final_hash(_summary())
    cp = make_confirmation("amireman-police", h, POLICE)
    # Police forges the thief's confirmation using its OWN key (fabrication attempt).
    forged = make_confirmation("amireman-thief", h, POLICE)
    # Verified against the thief's real key, the forgery fails.
    assert verify_confirmation(forged, THIEF) is False
    res = verify_mutual(cp, forged, POLICE, THIEF)
    assert res["passed"] is False
    assert any("fabricated" in f for f in res["failures"])


def test_hash_disagreement_fails_closed():
    cp = make_confirmation("amireman-police", "a" * 64, POLICE)
    ct = make_confirmation("amireman-thief", "b" * 64, THIEF)
    assert verify_mutual(cp, ct, POLICE, THIEF)["passed"] is False


def test_duplicate_or_reordered_same_peer_fails():
    h = final_hash(_summary())
    cp = make_confirmation("amireman-police", h, POLICE)
    assert verify_mutual(cp, cp, POLICE, POLICE)["passed"] is False  # same group twice


def test_missing_confirmation_fails():
    h = final_hash(_summary())
    cp = make_confirmation("amireman-police", h, POLICE)
    assert verify_mutual(cp, None, POLICE, THIEF)["passed"] is False
    assert verify_mutual(None, cp, POLICE, THIEF)["passed"] is False


def test_responder_confirmation_recomputes_hash():
    final = _summary()
    out = responder_confirmation("amireman-thief", {"final": final}, THIEF)
    assert out["group"] == "amireman-thief"
    conf = out["confirmation"]
    assert conf["final_sha256"] == final_hash(final)
    assert verify_confirmation(conf, THIEF) is True
    assert verify_confirmation(conf, POLICE) is False  # not forgeable under police key


def test_responder_rejects_malformed_payload():
    with pytest.raises(ValueError):
        responder_confirmation("g", {"no_final": 1}, THIEF)
    with pytest.raises(ValueError):
        responder_confirmation("g", "notadict", THIEF)


def test_summary_is_role_symmetric():
    # Same game viewed from either side yields the same group-keyed hash.
    driver = confirmation_summary(
        {
            "sub_games": [{"sub_game": 1, "outcome": "survival", "self_score": 5, "opp_score": 10}],
            "self_total": 5,
            "opp_total": 10,
        },
        "amireman-police",
        "amireman-thief",
    )
    responder = confirmation_summary(
        {
            "sub_games": [{"sub_game": 1, "outcome": "survival", "self_score": 10, "opp_score": 5}],
            "self_total": 10,
            "opp_total": 5,
        },
        "amireman-thief",
        "amireman-police",
    )
    assert final_hash(driver) == final_hash(responder)
