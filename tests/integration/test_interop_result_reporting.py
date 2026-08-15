"""End-to-end reporting integration: a real in-process six-sub-game series must produce a
``result_<game_id>.json`` that satisfies every book-mandatory field, with BOTH groups' real
per-sub-game runtime SHAs recorded (book ch.5.5 / App. E rules 53-54, ch.9 §9.3.3-§9.4).

Both sides run our production runtime over the loopback transport (no sockets)."""

import json
import threading
from pathlib import Path

from interop_loopback import Boxes, Loopback

from thief_agent.interop.compliance import assert_compliant, problems_with
from thief_agent.interop.friendly import emit_artifacts
from thief_agent.interop.ids import result_name
from thief_agent.interop.series import identity_for, run_series
from thief_agent.interop.terms import default_terms

OUR_SHA = "1a" * 20
PEER_SHA = "2b" * 20
PEER_REPOS = {"cop": "https://github.com/peer/cop", "thief": "https://github.com/peer/thief"}
PEER_MCP = {"cop": "https://peer.example/mcp", "thief": "https://peer.example/mcp"}


def _identity(group, sha, declare_commit=True):
    """The peer identity a side advertises. ``declare_commit=False`` reproduces a peer whose
    identity block carries no commit at all (it still signs one into its Step-0 record)."""
    ident = identity_for(
        group,
        repos=PEER_REPOS,
        mcp_servers=PEER_MCP,
        members=["Peer Member"],
        github_commit=sha if declare_commit else "",
    )
    return ident


def _play(peer_declares_commit=True):
    a, b = Boxes(), Boxes()
    terms = default_terms()
    out: dict = {}

    def side(role, group, own_boxes, peer_boxes, sha, identity):
        out[group] = run_series(
            terms,
            role,
            Loopback(own_boxes, peer_boxes),
            group,
            sha,  # the commit our Step-0 record is bound to
            own_identity=identity,
            num_games=6,
            turn_timeout=8.0,
        )

    ours = identity_for(
        "amireman",
        mcp_servers={"cop": "https://ours.example/mcp", "thief": "https://ours.example/mcp"},
        github_commit=OUR_SHA,
    )
    theirs = _identity("peer-group", PEER_SHA, declare_commit=peer_declares_commit)
    t1 = threading.Thread(target=side, args=("thief", "amireman", a, b, OUR_SHA, ours))
    t2 = threading.Thread(target=side, args=("police", "peer-group", b, a, PEER_SHA, theirs))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return out["amireman"], terms


def test_real_series_result_is_book_compliant(tmp_path):
    series, terms = _play()
    paths, doc = emit_artifacts(tmp_path / "run", series, terms, ended="2026-09-01T12:00:00+00:00")
    assert problems_with(doc) == []
    assert_compliant(doc)
    written = [p.name for p in paths]
    assert result_name(series.game_id) in written  # the exact emailed filename
    on_disk = json.loads((Path(tmp_path) / "run" / result_name(series.game_id)).read_text())
    assert on_disk == doc and len(on_disk["sub_games"]) == 6


def test_both_group_shas_are_recorded_for_every_sub_game(tmp_path):
    series, terms = _play()
    _, doc = emit_artifacts(tmp_path / "run", series, terms)
    for row in doc["sub_games"]:
        assert row["github_commit"]["amireman"] == OUR_SHA
        assert row["github_commit"]["peer-group"] == PEER_SHA


def test_peer_that_omits_the_commit_in_its_identity_is_still_reported(tmp_path):
    """The G012 case: the peer's identity block carried no commit. Its signed Step-0 reveal
    for that sub-game does, so the report is complete instead of blank — and still never
    invented (the value equals the peer's real runtime SHA)."""
    series, terms = _play(peer_declares_commit=False)
    _, doc = emit_artifacts(tmp_path / "run", series, terms)
    assert [r["github_commit"]["peer-group"] for r in doc["sub_games"]] == [PEER_SHA] * 6
    assert problems_with(doc) == []
