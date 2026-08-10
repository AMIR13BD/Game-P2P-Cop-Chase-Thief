"""Aggregate-report semantics the peer relies on for mutual verification (book §5.4):
  * mutual_agreement.sha256 is a CANONICAL fingerprint over ONLY the mutually-agreed facts
    (game_uid + per-sub-game number/result/winner/roles/score/steps) — never tokens /
    github_commit / timestamps — so BOTH independently-generated reports hash byte-identical
    input and land on the SAME sha256;
  * mutual_agreement.confirmed is reachable but NEVER forced: it is true iff every sub-game's
    PEER log verified untampered (our post-mortem mutual audit), false the moment one fails;
  * a survival sub-game's recorded steps equal the survival threshold (max_steps) for BOTH
    roles, so the two reports agree on the game length (35, not the cop's 34).
No strategy/scoring change — these are report/serialization values only.
"""

import copy
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integration"))
from interop_loopback import Boxes, Loopback  # noqa: E402

from thief_agent.interop.friendly import emit_artifacts  # noqa: E402
from thief_agent.interop.series import run_series  # noqa: E402
from thief_agent.interop.submission import (  # noqa: E402
    _canonical_fingerprint,
    _mutual_clean,
)
from thief_agent.interop.terms import default_terms  # noqa: E402


def _play():
    terms = default_terms()
    out: dict = {}

    def side(role, grp, own, peer):
        out[grp] = run_series(
            terms, role, Loopback(own, peer, False), grp, "0" * 40, num_games=6, turn_timeout=8.0
        )

    a, b = Boxes(), Boxes()
    t1 = threading.Thread(target=side, args=("police", "amireman", a, b))
    t2 = threading.Thread(target=side, args=("thief", "uoh-ay26", b, a))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return out["amireman"], out["uoh-ay26"], terms


def test_confirmed_true_and_same_fingerprint_when_both_verify_clean(tmp_path):
    ours, theirs, terms = _play()
    _pa, ra = emit_artifacts(tmp_path / "a", ours, terms)
    _pb, rb = emit_artifacts(tmp_path / "b", theirs, terms)
    # both peers cleanly verified each other -> BOTH reports independently reach confirmed=true
    assert ra["mutual_agreement"]["confirmed"] is True
    assert rb["mutual_agreement"]["confirmed"] is True
    # and both land on the SAME canonical fingerprint (the joint sign-off the lecturer compares)
    assert ra["mutual_agreement"]["sha256"] == rb["mutual_agreement"]["sha256"]
    assert len(ra["mutual_agreement"]["sha256"]) == 64


def test_confirmed_false_the_moment_a_peer_log_fails():
    # a single tampered/unverified peer sub-game must drop confirmed to false (never forced true)
    clean = [{"audit": {"log_verified": True, "tampered": False}} for _ in range(6)]
    assert _mutual_clean(clean) is True
    clean[3]["audit"]["tampered"] = True
    assert _mutual_clean(clean) is False
    assert _mutual_clean([]) is False  # no sub-games is not agreement


def test_fingerprint_ignores_local_only_fields():
    # tokens / github_commit / timestamps legitimately differ (or are absent) between peers;
    # the canonical fingerprint must be invariant to them so both sides still match.
    base = [
        {
            "sub_game_number": 1,
            "result": "survival",
            "winner_group": "uoh-ay26",
            "roles": {"amireman": "police", "uoh-ay26": "thief"},
            "score": {"amireman": 0, "uoh-ay26": 3},
            "steps": 35,
        }
    ]
    fp = _canonical_fingerprint("uid-123", base)
    noisy = copy.deepcopy(base)
    noisy[0].update(
        tokens_total=99, github_commit="deadbeef", started_at="2026-01-01T00:00:00", extra=1
    )
    assert _canonical_fingerprint("uid-123", noisy) == fp  # local-only noise excluded
    assert _canonical_fingerprint("uid-999", base) != fp  # a real shared-fact change DOES matter


def test_survival_steps_equal_threshold_for_both_roles(tmp_path):
    ours, theirs, terms = _play()
    thr = terms["max_steps"]
    _pa, ra = emit_artifacts(tmp_path / "a", ours, terms)
    _pb, rb = emit_artifacts(tmp_path / "b", theirs, terms)
    saw_survival = False
    for sa, sb in zip(ra["sub_games"], rb["sub_games"], strict=True):
        if sa["result"] == "survival":
            saw_survival = True
            assert sa["steps"] == thr, sa  # canonical survival length, not the cop's 34
            assert sb["steps"] == thr  # both independently-generated reports agree
            assert sa["steps"] == sb["steps"]
    assert saw_survival  # the scenario actually contains survivals
