"""The per-sub-game handshake, and the two dialects a conforming peer may answer in.

Split out of ``client.py`` to keep both modules inside the repository's 150-line ceiling.

``negotiate`` is built two ways in the league and the published vectors pin the BYTES
rather than the direction:

* as a **push** — call the opponent's ``negotiate``, discard the return value, and wait
  for THEIR call to arrive at ours;
* as **request/response** — call the opponent's ``negotiate`` and read the agreement out
  of the reply.

A push peer and a request/response peer are each internally correct and mutually mute:
the request/response side answers every call perfectly, and its answers land in a variable
the push side never reads. Nothing errors, both logs look healthy, and the missing thing
is missing from both — so there is nothing to see until the deadline expires.

We therefore do both, and neither is a shortcut: whichever source an agreement arrives
from, it goes through the SAME ``Negotiator.verify_peer`` — 14-term value equality, the
terms signature under the peer's own nonce, the group-id guard and the declared
``game_uid``. Accepting from a second place widens where we listen, never what we trust.
"""

import contextlib
import queue
import time

from ..exceptions import NetworkError

# Our own server answers a push with an ack, not a greeting. Only a reply carrying an
# object `terms` is a candidate agreement; anything else is just a 200.
_ACK_KEYS = ("terms",)


def _reply_agreement(reply: object, want: int | None) -> dict | None:
    """A response body that is genuinely a greeting for THIS sub-game, else None."""
    if not isinstance(reply, dict) or not isinstance(reply.get(_ACK_KEYS[0]), dict):
        return None
    if want is not None and reply.get("sub_game_number") not in (None, want):
        return None
    return reply


class AgreementMixin:
    """The handshake half of ``McpTransport`` (see client.py for the rest of the wire)."""

    def _send_offer(self, signed: dict) -> object:
        """(Re)send our SAME negotiate offer and hand back whatever the peer answered.

        Transient 502 / connection-refused are still retried inside ``_call_with_retry``;
        a peer that stays unreachable is swallowed here so the mutual loop keeps trying
        until its own overall deadline rather than aborting on one failed (re)send.
        """
        with contextlib.suppress(NetworkError):
            return self._call_with_retry("negotiate", signed, timeout=self._resend_timeout)
        return None

    def _poll_pushed(self, want: int | None) -> dict | None:
        """One bounded wait on our own inbox, skipping stragglers for other sub-games."""
        try:
            msg = self._inboxes.agreements.get(timeout=self._resend_interval)
        except queue.Empty:
            return None
        tagged = msg.get("sub_game_number") if isinstance(msg, dict) else None
        if want is not None and tagged not in (None, want):
            return None  # a straggler offer for a different sub-game: skip
        return msg

    def exchange_agreement(self, signed: dict) -> dict:
        """MUTUAL per-sub-game handshake, satisfied by EITHER dialect.

        A single successful POST is not sufficient for the push dialect: the peer's router
        may swap the active role-agent between sub-games, so an old agent can accept + ack
        our offer and then exit before the new agent ever sees it. We keep re-sending the
        IDENTICAL offer (same nonce / identity / terms — never regenerated on a retry)
        until an agreement has arrived by one route or the other, then re-send once more so
        the peer's currently-active agent definitely holds ours. Bounded by
        ``agreement_timeout``; duplicate offers are idempotent because the receiving server
        only enqueues them.
        """
        want = signed.get("sub_game_number")
        deadline = time.time() + self._agreement_timeout
        from_reply: dict | None = None
        pushed: dict | None = None
        while pushed is None and from_reply is None:
            reply = self._send_offer(signed)
            from_reply = _reply_agreement(reply, want)
            pushed = self._poll_pushed(want)
            if pushed is None and from_reply is None and time.time() >= deadline:
                # ``queue.Empty`` is the ordinary polling tick, not the failure: it fires
                # every ``_resend_interval``. Only the deadline is the real error, so the
                # internal timeout is suppressed from the public traceback.
                raise NetworkError("opponent never sent its agreement") from None
        agreed = reconcile(pushed, from_reply)
        self._send_offer(signed)  # mutual: one more so the peer's CURRENT agent holds ours
        return agreed


def reconcile(pushed: dict | None, from_reply: dict | None) -> dict:
    """One agreement out of the two routes, refusing a peer that says two different things.

    Identical greetings by both routes are the ordinary case for a peer that implements
    both, and are processed once. A genuine DISAGREEMENT is refused rather than resolved:
    picking a winner would let the choice of route decide the terms, the roles or the
    opponent's identity, and that is not a dialect difference — it is a fault.
    """
    if pushed is not None and from_reply is not None and pushed != from_reply:
        raise NetworkError(
            "opponent's pushed greeting and its negotiate reply disagree; refusing rather "
            "than choosing one — the two must be the same agreement"
        )
    agreed = pushed if pushed is not None else from_reply
    if agreed is None:  # pragma: no cover - the caller loops until one is present
        raise NetworkError("opponent never sent its agreement")
    return agreed
