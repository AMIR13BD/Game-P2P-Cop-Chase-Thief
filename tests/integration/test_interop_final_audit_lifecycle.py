"""The final-audit shutdown race, reproduced at the socket level (no gameplay, no series).

The opponent's LAST ``submit_audit`` enqueues its payload and only THEN does uvicorn flush
the tool's HTTP ``200``. Our runtime unblocks the instant the payload is enqueued
(``poll_audit`` returns), so the process could reach interpreter exit — killing the daemon
server thread — while that ``200`` was still on the wire. Over a tunnel the peer then sees
``502 Bad Gateway`` / a timeout.

These two tests model that exact lifecycle against a REAL running peer server:
``slow_put`` widens the post-enqueue flush window (as a tunnel would), the "runner" then
shuts the server down the moment it has drained the audit. The abrupt path (a daemon-thread
kill == uvicorn ``force_exit``, no drain) reproduces the failure; ``PeerServer.stop`` (the
fix) keeps serving until the peer's request drains, so the peer's call succeeds.
"""

import asyncio
import logging
import socket
import threading

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from thief_agent.interop.server import start_peer_server


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run_final_audit_scenario(abrupt: bool) -> dict:
    """Drive one peer ``submit_audit`` whose response is still flushing when we shut down."""
    logging.disable(logging.CRITICAL)  # uvicorn logs a cancelled-task traceback on force kill
    port = _free_port()
    server = start_peer_server("repro-final-audit", "127.0.0.1", port)

    # Widen the window between "consumer unblocks" (real put) and "HTTP response flushed"
    # (handler returns) — exactly the gap a tunnel introduces on the last audit.
    audits = server.inboxes.audits
    real_put = audits.put

    def slow_put(item, *a, **k):
        real_put(item, *a, **k)  # <- our poll_audit unblocks HERE
        threading.Event().wait(0.6)  # response is still on the wire for 0.6s after that

    audits.put = slow_put

    peer: dict = {"call_ok": None}

    def peer_call():
        async def go():
            url = f"http://127.0.0.1:{port}/mcp"
            async with Client(StreamableHttpTransport(url)) as client:
                res = await client.call_tool("submit_audit", {"payload": {"sender": "peer"}})
                peer["call_ok"] = res.data == {"ok": True}  # measured before session teardown

        try:
            asyncio.run(go())
        except Exception as exc:  # noqa: BLE001 - any transport failure is a failed delivery
            if peer["call_ok"] is None:
                peer["call_ok"] = False
            peer["error"] = f"{type(exc).__name__}: {str(exc)[:60]}"

    def runner():
        server.inboxes.audits.get(timeout=10)  # == runtime.poll_audit: unblocks at real_put
        if abrupt:
            # Model the OLD behaviour: process exits and the daemon server thread is killed
            # with the response un-flushed (uvicorn force_exit skips the connection drain).
            server._server.should_exit = True
            server._server.force_exit = True
            server._thread.join(8)
        else:
            server.stop()  # the fix: drain the peer's in-flight request, then stop gracefully

    tp = threading.Thread(target=peer_call)
    tr = threading.Thread(target=runner)
    tp.start()
    tr.start()
    tp.join(20)
    tr.join(20)
    logging.disable(logging.NOTSET)
    peer["server_thread_alive"] = server._thread.is_alive()
    return peer


def test_abrupt_shutdown_drops_final_audit_response():
    """BEFORE: killing the server the moment the audit is drained loses the peer's 200."""
    result = _run_final_audit_scenario(abrupt=True)
    assert result["call_ok"] is False, result  # peer saw the 502-equivalent transport failure


def test_graceful_stop_delivers_final_audit_response():
    """AFTER: PeerServer.stop keeps serving until the peer's submit_audit fully completes."""
    result = _run_final_audit_scenario(abrupt=False)
    assert result["call_ok"] is True, result  # peer got its {"ok": true}
    assert result["server_thread_alive"] is False  # and we still shut the server down cleanly
