"""Finding 2: server-side idempotency over the real transport. A retried identical
request causes exactly one state transition and returns the cached response."""

import socket
import subprocess
import sys
import time

import anyio
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError

PORT, TOKEN = 8815, "IDEMTOK"


def _wait(port, t=40):
    end = time.time() + t
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def _tp():
    return StreamableHttpTransport(
        f"http://127.0.0.1:{PORT}/mcp", headers={"Authorization": f"Bearer {TOKEN}"}
    )


@pytest.fixture(scope="module")
def server():
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "thief_agent",
            "serve",
            "--port",
            str(PORT),
            "--token",
            TOKEN,
            "--group",
            "opponent",
        ]
    )
    assert _wait(PORT), "server did not start"
    yield
    proc.terminate()
    try:
        proc.wait(10)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_retry_same_request_id_one_state_transition(server):
    async def main():
        async with Client(_tp()) as c:
            await c.call_tool(
                "start_subgame", {"payload": {"sub_game": 1, "responder_role": "thief"}}
            )
            msg = {
                "step": 1,
                "sender": "police",
                "commit": "c",
                "hint": "h",
                "scent": {},
                "_rid": "R1",
                "_sid": "S",
            }
            r1 = (await c.call_tool("exchange", {"payload": msg})).data  # attempt 1 (processed)
            r2 = (await c.call_tool("exchange", {"payload": msg})).data  # attempt 2 (retry)
            return r1, r2

    r1, r2 = anyio.run(main)
    assert r1["msg"]["step"] == r2["msg"]["step"]  # exactly one state transition
    assert r1 == r2  # cached response returned


def test_same_request_id_changed_payload_rejected(server):
    async def main():
        async with Client(_tp()) as c:
            await c.call_tool(
                "start_subgame", {"payload": {"sub_game": 2, "responder_role": "thief"}}
            )
            m1 = {
                "step": 1,
                "sender": "police",
                "commit": "c",
                "hint": "h",
                "scent": {},
                "_rid": "R2",
                "_sid": "S",
            }
            await c.call_tool("exchange", {"payload": m1})
            m2 = {**m1, "hint": "CHANGED"}
            with pytest.raises(ToolError):
                await c.call_tool("exchange", {"payload": m2})

    anyio.run(main)
