"""Driver-side helpers for the networked series: reliable send, per-sub-game loop,
and score-row assembly. Kept separate so net_runtime.py stays within the line limit."""

import httpx
from fastmcp.exceptions import ToolError

from ..constants import Role, complement
from ..domain import scoring
from ..exceptions import ProtocolError
from ..peer.net_engine import PeerHalf
from ..strategy.production import make_gameplay_brain


def role_for(natural: Role, n: int) -> Role:
    return natural if n % 2 == 1 else complement(natural)


def brain(role, seed, horizon=35, profile=None, credibility=0.5, baseline=False):
    """Production adaptive brain by default; baseline only on explicit request."""
    return make_gameplay_brain(role, seed, horizon, profile, credibility, baseline)


def make_send(client):
    async def send(req):
        p = req["payload"]
        args = dict(p.get("args") or {})
        args["_rid"], args["_sid"] = req["request_id"], req["session_id"]
        try:
            data = (await client.call_tool(p["tool"], {"payload": args})).data
        except ToolError as exc:
            raise ProtocolError(str(exc)) from exc
        except (httpx.HTTPError, OSError) as exc:
            raise ConnectionError(str(exc)) from exc
        if isinstance(data, dict):
            data.setdefault("request_id", req["request_id"])
            data.setdefault("session_id", req["session_id"])
        return data

    return send


async def play_subgame(
    rc, cfg, drole, n, group, gc, signer, wd, profile=None, credibility=0.5, baseline=False
):
    rrole = complement(Role(drole)).value
    await rc.call({"tool": "start_subgame", "args": {"sub_game": n, "responder_role": rrole}})
    horizon = cfg.get("survival_threshold", 35)
    dbrain = brain(drole, 1000 + n, horizon, profile, credibility, baseline)
    half = PeerHalf(drole, cfg, dbrain, group, gc, signer, n)
    outcome = "survival"
    for step in range(1, cfg["max_moves"] + 1):
        if wd.stalled():
            outcome = "technical"
            break
        resp = await rc.call({"tool": "exchange", "args": half.act()})
        wd.heartbeat()
        if (resp.get("claim_response") or {}).get("caught") or half.receive(resp.get("msg", {})):
            outcome = "capture"
            break
        if step >= cfg["survival_threshold"]:
            break
    fin = await rc.call({"tool": "finalize", "args": {}})
    return {
        "outcome": outcome,
        "records": half.records,
        "opp_records": fin.get("records", []),
        "steps": half.step,
    }


def technical_row(n, drole):
    return {
        "sub_game": n,
        "self_role": drole,
        "outcome": "technical",
        "self_score": 0,
        "opp_score": 0,
        "steps": 0,
        "records": [],
        "opp_records": [],
        "trajectory": [],
    }


def score_row(n, drole, sg):
    pol, thf = scoring.score_outcome(sg["outcome"])
    self_s, opp_s = (pol, thf) if drole == "police" else (thf, pol)
    return (
        {
            "sub_game": n,
            "self_role": drole,
            "outcome": sg["outcome"],
            "self_score": self_s,
            "opp_score": opp_s,
            "steps": sg["steps"],
            "records": sg["records"],
            "opp_records": sg["opp_records"],
            "trajectory": [],
        },
        self_s,
        opp_s,
    )
