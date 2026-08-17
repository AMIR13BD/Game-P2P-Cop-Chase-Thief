"""McpTransport: the peer-to-peer 'network' — my inboxes + the opponent's URL.

Outbound calls go to the OPPONENT's MCP server; inbound arrives in MY server's
inboxes. Transport is provider-neutral: an optional bearer token plus optional
``PT_TUNNEL_HEADERS`` (e.g. Localtonet's ``localtonet-skip-warning: true``) — never a
hardcoded host, provider or opponent name. Tunnel headers can never override
``Authorization`` (enforced in ``tunnel.tunnel_headers``).
"""

import asyncio
import contextlib
import json
import queue
import time

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from ..exceptions import NetworkError
from ..infra.tunnel import tunnel_headers
from .agree import AgreementMixin
from .server import PeerInboxes


def _reply_payload(result: object) -> object:
    """The structured body of a tool reply, or None. Total: a peer may answer with plain
    text, with nothing at all, or with a shape this client version does not model, and
    none of those may raise on a path the handshake depends on."""
    for attribute in ("data", "structured_content"):
        value = getattr(result, attribute, None)
        if isinstance(value, dict):
            return value
    content = getattr(result, "content", None)
    if isinstance(content, list) and content:
        text = getattr(content[0], "text", None)
        if isinstance(text, str):
            with contextlib.suppress(ValueError):
                return json.loads(text)
    return result if isinstance(result, dict) else None


class McpTransport(AgreementMixin):
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

    def _call(self, tool: str, argument: dict) -> object:
        """Invoke one opponent tool and hand back its answer, if it structured one.

        The reply is returned rather than discarded so the handshake can read an agreement
        out of it (see agree.py); every other call ignores what comes back.
        """
        key = "payload" if tool == "submit_audit" else "message"

        async def invoke():
            async with Client(StreamableHttpTransport(self._url, headers=self._headers)) as client:
                return await client.call_tool(tool, {key: argument})

        return _reply_payload(asyncio.run(invoke()))

    def _call_with_retry(self, tool: str, argument: dict, timeout: float | None = None) -> object:
        """Retry until the opponent's server is up (peers may start seconds apart)."""
        deadline = time.time() + (timeout if timeout is not None else self._connect_timeout)
        while True:
            try:
                return self._call(tool, argument)
            except Exception as exc:
                if time.time() >= deadline:
                    raise NetworkError(f"opponent MCP unreachable at {self._url}: {exc}") from exc
                time.sleep(self._retry)

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
