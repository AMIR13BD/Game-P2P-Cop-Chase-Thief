"""P19 fault-injection over the real path: technical-loss on an unreachable opponent,
and retry-recovery over the real FastMCP transport after a transient drop."""

import socket
import subprocess
import sys
import time

import anyio
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from thief_agent.constants import Role
from thief_agent.infra.reliability import ReliableCaller
from thief_agent.peer.net_runtime import run_networked
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

PORT, TOKEN = 8814, "FAULTTOK"


def _wait(port, t=40):
    end = time.time() + t
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def test_unreachable_opponent_yields_technical_series():
    cfg = validate(DEFAULT_GAME_CONFIG)
    res = anyio.run(
        run_networked,
        "http://127.0.0.1:8899/mcp",
        TOKEN,
        cfg,
        Role.POLICE,
        "amireman-police",
        "0" * 40,
        DevTestSigner(),
        1234,
        None,
        0.4,
        2,
        0.0,
    )
    assert len(res["sub_games"]) == 6
    assert all(s["outcome"] == "technical" for s in res["sub_games"])
    assert res["self_total"] == 0 and res["opp_total"] == 0


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
    assert _wait(PORT), "responder did not start"
    yield
    proc.terminate()
    try:
        proc.wait(10)
    except subprocess.TimeoutExpired:
        proc.kill()


def test_reliable_retry_recovers_over_real_transport(server):
    calls = {"n": 0}

    async def main():
        transport = StreamableHttpTransport(
            f"http://127.0.0.1:{PORT}/mcp", headers={"Authorization": f"Bearer {TOKEN}"}
        )
        async with Client(transport) as client:

            async def send(req):
                calls["n"] += 1
                if calls["n"] == 1:
                    raise ConnectionError("injected transient drop")
                data = (await client.call_tool("version", {})).data
                data.setdefault("request_id", req["request_id"])
                data.setdefault("session_id", req["session_id"])
                return data

            rc = ReliableCaller(send, timeout_s=5.0, retries=3, backoff_s=0.0, session_id="t")
            return await rc.call({"probe": 1})

    data = anyio.run(main)
    assert data.get("group") and calls["n"] == 2  # first attempt dropped, retry succeeded
