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
    ):
        self._url = opponent_url
        self._inboxes = inboxes
        self._headers = dict(tunnel_headers(env))
        if token:
            self._headers["Authorization"] = f"Bearer {token}"
        self._connect_timeout = connect_timeout
        self._retry = retry_interval

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

    def exchange_agreement(self, signed: dict) -> dict:
        self._call_with_retry("negotiate", signed)
        try:
            return self._inboxes.agreements.get(timeout=self._connect_timeout)
        except queue.Empty as exc:
            raise NetworkError("opponent never sent its agreement") from exc

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
