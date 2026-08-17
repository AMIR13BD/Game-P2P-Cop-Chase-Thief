"""Writing the four official artifacts, with every filename proven to stay in ``out_dir``.

Split out of ``friendly.py`` so both modules stay inside the repository's 150-line
ceiling; the emitted bytes are unchanged.

Every name here is built from ``game_id``, which is derived from the OPPONENT's declared
group id. ``guard.check_group_id`` refuses a path-shaped identity at the handshake, and
``guard.safe_child`` independently re-proves each resolved path before anything is
written — two defences on the same hazard, because the write is what is irreversible.
"""

from pathlib import Path

from ..domain.crypto import canonical_json
from .artifacts import build_config, build_declaration, build_log, build_result
from .consensus import LEGACY
from .guard import safe_child
from .submission import enrich_result


def write_doc(out_dir: Path, name: str, doc: dict) -> Path:
    """Write one artifact as canonical bytes, refusing any name that escapes ``out_dir``."""
    path = safe_child(out_dir, name)
    path.write_bytes(canonical_json(doc).encode("utf-8") + b"\n")
    return path


def emit_artifacts(out_dir: Path, series, terms: dict, ended: str = "") -> tuple[list, dict]:
    """Write the four official artifacts for a completed series into one flat directory."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    gid, guid = series.game_id, series.game_uid
    ours = series.own_identity["group_id"]
    theirs = series.peer_identity.get("group_id", "opponent")
    commits = {
        ours: series.own_identity.get("github_commit", ""),
        theirs: series.peer_identity.get("github_commit", ""),
    }
    started = series.summaries[0]["started_at"] if series.summaries else ""
    paths = [
        write_doc(
            out_dir,
            f"declaration_{gid}.json",
            build_declaration(
                gid,
                guid,
                series.own_identity,
                series.peer_identity,
                len(series.summaries),
                started,
                ended,
            ),
        )
    ]
    for summary in series.summaries:
        n = summary["sub_game_number"]
        paths.append(
            write_doc(out_dir, f"config_{gid}_g{n:02d}.json", build_config(terms, gid, guid, n))
        )
        paths.append(
            write_doc(
                out_dir, f"log_{gid}_g{n:02d}.json", build_log(summary, gid, guid, ours, theirs)
            )
        )
    result_doc = build_result(gid, guid, ours, theirs, series.summaries, commits)
    consensus = {
        "sha256": series.consensus_sha,
        "peer_sha256": series.peer_consensus_sha,
        "sha_match": series.sha_match,
        # In-process only: enrich_result reads this to pick the profile for its fallback
        # digest. It is NOT written into the artifact, so the emitted bytes are unchanged.
        "profile": getattr(series, "consensus_profile", LEGACY),
    }
    args = (series.summaries, series.own_identity, series.peer_identity, consensus)
    result_doc = enrich_result(result_doc, *args)
    paths.append(write_doc(out_dir, f"result_{gid}.json", result_doc))
    return paths, result_doc
