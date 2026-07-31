"""P17 free-language hints: word-limit, prohibited-info filtering, malformed/empty
handling, truthful vs deceptive generation, audited credibility, hint effect on
strategy, and refusal to act on unverified claims."""

from thief_agent.domain.board import Board
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.hint_filter import (
    credibility_from_records,
    is_valid,
    leaks_information,
    sanitize,
    word_count,
)
from thief_agent.strategy.hints import HintGenerator, biased_target
from thief_agent.strategy.police_greedy import PoliceGreedyBrain
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_distance import ThiefDistanceBrain


def test_word_limit_enforced():
    long_hint = " ".join(["word"] * 20)
    assert not is_valid(long_hint)
    assert word_count(sanitize(long_hint)) <= 15
    assert is_valid("heading north toward the district")


def test_prohibited_information_filtered():
    for leak in [
        "I am at [3, 4]",
        "go to row 3 column 5",
        "position (2,2) now",
        "position 3 currently",  # single-scalar position
        "x=4 y=5 exactly",  # keyed coordinates
        "hiding in square 9",  # indexed cell
        "nonce is abcd1234ef",
        "the token deadbeefcafe",
        "my secret move",
    ]:
        assert leaks_information(leak)
        assert sanitize(leak) == "moving through the streets"  # fail-closed


def test_any_digit_is_rejected():
    assert leaks_information("meet at 12")  # bare integer could encode a position
    assert not leaks_information("meet near the old bakery")


def test_malformed_and_empty_hints():
    assert not is_valid("")
    assert not is_valid("   ")
    assert not is_valid(None)
    assert sanitize(None) == "moving through the streets"
    assert sanitize("") == "moving through the streets"


def test_truthful_vs_deceptive_generation():
    truth = HintGenerator(make_rng(1), mode="truthful").generate(toward="N")
    lie = HintGenerator(make_rng(1), mode="deceptive").generate(toward="N")
    assert "north" in truth and "south" in lie  # deception inverts the direction
    assert is_valid(truth) and is_valid(lie)


def test_vague_mode_is_seed_reproducible_and_safe():
    a = HintGenerator(make_rng(3), mode="vague").generate()
    b = HintGenerator(make_rng(3), mode="vague").generate()
    assert a == b and is_valid(a) and not leaks_information(a)


def _records():
    cfg = validate(DEFAULT_GAME_CONFIG)
    return run_sub_game(
        PoliceGreedyBrain(make_rng(1)),
        ThiefDistanceBrain(make_rng(2)),
        {**cfg, "sub_game_number": 1},
        "opp",
        DevTestSigner(),
        "0" * 40,
    )["records"]


def test_credibility_only_from_audited_evidence():
    recs = _records()
    checked, score = credibility_from_records(recs, DevTestSigner())
    assert checked > 0 and 0.0 <= score <= 1.0
    tampered = [dict(r) for r in recs]
    tampered[-1] = {**tampered[-1], "commit": "00"}
    assert credibility_from_records(tampered, DevTestSigner()) == (0, 0.5)  # rejected


def test_hint_affects_strategy_only_when_credible():
    board = Board(7)
    scent = {(3, 3): 0.9}
    base = biased_target(board, scent, "heading south toward the district", 0.5)
    shifted = biased_target(board, scent, "heading south toward the district", 0.9)
    assert base == (3, 3)  # neutral credibility -> hint ignored (no unverified trust)
    assert shifted == (4, 3)  # proven-credible hint moves the pursuit target


def test_no_bias_from_nondirectional_or_missing_hint():
    board = Board(7)
    scent = {(3, 3): 0.9}
    assert biased_target(board, scent, "weaving through the streets", 0.9) == (3, 3)
    assert biased_target(board, scent, None, 0.9) == (3, 3)
