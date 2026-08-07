"""In-process integration for the interop adapter: a full six-sub-game series over a
loopback transport (no sockets), reliability under duplicate turn delivery, artifact
join, and the friendly-mode email hard-block. Both sides run our production runtime."""

import inspect
import tempfile
import threading
from pathlib import Path

import pytest
from interop_loopback import Boxes, Loopback

from thief_agent.interop.friendly import emit_artifacts
from thief_agent.interop.series import run_series
from thief_agent.interop.terms import default_terms


def _play(dup: bool = False):
    a, b = Boxes(), Boxes()
    terms = default_terms()
    out: dict = {}

    def side(role, group, own, peer):
        out[group] = run_series(
            terms, role, Loopback(own, peer, dup), group, "local", num_games=6, turn_timeout=8.0
        )

    t1 = threading.Thread(target=side, args=("police", "amireman", a, b))
    t2 = threading.Thread(target=side, args=("thief", "sparring-local", b, a))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return out["amireman"], out["sparring-local"], terms


def test_full_six_game_series_matches_ids_roles_and_clean_audit():
    ours, theirs, _ = _play()
    assert ours.game_id == theirs.game_id and ours.game_uid == theirs.game_uid
    assert len(ours.summaries) == 6 and len(theirs.summaries) == 6
    for sa, sb in zip(ours.summaries, theirs.summaries, strict=True):
        assert sa["result"] == sb["result"]  # both settle identically
        assert sa["role"] != sb["role"]  # complementary roles
        assert sa["audit"]["log_verified"] and sb["audit"]["log_verified"]
        assert not sa["audit"]["tampered"] and not sb["audit"]["tampered"]
    assert [s["role"] for s in ours.summaries] == ["police", "thief"] * 3


def test_series_survives_duplicate_turn_delivery():
    ours, _, _ = _play(dup=True)
    assert len(ours.summaries) == 6
    assert all(s["audit"]["log_verified"] for s in ours.summaries)


def test_artifacts_join_on_ids_and_totals():
    ours, theirs, terms = _play()
    with tempfile.TemporaryDirectory() as td:
        _, our_result = emit_artifacts(Path(td) / "a", ours, terms)
        _, their_result = emit_artifacts(Path(td) / "b", theirs, terms)
    assert our_result["game_uid"] == their_result["game_uid"]
    fr_a, fr_b = our_result["final_result"], their_result["final_result"]
    assert fr_a["total_score"] == fr_b["total_score"]
    assert fr_a["winner_group"] == fr_b["winner_group"]
    for ra, rb in zip(our_result["sub_games"], their_result["sub_games"], strict=True):
        assert ra["score"] == rb["score"]


@pytest.mark.parametrize("outcome", ["clean", "tampered"])
def test_friendly_never_calls_gmail_sender(monkeypatch, outcome, tmp_path):
    """Even a fully successful (or tampered) friendly series cannot reach the mail sender."""
    import thief_agent.infra.gmail_report as gmail

    called = {"n": 0}
    monkeypatch.setattr(
        gmail, "send_report", lambda *a, **k: called.__setitem__("n", called["n"] + 1)
    )
    ours, _, terms = _play()
    if outcome == "tampered":
        ours.summaries[0]["records"][1]["commit"] = "0" * 64
    _, result_doc = emit_artifacts(tmp_path / "f", ours, terms)
    assert called["n"] == 0  # sender never invoked
    assert "counted-two-peer" not in str(result_doc)  # never marked counted
    assert result_doc["report_type"] == "final_game_result"


def test_friendly_module_imports_no_gmail():
    """Structural guarantee: the friendly module IMPORTS no mail code path."""
    import thief_agent.interop.friendly as fr

    import_lines = [
        ln
        for ln in inspect.getsource(fr).splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    joined = "\n".join(import_lines)
    for forbidden in ("gmail", "email_sender", "report.emit", "commands_report", "smtplib"):
        assert forbidden not in joined
    assert fr.LECTURER_REPORT_SENT is False and fr.MATCH_MODE == "friendly"
