"""Aggregate-report semantics the peer relies on for mutual verification:
  * mutual_agreement.confirmed is NEVER forced true unilaterally (book §5.4: mutual
    agreement is a joint property established by BOTH peers, not one side's clean audit);
  * a survival sub-game's recorded steps equal the survival threshold (max_steps) for BOTH
    roles, so the two independently-generated reports agree on the game length (35, not 34).
No strategy/scoring change — these are report/serialization values only.
"""

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integration"))
from interop_loopback import Boxes, Loopback  # noqa: E402

from thief_agent.interop.friendly import emit_artifacts  # noqa: E402
from thief_agent.interop.series import run_series  # noqa: E402
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


def test_confirmed_never_forced_true_unilaterally(tmp_path):
    ours, _theirs, terms = _play()
    _paths, res = emit_artifacts(tmp_path / "a", ours, terms)
    ma = res["mutual_agreement"]
    assert ma["confirmed"] is False  # a clean self-audit must NOT assert mutual agreement
    assert isinstance(ma["sha256"], str) and len(ma["sha256"]) == 64  # fingerprint still published


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
