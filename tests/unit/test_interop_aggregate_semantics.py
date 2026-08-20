"""Aggregate-report semantics the peer relies on for mutual verification (book §5.4):
  * mutual_agreement.sha256 is a CANONICAL fingerprint over ONLY the mutually-agreed facts
    (game_uid + per-sub-game number/result/winner/roles/score/steps) — never tokens /
    github_commit / timestamps — so BOTH independently-generated reports hash byte-identical
    input and land on the SAME sha256;
  * mutual_agreement.confirmed is reachable but NEVER forced: it is true iff every sub-game's
    PEER log verified untampered (our post-mortem mutual audit), false the moment one fails;
  * ``steps`` is each side's OWN step_number (Kit ``peer/summary.py``), so a survival
    sub-game reads 35 in the surviving thief's report and 34 in the cop's — and that
    asymmetry is correct, because ``steps`` is per-side metadata outside the digest.
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


def test_fingerprint_ignores_steps_and_local_only_fields():
    # steps / tie / tokens / github_commit / timestamps are NOT in the AGREED preimage, so they
    # must never change the digest; a real shared fact (game_id/game_uid) DOES change it.
    base = [
        {
            "sub_game_number": 1,
            "result": "survival",
            "roles": {"amireman": "police", "uoh-ay26": "thief"},
            "score": {"amireman": 0, "uoh-ay26": 3},
            "winner_group": "uoh-ay26",
        }
    ]
    fp = _canonical_fingerprint("G002", "uid-123", base)
    noisy = copy.deepcopy(base)
    noisy[0].update(
        steps=35,
        tie=False,
        tokens_total=99,
        github_commit="deadbeef",
        started_at="2026-01-01T00:00:00",
        extra=1,
    )
    assert _canonical_fingerprint("G002", "uid-123", noisy) == fp  # steps + local-only excluded
    assert _canonical_fingerprint("G002", "uid-999", base) != fp  # game_uid change matters
    assert _canonical_fingerprint("G003", "uid-123", base) != fp  # game_id change matters


def test_each_side_reports_its_own_step_count_on_a_survival(tmp_path):
    """Kit semantics (reference ``peer/summary.py``: ``steps = rt.state.step_number``): each
    peer reports the actions IT sealed. A thief that reaches the threshold reports 35; the
    cop it outlasted answered 34 of those turns and reports 34. Reporting the threshold for
    both roles (as we did until this test was rewritten) overstates the cop's own play by one
    and contradicts the reference — and it was never needed for agreement, since ``steps`` is
    excluded from the consensus preimage (see the fingerprint test above)."""
    ours, theirs, terms = _play()  # amireman=police on odd sub-games, uoh-ay26=thief
    thr = terms["max_steps"]
    _pa, ra = emit_artifacts(tmp_path / "a", ours, terms)
    _pb, rb = emit_artifacts(tmp_path / "b", theirs, terms)
    saw_survival = False
    for sa, sb in zip(ra["sub_games"], rb["sub_games"], strict=True):
        if sa["result"] == "survival":
            saw_survival = True
            thief_side, cop_side = (sb, sa) if sa["roles"]["amireman"] == "police" else (sa, sb)
            assert thief_side["steps"] == thr  # the survivor reached the signed threshold
            assert cop_side["steps"] == thr - 1  # its own answers, one fewer, never invented
    assert saw_survival  # the scenario actually contains survivals
    # The asymmetry stays out of the settlement: both sides still sign the same digest.
    assert ra["mutual_agreement"]["sha256"] == rb["mutual_agreement"]["sha256"]
