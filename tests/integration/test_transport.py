"""P18 transport gate: real FastMCP servers launched as separate localhost processes."""

import socket
import subprocess
import sys
import time

import anyio
import pytest
from fastmcp.exceptions import ToolError

from thief_agent.infra.mcp_client import PeerClient
from thief_agent.peer.handshake import PROTOCOL_VERSION, SCHEMA_VERSION
from thief_agent.shared.config_hash import config_sha256
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

MAIN, MM = 8811, 8812
GOOD, REV = "GOOD", "REV"


def _url(port):
    return f"http://127.0.0.1:{port}/mcp"


def _wait(port, t=40):
    end = time.time() + t
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def _spawn(port, extra):
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "thief_agent",
            "serve",
            "--port",
            str(port),
            "--token",
            f"{GOOD},{REV}",
            "--revoked",
            REV,
            *extra,
        ]
    )
    assert _wait(port), f"server on {port} did not start"
    return proc


@pytest.fixture(scope="module")
def servers():
    procs = [_spawn(MAIN, []), _spawn(MM, ["--grid", "9"])]
    yield
    for p in procs:
        p.terminate()
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            p.kill()


def _call(port, token, tool, payload=None):
    client = PeerClient(_url(port), token)
    if tool == "version":
        return anyio.run(client.version)
    return anyio.run(client.call, tool, payload)


def test_connect_and_authenticate(servers):
    assert _call(MAIN, GOOD, "version")["group"]


def test_invalid_credential_rejected(servers):
    with pytest.raises(ToolError):
        _call(MAIN, "NOPE", "version")


def test_revoked_credential_rejected(servers):
    with pytest.raises(ToolError):
        _call(MAIN, REV, "version")


def test_malformed_message_rejected(servers):
    with pytest.raises(ToolError):
        _call(MAIN, GOOD, "exchange", {"step": 1})  # missing required keys


def test_negotiate_agrees_same_config(servers):
    d = _call(MAIN, GOOD, "negotiate", {"config_sha256": config_sha256(DEFAULT_GAME_CONFIG)})
    assert d["agreed"] and d["config_sha256"] == config_sha256(DEFAULT_GAME_CONFIG)


def test_config_mismatch_refused(servers):
    with pytest.raises(ToolError):
        _call(MM, GOOD, "negotiate", {"config_sha256": config_sha256(DEFAULT_GAME_CONFIG)})


def test_version_mismatch_refused(servers):
    with pytest.raises(ToolError):
        _call(MAIN, GOOD, "hello", {"protocol_version": "WRONG", "schema_version": SCHEMA_VERSION})


def test_schema_mismatch_refused(servers):
    with pytest.raises(ToolError):
        _call(MAIN, GOOD, "hello", {"protocol_version": PROTOCOL_VERSION, "schema_version": "9.9"})


def test_legal_protocol_exchange(servers):
    _call(MAIN, GOOD, "start_subgame", {"sub_game": 1, "responder_role": "thief"})
    r = _call(
        MAIN,
        GOOD,
        "exchange",
        {"step": 1, "sender": "police", "commit": "c", "hint": "hi", "scent": {}},
    )
    assert "msg" in r and "claim_response" in r
