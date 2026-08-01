"""Driver of a distributed six-sub-game series over real FastMCP transport, routed
through the production ReliableCaller (timeout/retry/backoff/correlation) with a
per-sub-game watchdog. Defined failures -> deterministic technical loss; unexpected
programmer errors are NOT swallowed."""

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from ..exceptions import ConfigError, ExhaustedRetriesError, ProtocolError
from ..infra.reliability import ReliableCaller, new_session_id
from ..infra.tunnel import validate_public_endpoint
from ..peer.handshake import local_hello
from ..peer.net_driver import make_send, play_subgame, role_for, score_row, technical_row
from ..peer.watchdog import Watchdog
from ..report.confirm import confirmation_summary, final_hash, make_confirmation
from ..shared.config_hash import config_sha256
from ..strategy.profiling import ProfileStore

SUB_GAMES = 6


async def run_networked(
    url,
    token,
    cfg,
    natural,
    group,
    github_commit,
    signer,
    seed=1234,
    terms=None,
    timeout_s=None,
    retries=None,
    backoff_s=None,
):
    validate_public_endpoint(url)  # fail closed on malformed / non-TLS public endpoint
    to = timeout_s if timeout_s is not None else cfg.get("response_timeout_sec", 30)
    tr = retries if retries is not None else cfg.get("max_retries", 3)
    bo = backoff_s if backoff_s is not None else cfg.get("retry_backoff_sec", 5)
    wd_th = cfg.get("watchdog_timeout_sec", 60)
    transport = StreamableHttpTransport(url, headers={"Authorization": f"Bearer {token}"})
    subs, role_seq, s_tot, o_tot = [], [], 0, 0
    peer_commit = None
    peer_ident = None
    confirmations = None
    fill_reason = "series incomplete"  # reason stamped on any technical fill sub-games
    store = ProfileStore()  # one profile for this single-opponent series
    opp_id = "peer"
    try:
        async with Client(transport) as client:
            rc = ReliableCaller(
                make_send(client),
                timeout_s=to,
                retries=tr,
                backoff_s=bo,
                session_id=new_session_id(f"{group}-net"),
            )
            if terms is not None:
                he = await rc.call({"tool": "hello", "args": local_hello(group, terms)})
                peer_commit = he.get("github_commit")
                peer_ident = he.get("ident")
                opp_id = he.get("group") or opp_id
                neg = await rc.call(
                    {"tool": "negotiate", "args": {"config_sha256": config_sha256(terms)}}
                )
                if not neg.get("agreed"):
                    raise ConfigError("config negotiation failed")
            for n in range(1, SUB_GAMES + 1):
                drole = role_for(natural, n).value
                role_seq.append(drole)
                prof = store.get(opp_id)
                try:
                    sg = await play_subgame(
                        rc,
                        cfg,
                        drole,
                        n,
                        group,
                        github_commit,
                        signer,
                        Watchdog(wd_th),
                        prof.features(),
                        prof.hint_credibility(),
                    )
                except (ExhaustedRetriesError, ProtocolError) as exc:
                    sg = {
                        "outcome": "technical",
                        "records": [],
                        "opp_records": [],
                        "steps": 0,
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                if sg["opp_records"]:  # learn only from valid audited opponent evidence
                    store.get(opp_id).observe_subgame(sg["opp_records"], signer, sg["outcome"])
                row, self_s, opp_s = score_row(n, drole, sg)
                s_tot += self_s
                o_tot += opp_s
                subs.append(row)
            confirmations = await _exchange_confirmation(
                rc, subs, s_tot, o_tot, group, opp_id, signer
            )
    except (ExhaustedRetriesError, ProtocolError, ConnectionError, httpx.HTTPError, OSError) as exc:
        fill_reason = f"{type(exc).__name__}: {exc}"  # connect-level failure; fill technical
    except RuntimeError as exc:
        if "connect" not in str(exc).lower():
            raise  # never swallow unexpected programmer errors
        fill_reason = f"RuntimeError: {exc}"
    while len(role_seq) < SUB_GAMES:
        role_seq.append(role_for(natural, len(role_seq) + 1).value)
    while len(subs) < SUB_GAMES:
        subs.append(technical_row(len(subs) + 1, role_seq[len(subs)], fill_reason))
    tie = s_tot == o_tot
    return {
        "sub_games": subs,
        "role_sequence": role_seq,
        "self_total": s_tot,
        "opp_total": o_tot,
        "series_tie": tie,
        "peer_commit": peer_commit,
        "peer_ident": peer_ident,
        "confirmations": confirmations,
        "winner": "tie" if tie else ("self" if s_tot > o_tot else "opp"),
    }


async def _exchange_confirmation(rc, subs, s_tot, o_tot, group, opp_id, signer):
    """P22: build the role-symmetric final, obtain the peer's own signed confirmation,
    and pair it with ours. Hash disagreement (or a missing peer confirmation) fails
    closed to None so no false mutual agreement is recorded."""
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
