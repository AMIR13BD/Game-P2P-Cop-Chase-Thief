"""Hostile inbound turns are refused or sanitized, and never crash the six-game process.

The failure this prevents is cheap for an opponent and expensive for us: before this,
``{"step": None}`` or a single unparseable scent key raised out of the turn loop, past the
two exception types the runtime catches, and ended the whole series. A peer could take the
match without playing it.

Refusal is deliberately NOT an outcome. The lecturer's reference performs no inbound
validation at all, so there is no precedent for turning an opponent's malformed byte into
a scored result, and inventing one would let a peer pick our result by sending garbage.
"""

import pytest

from thief_agent.interop.msgcheck import clean_audit, clean_turn
from thief_agent.shared import wirecheck as wc

SIZE = 7
GOOD = {
    "step": 7,
    "sender": "police",
    "hint": "north of the park",
    "smell_grid": {"3,3": 0.9, "3,4": 0.5},
    "commit": "a" * 64,
    "timestamp": "2026-08-08T19:00:00Z",
    "barrier_placed": [5, 6],
    "capture_claim": None,
    "claim_response": None,
    "win_claim": None,
}


def turn(**overrides) -> dict:
    return {**GOOD, **overrides}


REFUSED = [
    ("missing step", {k: v for k, v in GOOD.items() if k != "step"}),
    ("step None", turn(step=None)),
    ("step negative", turn(step=-1)),
    ("step float", turn(step=1.5)),
    ("step bool", turn(step=True)),
    ("missing commit", {k: v for k, v in GOOD.items() if k != "commit"}),
    ("commit short", turn(commit="abc")),
    ("commit uppercase", turn(commit="A" * 64)),
    ("commit non-string", turn(commit={"a": 1})),
    ("sender empty", turn(sender="")),
    ("sender non-string", turn(sender=42)),
    ("not a dict", ["not", "a", "turn"]),
    ("oversized", turn(hint="x" * (wc.MAX_MESSAGE_BYTES + 10))),
]


@pytest.mark.parametrize(("label", "message"), REFUSED, ids=[r[0] for r in REFUSED])
def test_structurally_unusable_turns_are_refused_without_raising(label, message):
    assert clean_turn(message, SIZE) is None


def test_a_digit_string_step_is_read_rather_than_refused():
    """Unambiguous, and refusing it would reject a peer we can read perfectly well."""
    assert clean_turn(turn(step="1"), SIZE)["step"] == 1


def test_a_missing_hint_becomes_empty_and_an_empty_timestamp_is_tolerated():
    """Some conforming peers send an empty timestamp; refusing it would break the match."""
    cleaned = clean_turn({k: v for k, v in turn(timestamp="").items() if k != "hint"}, SIZE)
    assert cleaned["hint"] == ""
    assert cleaned["timestamp"] == ""


def test_unknown_extension_fields_are_tolerated():
    """The extension seam: a receiver that refuses these cannot be extended."""
    cleaned = clean_turn(turn(unknown_field={"anything": 1}, another="x"), SIZE)
    assert cleaned is not None
    assert "unknown_field" not in cleaned


SPOILED = [
    ("malformed scent key", {"not-a-cell": 0.5}),
    ("scent NaN", {"3,3": float("nan")}),
    ("scent Infinity", {"3,3": float("inf")}),
    ("scent string value", {"3,3": "0.9"}),
    ("scent off board", {"99,99": 0.5}),
    ("scent negative coord", {"-1,3": 0.5}),
    ("scent out of range", {"3,3": 7.5}),
    ("scent key not a string", {7: 0.5}),
]


@pytest.mark.parametrize(("label", "grid"), SPOILED, ids=[s[0] for s in SPOILED])
def test_a_spoiled_scent_cell_is_dropped_and_the_turn_survives(label, grid):
    cleaned = clean_turn(turn(smell_grid=grid), SIZE)
    assert cleaned is not None
    assert cleaned["smell_grid"] == {}


def test_a_flooded_scent_grid_is_capped_at_the_physical_board():
    """Cells beyond the board cannot mean anything, so they never enter our state."""
    flood = {f"{r},{c}": 0.5 for r in range(30) for c in range(30)}
    cleaned = clean_turn(turn(smell_grid=flood), SIZE)
    assert 0 < len(cleaned["smell_grid"]) <= SIZE * SIZE


def test_a_grid_so_large_it_is_an_attack_is_refused_outright():
    flood = {f"{r},{c}": 0.5 for r in range(200) for c in range(200)}
    assert clean_turn(turn(smell_grid=flood), SIZE) is None


def test_good_scent_cells_survive_untouched():
    assert clean_turn(turn(), SIZE)["smell_grid"] == {"3,3": 0.9, "3,4": 0.5}


MALFORMED_FIELDS = [
    ("barrier wrong arity", {"barrier_placed": [1, 2, 3]}),
    ("barrier non-int", {"barrier_placed": ["a", "b"]}),
    ("barrier off board", {"barrier_placed": [999, 999]}),
    ("claim as string", {"capture_claim": "3,3"}),
    ("claim huge list", {"capture_claim": [1] * 1000}),
    ("response not a dict", {"claim_response": "caught"}),
    ("response caught non-bool", {"claim_response": {"claim": [3, 3], "caught": "yes"}}),
    ("response claim malformed", {"claim_response": {"claim": [99, 99], "caught": True}}),
    ("win_claim not a dict", {"win_claim": "survival"}),
]


@pytest.mark.parametrize(
    ("label", "fields"), MALFORMED_FIELDS, ids=[m[0] for m in MALFORMED_FIELDS]
)
def test_a_malformed_optional_field_is_dropped_not_fatal(label, fields):
    cleaned = clean_turn(turn(**fields), SIZE)
    assert cleaned is not None
    assert cleaned[next(iter(fields))] is None


def test_well_formed_terminal_fields_are_preserved():
    cleaned = clean_turn(
        turn(claim_response={"claim": [3, 3], "caught": True}, win_claim={"type": "survival"}),
        SIZE,
    )
    assert cleaned["claim_response"] == {"claim": [3, 3], "caught": True}
    assert cleaned["win_claim"] == {"type": "survival"}


def test_audit_reveals_are_bounded_and_malformed_envelopes_refused():
    ok = {"sender": "thief", "records": [{"payload": {}}], "result_claim": "survival"}
    assert clean_audit(ok, 35) is not None
    assert clean_audit({**ok, "records": "not-a-list"}, 35) is None
    assert clean_audit({**ok, "sender": 7}, 35) is None
    flood = {**ok, "records": [{"payload": {}}] * (35 * wc.AUDIT_RECORDS_PER_STEP + 1)}
    assert clean_audit(flood, 35) is None
