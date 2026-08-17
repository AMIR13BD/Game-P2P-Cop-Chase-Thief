"""A conforming peer may answer ``negotiate`` by pushing, by replying, or by both.

A push peer and a request/response peer are each internally correct and mutually mute, and
every probe passes while they wait for each other. We listen on both routes; what we TRUST
is unchanged, because either route lands in the same ``Negotiator.verify_peer``.
"""

import queue

import pytest

from thief_agent.exceptions import NetworkError
from thief_agent.interop.agree import AgreementMixin, reconcile

GREETING = {"terms": {"board_size": 7}, "nonce": "n", "signature": "s", "sub_game_number": 1}
OTHER = {**GREETING, "nonce": "different"}


class FakeTransport(AgreementMixin):
    """Only the pieces the handshake touches: an outbound call and our own inbox."""

    def __init__(self, reply=None, pushed=None):
        self._reply = reply
        self._inboxes = type("I", (), {"agreements": queue.Queue()})()
        for message in pushed or []:
            self._inboxes.agreements.put(message)
        self._resend_interval = 0.01
        self._resend_timeout = 0.01
        self._agreement_timeout = 0.3
        self.sent = 0

    def _call_with_retry(self, tool, argument, timeout=None):
        self.sent += 1
        return self._reply


def test_push_only_is_accepted():
    transport = FakeTransport(reply={"ok": True}, pushed=[GREETING])
    assert transport.exchange_agreement({"sub_game_number": 1}) == GREETING


def test_response_body_only_is_accepted():
    """The dialect that used to stall us forever: they answer, nobody pushes."""
    transport = FakeTransport(reply=GREETING)
    assert transport.exchange_agreement({"sub_game_number": 1}) == GREETING


def test_both_routes_agreeing_is_processed_once():
    transport = FakeTransport(reply=GREETING, pushed=[GREETING])
    assert transport.exchange_agreement({"sub_game_number": 1}) == GREETING


def test_both_routes_disagreeing_is_refused():
    """Choosing a winner would let the route decide the terms, roles or identity."""
    transport = FakeTransport(reply=OTHER, pushed=[GREETING])
    with pytest.raises(NetworkError):
        transport.exchange_agreement({"sub_game_number": 1})


def test_a_plain_ack_is_not_mistaken_for_an_agreement():
    """Our own server answers a push with {"ok": true}; that is a 200, not a greeting."""
    transport = FakeTransport(reply={"ok": True})
    with pytest.raises(NetworkError):
        transport.exchange_agreement({"sub_game_number": 1})


def test_a_reply_for_another_sub_game_is_ignored():
    transport = FakeTransport(reply={**GREETING, "sub_game_number": 5})
    with pytest.raises(NetworkError):
        transport.exchange_agreement({"sub_game_number": 1})


def test_a_pushed_straggler_for_another_sub_game_is_skipped():
    straggler = {**GREETING, "sub_game_number": 5}
    transport = FakeTransport(reply={"ok": True}, pushed=[straggler, GREETING])
    assert transport.exchange_agreement({"sub_game_number": 1}) == GREETING


def test_a_greeting_without_a_sub_game_number_still_matches():
    """Older peers omit the pairing fields; omission is never a refusal."""
    bare = {"terms": {"board_size": 7}, "nonce": "n", "signature": "s"}
    assert FakeTransport(reply=bare).exchange_agreement({"sub_game_number": 3}) == bare


def test_we_speak_first_and_keep_re_sending():
    """Whoever speaks first unblocks the other, so speaking is never the wrong move."""
    transport = FakeTransport(reply=GREETING)
    transport.exchange_agreement({"sub_game_number": 1})
    assert transport.sent >= 2  # the offer, then one more so their CURRENT agent holds it


def test_reconcile_is_idempotent_and_refuses_a_contradiction():
    assert reconcile(GREETING, GREETING) == GREETING
    assert reconcile(GREETING, None) == GREETING
    assert reconcile(None, GREETING) == GREETING
    with pytest.raises(NetworkError):
        reconcile(GREETING, OTHER)
