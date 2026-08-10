"""mutual_agreement.confirmed requires ALL of: clean peer logs, per-sub-game RESULT
agreement (local_result_claim == peer_result_claim), AND an actually-received peer
consensus digest that matches ours. A locally-computed SHA is never sufficient. Covers
regression scenarios 4, 5, 6, 7 (unit) plus a real two-peer digest exchange (loopback).
"""

import sys
import threading
from pathlib import Path

from thief_agent.interop.artifacts import build_result
from thief_agent.interop.consensus import canonical_rows, consensus_sha
from thief_agent.interop.submission import enrich_result

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integration"))
from interop_loopback import Boxes, Loopback  # noqa: E402

from thief_agent.interop.friendly import emit_artifacts  # noqa: E402
from thief_agent.interop.series import run_series  # noqa: E402
from thief_agent.interop.terms import default_terms  # noqa: E402

IDENT = {"group_id": "amireman", "repos": {"cop": "u", "thief": "v"}, "github_commit": "a" * 40}


def _summaries(result_agreed: bool, log_verified: bool = True):
    peer = "survival" if result_agreed else "capture"
    return [
        {
            "sub_game_number": i + 1,
            "result": "survival",
            "role": "thief" if i % 2 == 0 else "police",
            "audit": {
                "log_verified": log_verified,
                "tampered": not log_verified,
                "local_result_claim": "survival",
                "peer_result_claim": peer,
                "result_agreed": result_agreed,
            },
            "started_at": "2026-01-01T00:00:00+00:00",
            "duration_seconds": 1,
            "steps": 35,
        }
        for i in range(6)
    ]


def _enriched(result_agreed, consensus, log_verified=True):
    s = _summaries(result_agreed, log_verified)
    doc = build_result("G", "U", "amireman", "opp", s, {"amireman": "a" * 40, "opp": "b" * 40})
    return enrich_result(doc, s, IDENT, {"group_id": "opp"}, consensus)["mutual_agreement"]


_MATCH = {"sha256": "aa", "peer_sha256": "aa", "sha_match": True}


def test_result_disagreement_blocks_confirmation():
    """Scenario 4: local survival vs peer capture -> result_agreed=false -> confirmed=false."""
    ma = _enriched(result_agreed=False, consensus=_MATCH)
    assert ma["results_agreed"] is False
    assert ma["confirmed"] is False


def test_same_results_but_different_sha_blocks_confirmation():
    """Scenario 5: results agree, logs clean, but the exchanged digests differ -> not confirmed."""
    ma = _enriched(True, {"sha256": "aa", "peer_sha256": "bb", "sha_match": False})
    assert ma["sha_match"] is False
    assert ma["confirmed"] is False


def test_all_conditions_met_confirms():
    """Scenario 6: clean logs + results agree + a matching exchanged peer digest -> confirmed."""
    ma = _enriched(True, _MATCH)
    assert ma["results_agreed"] is True and ma["sha_match"] is True
    assert ma["confirmed"] is True


def test_missing_peer_sha_blocks_confirmation():
    """Scenario 7: no peer digest received (None) -> sha_match false -> confirmed false."""
    ma = _enriched(True, {"sha256": "aa", "peer_sha256": None, "sha_match": False})
    assert ma["peer_sha256"] is None
    assert ma["confirmed"] is False


def test_local_sha_alone_never_confirms():
    """A locally computed SHA with NO peer exchange must not confirm (defends the core rule)."""
    ma = _enriched(True, {"sha256": "aa", "peer_sha256": None, "sha_match": False})
    assert ma["sha256"] == "aa"  # we still publish ours
    assert ma["confirmed"] is False  # but never confirm without a real peer match


def _play(game_id="G002"):
    terms = default_terms()
    out: dict = {}

    def side(role, grp, own, peer):
        out[grp] = run_series(
            terms,
            role,
            Loopback(own, peer, False),
            grp,
            "0" * 40,
            num_games=6,
            turn_timeout=8.0,
            game_id=game_id,
        )

    a, b = Boxes(), Boxes()
    t1 = threading.Thread(target=side, args=("police", "amireman", a, b))
    t2 = threading.Thread(target=side, args=("thief", "uoh-ay26", b, a))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return out["amireman"], out["uoh-ay26"], terms


def test_real_two_peer_digest_exchange_matches_and_confirms(tmp_path):
    """Both peers genuinely EXCHANGE digests over the final-audit channel: each receives the
    other's SHA, they match, and both reports independently reach confirmed=true."""
    ours, theirs, terms = _play()
    # the exchange actually happened: each side received the OTHER's digest, not just its own
    assert ours.peer_consensus_sha is not None and theirs.peer_consensus_sha is not None
    assert ours.sha_match is True and theirs.sha_match is True
    assert ours.consensus_sha == theirs.consensus_sha == ours.peer_consensus_sha
    # and it equals an independent recomputation from the summaries
    rows = canonical_rows(ours.summaries, "amireman", "uoh-ay26")
    assert ours.consensus_sha == consensus_sha(ours.game_id, ours.game_uid, rows)
    _pa, ra = emit_artifacts(tmp_path / "a", ours, terms)
    _pb, rb = emit_artifacts(tmp_path / "b", theirs, terms)
    assert ra["mutual_agreement"]["confirmed"] is True
    assert rb["mutual_agreement"]["confirmed"] is True
    assert ra["mutual_agreement"]["sha_match"] is True
