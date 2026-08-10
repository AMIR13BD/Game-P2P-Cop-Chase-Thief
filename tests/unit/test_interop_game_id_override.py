"""game_id agreement (book Table 20): the four artifacts' filenames derive from a game_id
that BOTH teams must share. The book prescribes no game_id FORMAT (so a peer using 'G002'
is not wrong), and our code derives '<groupA>-vs-<groupB>' locally — which diverges from a
peer that names the series differently. run_series therefore accepts an OPTIONAL game_id
override so both teams can pass the SAME out-of-band-agreed id and their artifacts join.
game_uid stays the derived cryptographic identifier and is never overridden.
"""

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "integration"))
from interop_loopback import Boxes, Loopback  # noqa: E402

from thief_agent.interop.friendly import emit_artifacts  # noqa: E402
from thief_agent.interop.series import run_series  # noqa: E402
from thief_agent.interop.terms import default_terms  # noqa: E402


def _play(game_id=None):
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


def test_default_game_id_is_derived_and_shared():
    ours, theirs, _ = _play()
    assert ours.game_id == "amireman-vs-uoh-ay26"  # sorted-pair derivation
    assert ours.game_id == theirs.game_id  # both sides derive the SAME id with no override
    assert ours.game_uid == theirs.game_uid  # derived crypto id matches too


def test_agreed_game_id_override_drives_both_sides_and_filenames(tmp_path):
    ours, theirs, terms = _play(game_id="G002")
    assert ours.game_id == theirs.game_id == "G002"
    assert ours.game_uid == theirs.game_uid  # game_uid is still the derived id, NOT overridden
    assert ours.game_uid != "G002"

    pa, ra = emit_artifacts(tmp_path / "a", ours, terms)
    pb, rb = emit_artifacts(tmp_path / "b", theirs, terms)
    names_a = sorted(p.name for p in pa)
    names_b = sorted(p.name for p in pb)
    assert names_a == names_b  # identical filename set on both sides
    assert "result_G002.json" in names_a
    assert "declaration_G002.json" in names_a
    assert any(n == "log_G002_g01.json" for n in names_a)
    # the agreed id also lands inside the documents, and the fingerprint still matches
    assert ra["game_id"] == rb["game_id"] == "G002"
    assert ra["game_uid"] == rb["game_uid"]
    assert ra["mutual_agreement"]["sha256"] == rb["mutual_agreement"]["sha256"]
    assert ra["mutual_agreement"]["confirmed"] is True
    assert rb["mutual_agreement"]["confirmed"] is True
