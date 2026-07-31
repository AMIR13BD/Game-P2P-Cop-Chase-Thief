"""P15 profiling: features come only from audited records; tampered/unaudited
evidence is rejected; profiles reset between opponents; no hidden state is used."""

from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.police_greedy import PoliceGreedyBrain
from thief_agent.strategy.profiling import OpponentProfile, ProfileStore, _parse_turn
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_distance import ThiefDistanceBrain


def _sub_game():
    cfg = validate(DEFAULT_GAME_CONFIG)
    return run_sub_game(
        PoliceGreedyBrain(make_rng(1)),
        ThiefDistanceBrain(make_rng(2)),
        {**cfg, "sub_game_number": 1},
        "opp",
        DevTestSigner(),
        "0" * 40,
    )


def test_profile_from_audited_records():
    res = _sub_game()
    prof = OpponentProfile("opp-A")
    assert prof.observe_subgame(res["records"], DevTestSigner(), res["outcome"]) is True
    f = prof.features()
    assert f["turns"] > 0
    assert 0.0 <= f["hint_honesty"] <= 1.0
    assert 0.0 <= f["predictability"] <= 1.0
    assert set(f["move_preferences"]) <= {"N", "S", "E", "W", "STAY", "BARRIER"}


def test_tampered_records_are_rejected():
    res = _sub_game()
    prof = OpponentProfile("opp-B")
    bad = [dict(r) for r in res["records"]]
    bad[-1] = {**bad[-1], "commit": "deadbeef"}  # break one commitment
    assert prof.observe_subgame(bad, DevTestSigner(), res["outcome"]) is False
    assert prof.turns == 0 and prof.sub_games == 0  # nothing entered the profile


def test_profile_reset_between_opponents():
    res = _sub_game()
    store = ProfileStore()
    store.get("opp-X").observe_subgame(res["records"], DevTestSigner())
    assert store.get("opp-X").turns > 0
    store.reset("opp-X")
    assert store.get("opp-X").turns == 0  # fresh profile, no carry-over


def test_parser_uses_only_revealed_payload_fields():
    res = _sub_game()
    turn = next(r for r in res["records"] if r["payload"].get("step", 0) > 0)
    role, cell, kind, direction, intent, grid = _parse_turn(turn)
    assert role in ("police", "thief")
    assert cell is not None and grid == validate(DEFAULT_GAME_CONFIG)["grid_size"]
    assert kind in ("MOVE", "STAY", "BARRIER")


def test_no_observation_type_accepted():
    # The profile API only accepts record lists; feeding a non-record fails audit.
    prof = OpponentProfile("opp-Z")
    assert prof.observe_subgame([{"not": "a record"}], DevTestSigner()) is False
    assert prof.turns == 0
