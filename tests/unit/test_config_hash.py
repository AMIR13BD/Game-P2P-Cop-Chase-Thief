import pytest

from thief_agent.domain.negotiation import Negotiation
from thief_agent.exceptions import CryptoError
from thief_agent.shared.config_hash import config_sha256
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

GOLDEN = "1355b4c57daa1b5d83819b228c90e7ead09efb90fac16e0053f20a0d3c44813d"


def test_golden_hash_stable_and_cross_repo():
    # identical shared config -> identical hash in both repos (role-agnostic)
    assert config_sha256(DEFAULT_GAME_CONFIG) == GOLDEN


def test_key_order_independent():
    assert config_sha256({"a": 1, "b": 2}) == config_sha256({"b": 2, "a": 1})


def test_changed_value_changes_hash():
    assert config_sha256({"x": 1}) != config_sha256({"x": 2})


def test_int_and_float_not_byte_identical():
    assert config_sha256({"x": 1}) != config_sha256({"x": 1.0})


def test_negotiation_agrees_on_identical_terms():
    terms = {"grid_size": 7, "move_set": ["N", "S"]}
    a = Negotiation(terms, {"g": "police"})
    b = Negotiation({"move_set": ["N", "S"], "grid_size": 7}, {"g": "opp"})
    assert b.verify_peer(a.signed()) == {"g": "police"}


def test_negotiation_refuses_mismatch():
    a = Negotiation({"grid_size": 7})
    b = Negotiation({"grid_size": 9})
    with pytest.raises(CryptoError):
        b.verify_peer(a.signed())
