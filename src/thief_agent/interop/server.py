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

import socket
import threading
import time

import uvicorn
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from ..exceptions import NetworkError
from ..security.auth import bearer_from_header
from .inboxes import PeerInboxes, accept


class PeerServer:
    """A running peer MCP server: its inboxes plus a drain-aware graceful stop.

    Closes the final-audit race — the peer's last ``submit_audit`` unblocks our
    ``poll_audit`` before uvicorn flushes the ``200``, so the old daemon thread could be
    killed at interpreter exit mid-response (peer saw 502/timeout). ``stop`` keeps serving
    until the peer's connections drain (bounded by ``max_linger``), then shuts uvicorn down
    gracefully (which itself waits for any still-open response) and joins the thread.
    """

    def __init__(self, inboxes: "PeerInboxes", server: uvicorn.Server, thread: threading.Thread):
        self.inboxes = inboxes
        self._server = server
        self._thread = thread

    def _active_connections(self) -> int | None:
        state = getattr(self._server, "server_state", None)
        return len(state.connections) if state is not None else None

    def stop(self, max_linger: float = 8.0, settle: float = 0.3, grace: float = 5.0) -> None:
        """Linger until the peer's final request has fully drained, then stop gracefully."""
        deadline = time.monotonic() + max_linger
        idle_since: float | None = None
        while time.monotonic() < deadline:
            active = self._active_connections()
            if active is None:  # introspection unavailable -> fall back to a bounded linger
                time.sleep(min(max_linger, 3.0))
                break
            now = time.monotonic()
            if active == 0:
                idle_since = idle_since if idle_since is not None else now
                if now - idle_since >= settle:  # quiet long enough: the peer is done
                    break
            else:
                idle_since = None  # a request is still in flight; keep serving
            time.sleep(0.05)
        self._server.should_exit = True  # graceful: uvicorn drains any open response first
        self._thread.join(grace)


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
        return accept(inboxes.agreements, message)

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        """Receive the opponent's turn message (the turn token travels with it)."""
        _auth()
        return accept(inboxes.turns, message)

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        """Receive the opponent's end-of-game audit reveal (records + nonces)."""
        _auth()
        return accept(inboxes.audits, payload)

    @mcp.tool
    def receive_control(message: dict) -> dict:
        """Receive an opponent control signal (enable / status / restart / quit)."""
        _auth()
        return accept(inboxes.controls, message)

    return mcp


def start_peer_server(name: str, host: str, port: int, token: str | None = None) -> PeerServer:
    """Start this peer's MCP server in a background daemon thread, returning a handle.

    We drive uvicorn directly (not ``FastMCP.run``) so the caller can stop it gracefully
    (``PeerServer.stop``); the ASGI app, ``/mcp`` path and tools match ``FastMCP.run``.
    """
    _ensure_port_free(host, port)
    inboxes = PeerInboxes()
    app = build_peer_server(name, inboxes, token).http_app()
    config = uvicorn.Config(
        app, host=host, port=port, log_level="warning", timeout_graceful_shutdown=5
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name=f"mcp-{name}")
    thread.start()
    while not server.started:  # don't return until the socket is accepting connections
        if not thread.is_alive():
            raise NetworkError(f"peer MCP server for {name} failed to start on {host}:{port}")
        time.sleep(0.02)
    return PeerServer(inboxes, server, thread)
