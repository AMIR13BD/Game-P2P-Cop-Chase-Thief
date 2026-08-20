"""Per-ROLE runtime commit SHAs (book ch.5.5 / App. E rule 53).

A pairing submits a cop repo AND a thief repo, but a series runs from one of them, so
stamping the launching repo's HEAD on all six sub-games mislabels half of them. These pin
the three properties that fix has to hold: the right SHA per role, a peer able to read it
out of the identity we send, and NOTHING new reaching the consensus preimage.
"""

from thief_agent.interop import commits, rolecommit
from thief_agent.interop.artifacts import build_result, group_block
from thief_agent.interop.consensus import OFFICIAL_REFERENCE_V1, canonical_rows, consensus_sha
from thief_agent.interop.series import identity_for

POLICE_SHA = "76206075faf12730669346d2e4632a5c50b934b9"
THIEF_SHA = "c74eeecb8f8a6d1264004d1af3678b02ebebb36e"
ROLES = {"cop": POLICE_SHA, "thief": THIEF_SHA}


def _summaries(with_role_commits: bool):
    """Six sub-games, thief on odd ones (roles alternate), as run_series records them."""
    out = []
    for n in range(1, 7):
        role = "thief" if n % 2 else "police"
        s = {
            "sub_game_number": n,
            "role": role,
            "result": "survival" if role == "thief" else "capture",
            "steps": 35 if role == "thief" else 12,
            "audit": {"log_verified": True, "tampered": False},
            "started_at": "2026-01-01T00:00:00+00:00",
            "duration_seconds": 1,
            "tokens_total": 0,
        }
        if with_role_commits:
            s["own_github_commit"] = THIEF_SHA if role == "thief" else POLICE_SHA
        out.append(s)
    return out


# ---- resolution ------------------------------------------------------------------------


def test_unset_roles_fall_back_to_the_launching_repo_head():
    assert rolecommit.resolve(THIEF_SHA) == {"cop": THIEF_SHA, "thief": THIEF_SHA}


def test_each_role_takes_its_own_repo_sha():
    assert rolecommit.resolve(THIEF_SHA, POLICE_SHA, THIEF_SHA) == ROLES


def test_a_non_sha_argument_is_refused_rather_than_reported():
    assert rolecommit.resolve(THIEF_SHA, "not-a-sha")["cop"] == THIEF_SHA


# ---- the identity we put on the wire ---------------------------------------------------


def test_identity_without_role_commits_is_byte_identical_to_before():
    ident = identity_for("amireman", github_commit=THIEF_SHA)
    assert "github_commits" not in ident
    scoped, sha = rolecommit.view(ident, "police", THIEF_SHA)
    assert scoped is ident and sha == THIEF_SHA  # same object -> same wire bytes


def test_identity_declares_both_role_shas():
    ident = identity_for("amireman", github_commit=THIEF_SHA, role_commits=ROLES)
    assert ident["github_commits"] == ROLES
    assert ident["github_commit"] == ident["git_commit_hash"] == THIEF_SHA


def test_the_flat_commit_we_declare_is_the_role_actually_playing():
    ident = identity_for("amireman", github_commit=THIEF_SHA, role_commits=ROLES)
    as_police, police_sha = rolecommit.view(ident, "police", THIEF_SHA)
    as_thief, thief_sha = rolecommit.view(ident, "thief", THIEF_SHA)
    assert police_sha == POLICE_SHA and thief_sha == THIEF_SHA
    assert as_police["github_commit"] == as_police["git_commit_hash"] == POLICE_SHA
    assert as_thief["github_commit"] == THIEF_SHA


def test_a_peer_parser_reads_the_role_sha_out_of_our_identity():
    """``commits.from_identity`` is the reference-shaped reader we use on the PEER's
    greeting; pointing it at ours proves a compatible peer records the right SHA per role."""
    ident = identity_for("amireman", github_commit=THIEF_SHA, role_commits=ROLES)
    for role, expected in (("police", POLICE_SHA), ("thief", THIEF_SHA)):
        scoped, _ = rolecommit.view(ident, role, THIEF_SHA)
        assert commits.from_identity(scoped) == expected


def test_group_block_carries_both_role_shas_for_a_reader_of_the_report():
    ident = identity_for("amireman", github_commit=THIEF_SHA, role_commits=ROLES)
    assert group_block(ident)["github_commits"] == ROLES
    assert group_block(identity_for("peer", github_commit=""))["github_commits"] == {}


# ---- the report ------------------------------------------------------------------------


def test_result_rows_stamp_the_sha_of_the_role_that_played():
    doc = build_result("G", "U", "amireman", "opp", _summaries(True), {"amireman": THIEF_SHA})
    by_n = {r["sub_game_number"]: r["github_commit"]["amireman"] for r in doc["sub_games"]}
    assert [by_n[n] for n in (1, 3, 5)] == [THIEF_SHA] * 3
    assert [by_n[n] for n in (2, 4, 6)] == [POLICE_SHA] * 3


def test_series_wide_commit_is_still_the_fallback_when_no_role_sha_was_stamped():
    doc = build_result("G", "U", "amireman", "opp", _summaries(False), {"amireman": THIEF_SHA})
    assert {r["github_commit"]["amireman"] for r in doc["sub_games"]} == {THIEF_SHA}


# ---- the invariant that matters most ---------------------------------------------------


def test_per_role_shas_cannot_move_the_consensus_digest():
    """Commits are excluded from CANON_SUB_KEYS, so both profiles must hash identically."""
    with_roles = canonical_rows(_summaries(True), "amireman", "opp")
    without = canonical_rows(_summaries(False), "amireman", "opp")
    assert with_roles == without
    for profile in ("legacy", OFFICIAL_REFERENCE_V1):
        assert consensus_sha("G", "U", with_roles, profile) == consensus_sha(
            "G", "U", without, profile
        )
