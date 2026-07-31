import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.peer.handshake import (
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    agree_config,
    check_compatibility,
    local_hello,
)
from thief_agent.security.auth import AuthRegistry, bearer_from_header
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def test_auth_registry_valid_invalid_revoked():
    reg = AuthRegistry({"GOOD", "REV"}, {"REV"})
    assert reg.check("GOOD")
    assert not reg.check("NOPE")
    assert not reg.check("REV")
    assert not reg.check(None)
    reg.revoke("GOOD")
    assert not reg.check("GOOD")


def test_bearer_parsing():
    assert bearer_from_header({"authorization": "Bearer abc"}) == "abc"
    assert bearer_from_header({"authorization": "Basic x"}) is None
    assert bearer_from_header({}) is None


def test_local_hello_and_compat():
    h = local_hello("g", DEFAULT_GAME_CONFIG)
    assert h["protocol_version"] == PROTOCOL_VERSION and h["schema_version"] == SCHEMA_VERSION
    check_compatibility(h)  # no raise


@pytest.mark.parametrize(
    "bad",
    [
        {"protocol_version": "X", "schema_version": SCHEMA_VERSION},
        {"protocol_version": PROTOCOL_VERSION, "schema_version": "9.9"},
    ],
)
def test_incompatible_refused(bad):
    with pytest.raises(ConfigError):
        check_compatibility(bad)


def test_agree_config_match_and_mismatch():
    h = local_hello("g", DEFAULT_GAME_CONFIG)["config_sha256"]
    assert agree_config(DEFAULT_GAME_CONFIG, h) == h
    with pytest.raises(ConfigError):
        agree_config(DEFAULT_GAME_CONFIG, "0" * 64)
