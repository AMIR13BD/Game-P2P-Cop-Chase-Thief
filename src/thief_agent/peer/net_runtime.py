"""Driver of a distributed six-sub-game series over real FastMCP transport (ReliableCaller
+ per-sub-game watchdog). A public tunnel can drop the streaming session mid-series; each
attempt runs isolated (see net_reconnect) so a drop is charged to the current sub-game and
the driver RECONNECTS a fresh session to finish the rest -- one recoverable interruption
never turns every remaining game technical. Programmer errors are NOT swallowed."""

from ..exceptions import ConfigError
from ..infra.reliability import ReliableCaller, new_session_id
from ..infra.tunnel import validate_public_endpoint
from ..peer.handshake import local_hello
from ..peer.net_driver import (
    default_connect,
    exchange_confirmation,
    make_send,
    play_subgame,
    role_for,
    score_row,
    technical_row,
)
from ..peer.net_reconnect import is_recoverable, recoverable_reason, run_isolated
from ..peer.watchdog import Watchdog
from ..shared.config_hash import config_sha256
from ..strategy.profiling import ProfileStore

SUB_GAMES = 6


class _Series:
    """Mutable progress for one series so it can resume across reconnects."""

    def __init__(self, terms):
        self.subs, self.role_seq = [], []
        self.s_tot = self.o_tot = 0
        self.peer_commit = self.peer_ident = self.confirmations = None
        self.opp_id = "peer"
        self.n = 1  # next sub-game to play
        self.began = None  # sub-game this attempt actually started (vs. failing at connect)
        self.handshook = terms is None


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
    connect=None,
):
    validate_public_endpoint(url)  # fail closed on malformed / non-TLS public endpoint
    to = timeout_s if timeout_s is not None else cfg.get("response_timeout_sec", 30)
    tr = retries if retries is not None else cfg.get("max_retries", 3)
    bo = backoff_s if backoff_s is not None else cfg.get("retry_backoff_sec", 5)
    connect = connect or default_connect
    store = ProfileStore()  # one profile for this single-opponent series
    s = _Series(terms)
    last_reason = "series incomplete"
    attempts = 0
    while s.n <= SUB_GAMES and attempts < 3 * SUB_GAMES:
        attempts += 1
        s.began = None

        async def _attempt():
            async with connect(url, token) as client:
                rc = ReliableCaller(
                    make_send(client),
                    timeout_s=to,
                    retries=tr,
                    backoff_s=bo,
                    session_id=new_session_id(f"{group}-net"),
                )
                await _run_session(rc, cfg, natural, group, github_commit, signer, terms, store, s)

        exc = await run_isolated(_attempt)  # isolated so a crashed session can't block reconnect
        if exc is None:
            continue  # session finished cleanly (all games + confirmation) -> loop exits
        if not is_recoverable(exc):
            raise exc  # never swallow an unexpected programmer error
        last_reason = recoverable_reason(exc)
        if s.handshook and s.began == s.n and s.n <= SUB_GAMES:
            drole = role_for(natural, s.n).value  # THIS sub-game was reached and failed
            if len(s.role_seq) < s.n:
                s.role_seq.append(drole)
            s.subs.append(technical_row(s.n, drole, last_reason))
            s.n += 1  # else: connect/handshake-level drop -> reconnect without losing a game
    while len(s.role_seq) < SUB_GAMES:
        s.role_seq.append(role_for(natural, len(s.role_seq) + 1).value)
    while len(s.subs) < SUB_GAMES:
        i = len(s.subs)
        s.subs.append(technical_row(i + 1, s.role_seq[i], last_reason))
    tie = s.s_tot == s.o_tot
    return {
        "sub_games": s.subs,
        "role_sequence": s.role_seq,
        "self_total": s.s_tot,
        "opp_total": s.o_tot,
        "series_tie": tie,
        "peer_commit": s.peer_commit,
        "peer_ident": s.peer_ident,
        "confirmations": s.confirmations,
        "winner": "tie" if tie else ("self" if s.s_tot > s.o_tot else "opp"),
    }


async def _run_session(rc, cfg, natural, group, github_commit, signer, terms, store, s):
    """Play remaining sub-games (from s.n) on ONE live session, then confirm. Any transport
    failure propagates so the caller can reconnect and resume where we stopped."""
    if not s.handshook:
        he = await rc.call({"tool": "hello", "args": local_hello(group, terms)})
        s.peer_commit, s.peer_ident = he.get("github_commit"), he.get("ident")
        s.opp_id = he.get("group") or s.opp_id
        neg = await rc.call({"tool": "negotiate", "args": {"config_sha256": config_sha256(terms)}})
        if not neg.get("agreed"):
            raise ConfigError("config negotiation failed")
        s.handshook = True
    wd_th = cfg.get("watchdog_timeout_sec", 60)
    while s.n <= SUB_GAMES:
        n, drole = s.n, role_for(natural, s.n).value
        if len(s.role_seq) < n:
            s.role_seq.append(drole)
        s.began = n  # we reached this sub-game; a drop here is charged to it
        prof = store.get(s.opp_id)
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
        if sg["opp_records"]:  # learn only from valid audited opponent evidence
            store.get(s.opp_id).observe_subgame(sg["opp_records"], signer, sg["outcome"])
        row, self_s, opp_s = score_row(n, drole, sg)
        s.s_tot += self_s
        s.o_tot += opp_s
        s.subs.append(row)
        s.n += 1
    s.confirmations = await exchange_confirmation(
        rc, s.subs, s.s_tot, s.o_tot, group, s.opp_id, signer
    )
