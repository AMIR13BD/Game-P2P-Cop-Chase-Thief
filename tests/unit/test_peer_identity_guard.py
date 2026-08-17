"""The opponent's declared identity is untrusted input, and it names our files.

The terms signature covers the TERMS and the signer's nonce — never the group name — so a
greeting can verify perfectly and still carry a group id built to escape the output
directory or to collide with ours. Both are refused on the record rather than rewritten.
"""

import pytest

from thief_agent.domain.crypto import commit_of, fresh_nonce
from thief_agent.exceptions import ConfigError
from thief_agent.interop.guard import check_group_id
from thief_agent.interop.negotiate import NegotiationRefusedError, Negotiator
from thief_agent.interop.terms import default_terms

OURS = "amireman"

HOSTILE = [
    "../../../../pwned",
    "..\\..\\pwned",
    "../etc/passwd",
    "/etc/passwd",
    "C:\\Windows\\system32",
    "~/.ssh/id_rsa",
    "a/b",
    "a\\b",
    "..",
    ".",
    "",
    "   ",
    "with\x00nul",
    "line\nbreak",
    "x" * 65,
]

LEGITIMATE = [
    "uoh-ay26",
    "Orcai-MJ",
    "team-aleph",
    "best2934",
    "anrbj666",
    "team aleph",
    "Group_7",
    "team.bet",
    "קבוצה",
]


@pytest.mark.parametrize("group", HOSTILE)
def test_hostile_group_ids_are_refused(group):
    with pytest.raises(ConfigError):
        check_group_id(group, OURS)


@pytest.mark.parametrize("group", LEGITIMATE)
def test_legitimate_group_ids_are_accepted_unchanged(group):
    """Refuse or accept — never silently rename a group we then file a match under."""
    assert check_group_id(group, OURS) == group


def test_a_peer_claiming_our_own_group_id_is_refused():
    """Both dicts are keyed by group: one id for both collapses roles and scores into one
    entry, which turns a win into a false tie without either peer's engine noticing."""
    with pytest.raises(ConfigError):
        check_group_id(OURS, OURS)


def _greeting(group: str) -> dict:
    terms = default_terms()
    nonce = fresh_nonce()
    return {
        "terms": terms,
        "nonce": nonce,
        "signature": commit_of(terms, nonce),
        "group_id": group,
        "role": "thief",
        "sub_game_number": 1,
        "identity": {"group_id": group},
    }


@pytest.mark.parametrize("group", ["../../../../pwned", OURS])
def test_the_handshake_refuses_a_hostile_identity_despite_a_valid_signature(group):
    negotiator = Negotiator(default_terms(), {"group_id": OURS}, OURS)
    with pytest.raises(NegotiationRefusedError):
        negotiator.verify_peer(_greeting(group))


def test_the_handshake_still_accepts_an_honest_opponent():
    negotiator = Negotiator(default_terms(), {"group_id": OURS}, OURS)
    agreed = negotiator.verify_peer(_greeting("uoh-ay26"))
    assert agreed.opponent_group == "uoh-ay26"
    assert agreed.game_id == "amireman-vs-uoh-ay26"


def test_an_opponent_may_not_change_identity_mid_series():
    """Once a series knows who it is playing, a later greeting naming someone else would
    silently re-key every artifact; it is refused instead."""
    negotiator = Negotiator(default_terms(), {"group_id": OURS}, OURS, expect_opponent="uoh-ay26")
    with pytest.raises(NegotiationRefusedError):
        negotiator.verify_peer(_greeting("Orcai-MJ"))
    assert negotiator.verify_peer(_greeting("uoh-ay26")).opponent_group == "uoh-ay26"
