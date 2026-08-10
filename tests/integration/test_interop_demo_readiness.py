"""One local two-peer SIX-sub-game series over the exact friendly transport (Loopback),
asserting the whole demo-readiness contract in a single run so a real rerun is predictable:

  * both sides derive the SAME game_id and game_uid, and emit an identical filename set;
  * both independently-generated reports carry the SAME canonical fingerprint AND
    confirmed=true (each cleanly verified the other's revealed log — book §5.4);
  * every sealed move token across BOTH sides' logs is a legal move_set value
    (N/S/E/W/STAY or the normalizable MOVE:<dir>) — never an illegal 'BARRIER:*' or 'HOLD:-';
  * on a capture sub-game the caught thief tells the TRUTH (its final record's committed
    position equals the cop's landing cell) and makes NO physical move after capture
    (the concession seals STAY at the unchanged cell).

Pure report/log assertions — no strategy, scoring, email, or network involved.
"""

import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from interop_loopback import Boxes, Loopback  # noqa: E402

from thief_agent.interop import DEFAULT_GROUP_ID  # noqa: E402
from thief_agent.interop.engine import SubEngine  # noqa: E402
from thief_agent.interop.friendly import emit_artifacts  # noqa: E402
from thief_agent.interop.series import run_series  # noqa: E402
from thief_agent.interop.terms import default_terms  # noqa: E402
from thief_agent.interop.wire import TurnMessage  # noqa: E402


def _legal_move(m: str) -> bool:
    return m == "STAY" or (m.startswith("MOVE:") and m.split(":", 1)[1] in {"N", "S", "E", "W"})


def _self_pos(rec: dict):
    # payload.state == "grid=7;self=[r,c]"
    state = rec["payload"].get("state", "")
    tail = state.split("self=", 1)[1] if "self=" in state else "[]"
    return json.loads(tail)


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


def test_two_peer_six_game_demo_contract(tmp_path):
    ours, theirs, terms = _play()

    # -- identity: same shared game_id / game_uid, six sub-games each --
    assert ours.game_id == theirs.game_id
    assert ours.game_uid == theirs.game_uid
    assert len(ours.summaries) == len(theirs.summaries) == 6

    pa, ra = emit_artifacts(tmp_path / "a", ours, terms)
    pb, rb = emit_artifacts(tmp_path / "b", theirs, terms)

    # -- filenames: identical set on both sides --
    assert sorted(p.name for p in pa) == sorted(p.name for p in pb)

    # -- mutual agreement: SAME canonical fingerprint AND both confirmed=true --
    assert ra["mutual_agreement"]["sha256"] == rb["mutual_agreement"]["sha256"]
    assert ra["mutual_agreement"]["confirmed"] is True
    assert rb["mutual_agreement"]["confirmed"] is True

    # -- token legality across BOTH sides' full logs: no BARRIER:* / no HOLD:- --
    blob = ""
    for series in (ours, theirs):
        for s in series.summaries:
            for rec in s["records"]:
                move = rec["payload"].get("move")
                if move is None:  # step-0 system_spec record has no move field
                    continue
                assert _legal_move(move), (s["sub_game_number"], move)
            blob += json.dumps(s["records"])
    assert "BARRIER:" not in blob
    assert "HOLD" not in blob


def test_capture_leg_is_truthful_with_no_post_capture_move():
    """The default template scenario is all-survival, so the capture contract is proven with a
    deterministic two-peer capture leg: the cop lands on the thief's committed cell and claims,
    the thief answers TRUTHFULLY (caught=true at that cell) and makes NO physical move, and
    BOTH sides' mutual audit of the other's revealed log verifies clean."""
    from thief_agent.domain.crypto import audit_records

    terms = default_terms(max_steps=10)
    thief = SubEngine("thief", terms, "uoh-ay26", "0" * 40, 1)
    cop = SubEngine("police", terms, DEFAULT_GROUP_ID, "0" * 40, 1)

    thief.take_turn()  # thief seals its position first
    caught_pos = list(thief.half.pos)
    pos_before = _self_pos(thief.half.records[-1])

    # cop lands on the thief's cell and claims it -> thief is caught
    claim = TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=caught_pos)
    assert thief.receive(claim).i_am_caught
    concession = thief.concede()

    # TRUTHFUL: the concession answers caught=true at the cop's exact landing cell
    assert concession.claim_response == {"claim": caught_pos, "caught": True}
    # NO post-capture physical move: final sealed record is STAY at the unchanged cell
    last = thief.half.records[-1]
    assert last["payload"]["move"] == "STAY"
    assert _self_pos(last) == pos_before == caught_pos

    # the cop turns that honest concession into its capture win
    assert cop.receive(concession).i_won

    # mutual audit: each side re-hashes the OTHER's revealed records and they verify clean
    assert not audit_records(thief.half.records)["failed_steps"]
    assert not audit_records(cop.half.records)["failed_steps"]
