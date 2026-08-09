"""Driver-side helpers for the networked series: reliable send, per-sub-game loop,
and score-row assembly. Kept separate so net_runtime.py stays within the line limit."""

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError

from ..constants import Role, complement
from ..domain import scoring
from ..exceptions import ExhaustedRetriesError, ProtocolError
from ..infra.tunnel import tunnel_headers
from ..peer.net_engine import PeerHalf
from ..report.confirm import confirmation_summary, final_hash, make_confirmation
from ..strategy.production import make_gameplay_brain

# transport-level failures that justify isolating a sub-game and reconnecting a session
TRANSPORT_ERRORS = (ExhaustedRetriesError, ProtocolError, ConnectionError, httpx.HTTPError, OSError)


def transport_reason(exc) -> str:
    """A never-empty technical reason: many tunnel drops carry no message."""
    return f"{type(exc).__name__}: {str(exc) or 'connection dropped (transport)'}"


def default_connect(url, token):
    # optional tunnel headers first (e.g. Localtonet warning-bypass); Authorization is
    # applied last so a tunnel header can never override it. An EMPTY token sends NO
    # Authorization header — matching the proven friendly transport and the reference
    # no-auth design (a bearer is attached only when one was actually agreed).
    headers = dict(tunnel_headers())
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return Client(StreamableHttpTransport(url, headers=headers))


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
            # many transport drops carry an empty message; keep the type name so the
            # technical reason is never a bare "ConnectError: "
            raise ConnectionError(str(exc) or type(exc).__name__) from exc
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


def technical_row(n, drole, reason=None):
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
        "reason": reason,
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
            "reason": sg.get("reason"),
        },
        self_s,
        opp_s,
    )


async def exchange_confirmation(rc, subs, s_tot, o_tot, group, opp_id, signer):
    """P22: build the role-symmetric final, obtain the peer's own signed confirmation, and
    pair it with ours. Hash disagreement (or a missing peer confirmation) fails closed to
    None so no false mutual agreement is recorded."""
    series = {"sub_games": subs, "self_total": s_tot, "opp_total": o_tot}
    final = confirmation_summary(series, group, opp_id)
    fhash = final_hash(final)
    self_conf = make_confirmation(group, fhash, signer)
    try:
        resp = await rc.call({"tool": "confirm", "args": {"final": final}})
    except (ExhaustedRetriesError, ProtocolError):
        return None
    peer_conf = resp.get("confirmation") if isinstance(resp, dict) else None
    if not peer_conf or peer_conf.get("final_sha256") != fhash:
        return None  # peer disagreed or sent nothing -> no agreement
    return {group: self_conf, peer_conf.get("group", opp_id): peer_conf}
