"""McpTransport: the peer-to-peer 'network' — my inboxes + the opponent's URL.

Outbound calls go to the OPPONENT's MCP server; inbound arrives in MY server's
inboxes. Transport is provider-neutral: an optional bearer token plus optional
``PT_TUNNEL_HEADERS`` (e.g. Localtonet's ``localtonet-skip-warning: true``) — never a
hardcoded host, provider or opponent name. Tunnel headers can never override
``Authorization`` (enforced in ``tunnel.tunnel_headers``).
"""

import asyncio
import contextlib
import queue
import time

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from ..exceptions import NetworkError
from ..infra.tunnel import tunnel_headers
from .server import PeerInboxes


class McpTransport:
    """One peer's view of the wire: push to opponent, pull from own inboxes."""

    def __init__(
        self,
        opponent_url: str,
        inboxes: PeerInboxes,
        token: str | None = None,
        env: dict | None = None,
        connect_timeout: float = 60.0,
        retry_interval: float = 1.0,
        agreement_timeout: float = 300.0,
        resend_interval: float = 3.0,
        resend_timeout: float = 15.0,
    ):
        self._url = opponent_url
        self._inboxes = inboxes
        self._headers = dict(tunnel_headers(env))
        if token:
            self._headers["Authorization"] = f"Bearer {token}"
        self._connect_timeout = connect_timeout
        self._retry = retry_interval
        # The per-sub-game handshake is MUTUAL, not a single POST: keep re-sending our
        # SAME offer until we have also received the peer's offer for this sub-game, so a
        # peer router that swaps the active role-agent between sub-games (old agent accepts
        # + acks our offer, then exits before the new agent sees it) cannot drop our offer.
        self._agreement_timeout = agreement_timeout
        self._resend_interval = resend_interval
        self._resend_timeout = resend_timeout

    def _call(self, tool: str, argument: dict) -> None:
        key = "payload" if tool == "submit_audit" else "message"

        async def invoke():
            async with Client(StreamableHttpTransport(self._url, headers=self._headers)) as client:
                await client.call_tool(tool, {key: argument})

        asyncio.run(invoke())

    def _call_with_retry(self, tool: str, argument: dict, timeout: float | None = None) -> None:
        """Retry until the opponent's server is up (peers may start seconds apart)."""
        deadline = time.time() + (timeout if timeout is not None else self._connect_timeout)
        while True:
            try:
                self._call(tool, argument)
                return
            except Exception as exc:
                if time.time() >= deadline:
                    raise NetworkError(f"opponent MCP unreachable at {self._url}: {exc}") from exc
                time.sleep(self._retry)

    def _send_offer(self, signed: dict) -> None:
        """(Re)send our SAME negotiate offer, best-effort. Transient HTTP 502 /
        connection-refused are still retried inside ``_call_with_retry``; a peer that
        stays unreachable is swallowed here so the mutual loop keeps trying until its own
        overall deadline rather than aborting on one failed (re)send."""
        with contextlib.suppress(NetworkError):
            self._call_with_retry("negotiate", signed, timeout=self._resend_timeout)

    def exchange_agreement(self, signed: dict) -> dict:
        """MUTUAL per-sub-game handshake. A single successful POST is NOT sufficient: the
        peer's router may swap the active role-agent between sub-games, so an old agent can
        accept + ack our offer and then exit before the new agent ever sees it. We keep
        re-sending the IDENTICAL offer (same nonce / identity / terms — never regenerated on
        a retry) until we have ALSO received the peer's offer for THIS sub-game, then re-send
        once more so the peer's currently-active agent definitely holds it. Bounded by
        ``agreement_timeout`` (no infinite hang); duplicate offers are idempotent because the
        receiving server only enqueues them."""
        want = signed.get("sub_game_number")
        deadline = time.time() + self._agreement_timeout
        received: dict | None = None
        while received is None:
            self._send_offer(signed)  # (re)send; a swap may have dropped the previous one
            try:
                msg = self._inboxes.agreements.get(timeout=self._resend_interval)
            except queue.Empty:
                if time.time() >= deadline:
                    # ``queue.Empty`` is the ordinary polling tick, not the failure:
                    # it fires every ``_resend_interval`` and is normally swallowed by
                    # the ``continue`` below. Only the deadline is the real error, so
                    # the internal timeout is suppressed from the public traceback.
                    raise NetworkError("opponent never sent its agreement") from None
                continue
            if (
                want is not None
                and isinstance(msg, dict)
                and msg.get("sub_game_number") not in (None, want)
            ):
                continue  # a straggler offer for a different sub-game: skip, keep waiting
            received = msg
        self._send_offer(signed)  # mutual: one more so the peer's CURRENT agent holds our offer
        return received

    def send_turn(self, message: dict) -> None:
        self._call_with_retry("receive_turn", message)

    def poll_turn(self, timeout: float) -> dict | None:
        try:
            return self._inboxes.turns.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_audit(self, payload: dict) -> None:
        with contextlib.suppress(NetworkError):
            self._call_with_retry("submit_audit", payload, timeout=10.0)

    def poll_audit(self, timeout: float) -> dict | None:
        try:
            return self._inboxes.audits.get(timeout=timeout)
        except queue.Empty:
            return None

    def send_control(self, message: dict) -> None:
        with contextlib.suppress(NetworkError):
            self._call_with_retry("receive_control", message, timeout=2.0)

    def poll_control(self) -> dict | None:
        try:
            return self._inboxes.controls.get_nowait()
        except queue.Empty:
            return None

    def drain_inboxes(self) -> None:
        for inbox in (self._inboxes.turns, self._inboxes.controls, self._inboxes.audits):
            with contextlib.suppress(queue.Empty):
                while True:
                    inbox.get_nowait()
