"""Driver of a distributed six-sub-game series over real FastMCP transport, routed
through the production ReliableCaller (timeout/retry/backoff/correlation) with a
per-sub-game watchdog. Defined failures -> deterministic technical loss; unexpected
programmer errors are NOT swallowed."""

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from ..exceptions import ConfigError, ExhaustedRetriesError, ProtocolError
from ..infra.reliability import ReliableCaller
from ..peer.handshake import local_hello
from ..peer.net_driver import make_send, play_subgame, role_for, score_row, technical_row
from ..peer.watchdog import Watchdog
from ..shared.config_hash import config_sha256

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
    to = timeout_s if timeout_s is not None else cfg.get("response_timeout_sec", 30)
    tr = retries if retries is not None else cfg.get("max_retries", 3)
    bo = backoff_s if backoff_s is not None else cfg.get("retry_backoff_sec", 5)
    wd_th = cfg.get("watchdog_timeout_sec", 60)
    transport = StreamableHttpTransport(url, headers={"Authorization": f"Bearer {token}"})
    subs, role_seq, s_tot, o_tot = [], [], 0, 0
    peer_commit = None
    peer_ident = None
    try:
        async with Client(transport) as client:
            rc = ReliableCaller(
                make_send(client), timeout_s=to, retries=tr, backoff_s=bo, session_id=f"{group}-net"
            )
            if terms is not None:
                he = await rc.call({"tool": "hello", "args": local_hello(group, terms)})
                peer_commit = he.get("github_commit")
                peer_ident = he.get("ident")
                neg = await rc.call(
                    {"tool": "negotiate", "args": {"config_sha256": config_sha256(terms)}}
                )
                if not neg.get("agreed"):
                    raise ConfigError("config negotiation failed")
            for n in range(1, SUB_GAMES + 1):
                drole = role_for(natural, n).value
                role_seq.append(drole)
                try:
                    sg = await play_subgame(
                        rc, cfg, drole, n, group, github_commit, signer, Watchdog(wd_th)
                    )
                except (ExhaustedRetriesError, ProtocolError):
                    sg = {"outcome": "technical", "records": [], "opp_records": [], "steps": 0}
                row, self_s, opp_s = score_row(n, drole, sg)
                s_tot += self_s
                o_tot += opp_s
                subs.append(row)
    except (ExhaustedRetriesError, ProtocolError, ConnectionError, httpx.HTTPError, OSError):
        pass  # connect-level failure -> remaining sub-games filled technical below
    except RuntimeError as exc:
        if "connect" not in str(exc).lower():
            raise  # never swallow unexpected programmer errors
    while len(role_seq) < SUB_GAMES:
        role_seq.append(role_for(natural, len(role_seq) + 1).value)
    while len(subs) < SUB_GAMES:
        subs.append(technical_row(len(subs) + 1, role_seq[len(subs)]))
    tie = s_tot == o_tot
    return {
        "sub_games": subs,
        "role_sequence": role_seq,
        "self_total": s_tot,
        "opp_total": o_tot,
        "series_tie": tie,
        "peer_commit": peer_commit,
        "peer_ident": peer_ident,
        "winner": "tie" if tie else ("self" if s_tot > o_tot else "opp"),
    }
