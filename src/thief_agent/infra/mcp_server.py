"""Real FastMCP peer server. Header bearer auth + revocation, version/schema and
config-hash agreement, malformed-message rejection, a concurrency/queue DoS guard,
request-correlation echo, and a responder match session."""

from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from ..peer.handshake import agree_config, check_compatibility, local_hello
from ..peer.net_engine import PeerHalf
from ..security.auth import AuthRegistry, bearer_from_header
from ..shared.gatekeeper import Gatekeeper
from ..strategy.police_greedy import PoliceGreedyBrain
from ..strategy.rng import make_rng
from ..strategy.thief_distance import ThiefDistanceBrain

REQ_MSG = ("step", "sender", "commit", "hint")
HIGH_RPM = 1_000_000  # per-turn game endpoint: DoS guard is concurrency/queue, not per-minute


@dataclass
class PeerConfig:
    group: str
    terms: dict
    flat_cfg: dict
    auth: AuthRegistry
    github_commit: str
    signer: Any
    seed: int = 1234


def _brain(role: str, seed: int):
    return (
        PoliceGreedyBrain(make_rng(seed))
        if role == "police"
        else ThiefDistanceBrain(make_rng(seed))
    )


def _echo(payload: object, result: dict) -> dict:
    if isinstance(payload, dict):
        result.setdefault("request_id", payload.get("_rid"))
        result.setdefault("session_id", payload.get("_sid"))
    return result


def build_server(pc: PeerConfig) -> FastMCP:
    mcp = FastMCP(f"peer-{pc.group}")
    session: dict = {}
    gk = Gatekeeper(
        HIGH_RPM, pc.flat_cfg.get("concurrent_requests", 2), pc.flat_cfg.get("queue_depth", 100)
    )

    def _auth() -> None:
        if not pc.auth.check(bearer_from_header(get_http_headers(include_all=True))):
            raise PermissionError("unauthorized or revoked credential")

    @mcp.tool
    def version() -> dict:
        _auth()
        return local_hello(pc.group, pc.terms)

    @mcp.tool
    def hello(payload: dict) -> dict:
        _auth()
        if isinstance(payload, dict) and payload.get("protocol_version"):
            check_compatibility(payload)
        return _echo(payload, {"hello": local_hello(pc.group, pc.terms), "group": pc.group})

    @mcp.tool
    def negotiate(payload: dict) -> dict:
        _auth()
        if not isinstance(payload, dict) or "config_sha256" not in payload:
            raise ValueError("malformed negotiate payload")
        return _echo(
            payload,
            {
                "agreed": True,
                "group": pc.group,
                "config_sha256": agree_config(pc.terms, payload["config_sha256"]),
            },
        )

    @mcp.tool
    def start_subgame(payload: dict) -> dict:
        _auth()
        n = int(payload["sub_game"])
        role = payload["responder_role"]
        session["half"] = PeerHalf(
            role,
            pc.flat_cfg,
            _brain(role, pc.seed + 100 + n),
            pc.group,
            pc.github_commit,
            pc.signer,
            n,
        )
        session["captured"] = False
        return _echo(payload, {"ok": True, "role": role, "group": pc.group})

    @mcp.tool
    def exchange(payload: dict) -> dict:
        _auth()
        if not isinstance(payload, dict) or any(k not in payload for k in REQ_MSG):
            raise ValueError("malformed turn message")
        gk.admit()
        try:
            half: PeerHalf = session["half"]
            caught_me = half.receive(payload)
            out = half.act()
            session["captured"] = session.get("captured") or caught_me
            return _echo(payload, {"msg": out, "claim_response": {"caught": caught_me}})
        finally:
            gk.release()

    @mcp.tool
    def finalize(payload: dict) -> dict:
        _auth()
        half = session.get("half")
        return _echo(
            payload,
            {"records": half.records if half else [], "captured": session.get("captured", False)},
        )

    return mcp
