"""FRIENDLY execution mode — a full official six-sub-game series that is STRUCTURALLY
unable to email a lecturer.

This module imports NOTHING from ``infra.gmail_*`` or ``report.emit``/``commands_report``:
there is no code path from a friendly run to the mail sender, no matter how the series
ends (success, failure, or a tamper forfeit). Artifacts are written locally; the result
is never marked ``counted-two-peer`` (the only mode our mail gate would ever accept), so
even if a later stage were handed this result it could not send it. Friendly play prints
``match_mode=friendly`` and ``lecturer_report_sent=False`` explicitly.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .artifacts_io import emit_artifacts
from .client import McpTransport
from .consensus import LEGACY
from .series import identity_for, mcp_servers_for, run_series
from .server import start_peer_server

MATCH_MODE = "friendly"
LECTURER_REPORT_SENT = False  # a friendly run can never flip this; there is no sender wired

__all__ = ["FriendlyResult", "emit_artifacts", "run_friendly"]


@dataclass
class FriendlyResult:
    game_id: str | None = None
    game_uid: str | None = None
    summaries: list = field(default_factory=list)
    artifacts: list = field(default_factory=list)
    result_doc: dict = field(default_factory=dict)
    clean: bool = False
    match_mode: str = MATCH_MODE
    lecturer_report_sent: bool = LECTURER_REPORT_SENT
    consensus_profile: str = LEGACY  # run metadata; never enters the signed terms


def run_friendly(
    group: str,
    opponent_url: str,
    natural_role: str,
    terms: dict,
    out_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8901,
    token: str | None = None,
    github_commit: str = "local",
    num_games: int = 6,
    seed: int = 1234,
    env: dict | None = None,
    turn_timeout: float = 180.0,
    identity: dict | None = None,
    public_mcp_url: str | None = None,
    listener=None,
    game_id: str | None = None,
    consensus_profile: str = LEGACY,
) -> FriendlyResult:
    """Stand up our server, dial the opponent, play a full friendly series, write artifacts.

    NEVER sends email. NEVER marks the match counted. Returns a FriendlyResult whose
    ``lecturer_report_sent`` is always False.
    """
    identity = identity or identity_for(
        group, mcp_servers=mcp_servers_for(public_mcp_url), github_commit=github_commit
    )
    server = start_peer_server(f"interop-{group}", host, port, token)
    transport = McpTransport(opponent_url, server.inboxes, token=token, env=env)
    try:
        series = run_series(
            terms,
            natural_role,
            transport,
            group,
            github_commit,
            own_identity=identity,
            num_games=num_games,
            seed=seed,
            listener=listener,
            turn_timeout=turn_timeout,
            game_id=game_id,
            consensus_profile=consensus_profile,
        )
    finally:
        # Keep our server alive until the peer's FINAL submit_audit has flushed (fixes the
        # peer seeing 502/timeout on the last audit). See PeerServer.stop.
        server.stop()
    ended = datetime.now(UTC).isoformat()
    paths, result_doc = emit_artifacts(Path(out_dir), series, terms, ended)
    clean = len(series.summaries) == num_games and all(
        not s["audit"].get("tampered") and s["result"] != "timeout" for s in series.summaries
    )
    return FriendlyResult(
        game_id=series.game_id,
        game_uid=series.game_uid,
        summaries=series.summaries,
        artifacts=paths,
        result_doc=result_doc,
        clean=clean,
        consensus_profile=consensus_profile,
    )
