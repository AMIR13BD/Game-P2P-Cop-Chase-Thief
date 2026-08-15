"""Where the peer's per-sub-game runtime SHA may come from, and where it may NOT.

Book ch.5.5 box + App. E rule 53: each side declares the 40-hex commit it played, and ch.9
requires that id per sub-game in the emailed result. A peer may put it in its identity block,
beside the identity in the greeting, or (always) in the signed Step-0 record it reveals in that
sub-game's audit. Nothing else may become a SHA, and role swaps must never move a SHA between
the two groups."""

from official_result_fixture import OURS, THEIRS

from thief_agent.interop import commits
from thief_agent.interop.artifacts import build_result
from thief_agent.interop.series import _peer_commit

IDENT_SHA = "4444444444444444444444444444444444444444"
GREET_SHA = "5555555555555555555555555555555555555555"
STEP0_SHA = "6666666666666666666666666666666666666666"


def _step0(sha, step=0):
    return [{"payload": {"step": step, "type": "system_spec", "github_commit": sha}}]


def test_identity_is_preferred_and_alias_accepted():
    assert _peer_commit({"github_commit": IDENT_SHA}) == IDENT_SHA
    assert _peer_commit({"git_commit_hash": IDENT_SHA}) == IDENT_SHA
    assert _peer_commit({"commit_hash": IDENT_SHA}) == IDENT_SHA
    assert _peer_commit({"github_commit": IDENT_SHA, "git_commit_hash": GREET_SHA}) == IDENT_SHA


def test_greeting_top_level_is_read_when_identity_has_none():
    """A peer that declares its commit BESIDE the identity (not inside it) is still recorded."""
    assert _peer_commit({}, {"group_id": THEIRS, "github_commit": GREET_SHA}) == GREET_SHA
    assert _peer_commit({"github_commit": IDENT_SHA}, {"github_commit": GREET_SHA}) == IDENT_SHA


def test_step0_reveal_is_the_last_resort():
    assert commits.from_records(_step0(STEP0_SHA)) == STEP0_SHA
    assert commits.from_records(_step0(STEP0_SHA, step=3)) == STEP0_SHA  # tagged system_spec
    assert commits.from_records([{"payload": {"step": 1, "hint": "hi"}}]) == ""
    assert commits.from_records([]) == "" and commits.from_records(None) == ""


def test_nothing_but_a_40_hex_value_is_ever_reported():
    assert _peer_commit({"github_commit": "unknown"}) == ""
    assert _peer_commit({"github_commit": "  "}) == ""
    assert _peer_commit({"github_commit": "z" * 40}) == ""  # not hex
    assert _peer_commit({"github_commit": "a" * 39}) == "" and _peer_commit({}) == ""
    assert _peer_commit(None, None) == ""
    # a 64-hex commit-reveal digest is NOT a runtime SHA and must never be mistaken for one
    assert commits.from_identity({"github_commit": "b" * 64}) == ""


def test_role_swap_keeps_each_sha_with_its_own_group():
    """g1/3/5 the peer is Police, g2/4/6 it is Thief: each row keeps that sub-game's peer SHA,
    and our own SHA never lands in the peer's slot."""
    police_sha, thief_sha = IDENT_SHA, GREET_SHA
    rows = []
    for n in range(1, 7):
        rows.append(
            {
                "sub_game_number": n,
                "role": "thief" if n % 2 else "police",
                "result": "survival", "winner": "thief", "steps": 35, "records": [],
                "audit": {"log_verified": True, "tampered": False, "local_result_claim": "s",
                          "peer_result_claim": "s", "result_agreed": True},
                "started_at": "", "duration_seconds": 0.0, "tokens_total": 0,
                "peer_github_commit": police_sha if n % 2 else thief_sha,
            }
        )
    doc = build_result("G013", "uid", OURS, THEIRS, rows, {OURS: "7" * 40})
    got = [r["github_commit"] for r in doc["sub_games"]]
    assert [g[THEIRS] for g in got] == [police_sha, thief_sha] * 3
    assert {g[OURS] for g in got} == {"7" * 40}  # our SHA is never overwritten by a swap
