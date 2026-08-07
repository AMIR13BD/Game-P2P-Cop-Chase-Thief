"""This peer's OWN FastMCP server — the four official receive tools, and nothing that
blocks. There is no central server: the server is this agent's public mailbox. The
opponent pushes negotiation/turn/audit/control messages into thread-safe inboxes that
the local runtime drains on a worker.

Tool + argument names mirror the reference EXACTLY: ``negotiate`` / ``receive_turn`` /
``receive_control`` take ``message``; ``submit_audit`` takes ``payload``.

Bearer auth: the official/reference design uses NONE (endpoints are tunnel-scoped), so
a reference peer sends no ``Authorization`` header. We preserve an OPTIONAL single
shared bearer token (defense-in-depth): enforced only when a token is configured, never
required of a no-auth reference peer.
"""

import queue
import socket
import threading

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from ..exceptions import NetworkError
from ..security.auth import bearer_from_header


class PeerInboxes:
    """Thread-safe mailboxes filled by MCP tools, drained by the runtime."""

    def __init__(self):
        self.agreements: queue.Queue = queue.Queue()
        self.turns: queue.Queue = queue.Queue()
        self.audits: queue.Queue = queue.Queue()
        self.controls: queue.Queue = queue.Queue()


def _ensure_port_free(host: str, port: int) -> None:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.bind((host, port))
    except OSError as exc:
        raise NetworkError(f"port {port} on {host} already in use — stop the orphan peer") from exc
    finally:
        probe.close()


def build_peer_server(name: str, inboxes: PeerInboxes, token: str | None = None) -> FastMCP:
    """A FastMCP app exposing this peer's four official receive tools."""
    mcp = FastMCP(name=name)

    def _auth() -> None:
        if token is None:
            return  # official design: no application-level bearer
        if bearer_from_header(get_http_headers(include_all=True)) != token:
            raise PermissionError("unauthorized: bearer token missing or wrong")

    @mcp.tool
    def negotiate(message: dict) -> dict:
        """Receive the opponent's signed game agreement."""
        _auth()
        inboxes.agreements.put(message)
        return {"ok": True}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        """Receive the opponent's turn message (the turn token travels with it)."""
        _auth()
        inboxes.turns.put(message)
        return {"ok": True}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        """Receive the opponent's end-of-game audit reveal (records + nonces)."""
        _auth()
        inboxes.audits.put(payload)
        return {"ok": True}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        """Receive an opponent control signal (enable / status / restart / quit)."""
        _auth()
        inboxes.controls.put(message)
        return {"ok": True}

    return mcp


def start_peer_server(name: str, host: str, port: int, token: str | None = None) -> PeerInboxes:
    """Start this peer's MCP server on its own port in a background daemon thread."""
    _ensure_port_free(host, port)
    inboxes = PeerInboxes()
    server = build_peer_server(name, inboxes, token)
    thread = threading.Thread(
        target=lambda: server.run(
            transport="http", host=host, port=port, show_banner=False, log_level="warning"
        ),
        daemon=True,
        name=f"mcp-{name}",
    )
    thread.start()
    return inboxes
