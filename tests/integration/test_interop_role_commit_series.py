"""A real six-sub-game series must report, for EVERY sub-game, the SHA of the repository
that actually played it — ours and the peer's alike (book ch.5.5 / App. E rule 53).

Both sides run our production runtime over the loopback transport (no sockets), each with
its own cop/thief SHAs, so the peer half of every assertion is produced by an independent
reader of what we put on the wire rather than by the writer of it.
"""

import threading

from interop_loopback import Boxes, Loopback

from thief_agent.interop.compliance import problems_with
from thief_agent.interop.friendly import emit_artifacts
from thief_agent.interop.series import identity_for, run_series
from thief_agent.interop.terms import default_terms

OUR_POLICE = "76206075faf12730669346d2e4632a5c50b934b9"
OUR_THIEF = "c74eeecb8f8a6d1264004d1af3678b02ebebb36e"
PEER_POLICE = "909cec2c621da776a30e8adfec27b069554c45fd"
PEER_THIEF = "c0f4f23e73dcd67f456401b2e57fc5be764a7f55"
PEER_REPOS = {"cop": "https://github.com/peer/cop", "thief": "https://github.com/peer/thief"}


def _play(role_commits=True):
    """One full series; returns (our SeriesResult, the peer's SeriesResult, terms)."""
    a, b = Boxes(), Boxes()
    terms = default_terms()
    out: dict = {}

    def side(role, group, own_boxes, peer_boxes, default_sha, identity):
        out[group] = run_series(
            terms,
            role,
            Loopback(own_boxes, peer_boxes),
            group,
            default_sha,
            own_identity=identity,
            num_games=6,
            turn_timeout=8.0,
        )

    ours = identity_for(
        "amireman",
        mcp_servers={"cop": "https://ours.example/mcp", "thief": "https://ours.example/mcp"},
        github_commit=OUR_THIEF,
        role_commits={"cop": OUR_POLICE, "thief": OUR_THIEF} if role_commits else None,
    )
    theirs = identity_for(
        "salareen",
        repos=PEER_REPOS,
        mcp_servers={"cop": "https://peer.example/mcp", "thief": "https://peer.example/mcp"},
        members=["Peer One"],
        github_commit=PEER_THIEF,
        role_commits={"cop": PEER_POLICE, "thief": PEER_THIEF} if role_commits else None,
    )
    t1 = threading.Thread(target=side, args=("thief", "amireman", a, b, OUR_THIEF, ours))
    t2 = threading.Thread(target=side, args=("police", "salareen", b, a, PEER_THIEF, theirs))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return out["amireman"], out["salareen"], terms


def test_our_report_stamps_the_role_repo_for_every_sub_game(tmp_path):
    ours, _, terms = _play()
    _, doc = emit_artifacts(tmp_path / "run", ours, terms)
    got = {r["sub_game_number"]: r["github_commit"] for r in doc["sub_games"]}
    for n in (1, 3, 5):  # we are thief on the odd sub-games, the peer is police
        assert got[n]["amireman"] == OUR_THIEF
        assert got[n]["salareen"] == PEER_POLICE
    for n in (2, 4, 6):
        assert got[n]["amireman"] == OUR_POLICE
        assert got[n]["salareen"] == PEER_THIEF
    assert problems_with(doc) == []


def test_the_peer_records_our_role_sha_from_what_we_sent(tmp_path):
    """The other side never sees our config — only our handshake identity. Its report is
    the proof that a compatible peer can record the right SHA for us."""
    _, peer, terms = _play()
    _, doc = emit_artifacts(tmp_path / "peer", peer, terms)
    got = {r["sub_game_number"]: r["github_commit"]["amireman"] for r in doc["sub_games"]}
    assert [got[n] for n in (1, 3, 5)] == [OUR_THIEF] * 3
    assert [got[n] for n in (2, 4, 6)] == [OUR_POLICE] * 3


def test_both_group_details_publish_the_two_role_shas(tmp_path):
    ours, _, terms = _play()
    _, doc = emit_artifacts(tmp_path / "run", ours, terms)
    blocks = {b["group_id"]: b for b in doc["group_details"].values()}
    assert blocks["amireman"]["github_commits"] == {"cop": OUR_POLICE, "thief": OUR_THIEF}
    assert blocks["salareen"]["github_commits"] == {"cop": PEER_POLICE, "thief": PEER_THIEF}
    assert set(doc["links"]["github"]["amireman"]) == {"cop", "thief"}
    assert set(doc["links"]["github"]["salareen"]) == {"cop", "thief"}


def test_declaring_per_role_shas_does_not_move_the_consensus_digest():
    """The digest is settled between peers; commits are not in its preimage. A series that
    declares role SHAs and one that does not must settle to the very same bytes."""
    with_roles, peer_with, _ = _play(role_commits=True)
    without, peer_without, _ = _play(role_commits=False)
    assert with_roles.consensus_sha == without.consensus_sha
    assert with_roles.sha_match and without.sha_match
    assert peer_with.consensus_sha == peer_without.consensus_sha == with_roles.consensus_sha
