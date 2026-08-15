"""Reporting-only regression: per-sub-game peer runtime SHA persistence + robust fallback.
Proves the canonical consensus is UNCHANGED (github_commit is excluded from the preimage)."""

from thief_agent.interop.artifacts import build_result
from thief_agent.interop.consensus import consensus_sha
from thief_agent.interop.series import _peer_commit

A = "3d2e95582d2e8bbf00d213cfae546a2ad180e021"  # sharNamr Police runtime (g1/3/5)
B = "0c924cd5379adbb3d8414b9ce138b3fdbb4e81cf"  # sharNamr Thief runtime (g2/4/6)
OURS, THEIRS = "amireman", "sharNamr"


def _summary(n, role, peer_sha):
    return {
        "sub_game_number": n,
        "role": role,
        "result": "survival",
        "winner": "thief",
        "steps": 35,
        "records": [],
        "audit": {
            "log_verified": True,
            "tampered": False,
            "local_result_claim": "survival",
            "peer_result_claim": "survival",
            "result_agreed": True,
        },
        "started_at": "",
        "duration_seconds": 0.0,
        "tokens_total": 0,
        "peer_github_commit": peer_sha,
    }


def test_peer_commit_fallback():
    assert _peer_commit({"github_commit": A}) == A  # prefer github_commit
    assert (
        _peer_commit({"github_commit": "", "git_commit_hash": B}) == B
    )  # E: empty -> git_commit_hash
    assert _peer_commit({"github_commit": A, "git_commit_hash": B}) == A  # F: both -> github_commit
    assert _peer_commit({}) == ""  # G: missing -> ""
    assert _peer_commit({"github_commit": "not-a-sha"}) == ""  # non 40-hex rejected
    assert _peer_commit(None) == ""


def test_result_persists_alternating_peer_sha_per_subgame():
    roles = ["thief", "police", "thief", "police", "thief", "police"]  # amireman starts thief
    peer = [A, B, A, B, A, B]  # sharNamr: police=A on g1/3/5, thief=B on g2/4/6
    summaries = [_summary(n, roles[n - 1], peer[n - 1]) for n in range(1, 7)]
    res = build_result("G006", "uid", OURS, THEIRS, summaries, {OURS: "ourSHA", THEIRS: "LAST"})
    got = [row["github_commit"][THEIRS] for row in res["sub_games"]]
    assert got == [A, B, A, B, A, B], got  # A/B/A/B/A/B, NOT one last value repeated
    assert all(row["github_commit"][OURS] == "ourSHA" for row in res["sub_games"])


def test_missing_peer_sha_stays_empty_and_falls_back_to_commits():
    summaries = [_summary(1, "thief", "")]  # G: no per-subgame sha
    res = build_result("G006", "uid", OURS, THEIRS, summaries, {OURS: "o", THEIRS: "FALLBACK"})
    assert (
        res["sub_games"][0]["github_commit"][THEIRS] == "FALLBACK"
    )  # falls back to commits[theirs]
    summaries2 = [_summary(1, "thief", "")]
    res2 = build_result("G006", "uid", OURS, THEIRS, summaries2, {OURS: "o"})  # no theirs commit
    assert res2["sub_games"][0]["github_commit"][THEIRS] == ""  # safely empty


def test_consensus_sha_unchanged_by_per_subgame_github_commit():
    """github_commit is NOT in the canonical preimage: the SHA must be identical whether
    peer SHAs differ per row or not, and whatever their values."""
    roles = ["thief", "police", "thief", "police", "thief", "police"]
    s_ab = [_summary(n, roles[n - 1], (A if n % 2 else B)) for n in range(1, 7)]
    s_empty = [_summary(n, roles[n - 1], "") for n in range(1, 7)]
    r_ab = build_result("G006", "uid", OURS, THEIRS, s_ab, {OURS: "o", THEIRS: "x"})
    r_empty = build_result("G006", "uid", OURS, THEIRS, s_empty, {OURS: "o", THEIRS: "y"})
    sha_ab = consensus_sha("G006", "uid", r_ab["sub_games"])
    sha_empty = consensus_sha("G006", "uid", r_empty["sub_games"])
    assert sha_ab == sha_empty, "consensus SHA must not depend on per-row github_commit"
    # and roles token is still 'police'/'thief' (never 'cop') in the report+consensus field
    assert set(r_ab["sub_games"][0]["roles"].values()) <= {"police", "thief"}
