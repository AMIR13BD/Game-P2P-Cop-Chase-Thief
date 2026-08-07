"""Unit tests for the interop adapter's pure layers: ids, terms, wire, delivery, scoring.
Byte-level constructions are cross-checked against an independent stdlib re-derivation of
the reference (no import of the adapter's own crypto)."""

import hashlib
import json
import uuid

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.interop import ids, terms
from thief_agent.interop.delivery import (
    EquivocationError,
    Inbox,
    ProtocolViolationError,
    delivery_decision,
)
from thief_agent.interop.wire import AuditPayload, Negotiation, TurnMessage


def _canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _ref_uid(t, a, b):
    seed = f"{_canon(t)}|{'|'.join(sorted([a, b]))}"
    return str(uuid.UUID(bytes=hashlib.sha256(seed.encode()).digest()[:16]))


# --- ids ----------------------------------------------------------------------------------
def test_game_id_is_sorted_pair_order_independent():
    t = terms.default_terms()
    assert ids.derive_game_ids(t, "bbb", "aaa")[0] == "aaa-vs-bbb"
    assert ids.derive_game_ids(t, "aaa", "bbb") == ids.derive_game_ids(t, "bbb", "aaa")


def test_game_uid_matches_independent_reference_and_is_uuid():
    t = terms.default_terms()
    _, guid = ids.derive_game_ids(t, "amireman", "sparring-local")
    assert guid == _ref_uid(t, "amireman", "sparring-local")
    uuid.UUID(guid)


def test_artifact_filenames():
    assert ids.declaration_name("g") == "declaration_g.json"
    assert ids.config_name("g", 2) == "config_g_g02.json"
    assert ids.log_name("g", 12) == "log_g_g12.json"
    assert ids.result_name("g") == "result_g.json"
    assert ids.links("g")["config"] == "config_g_g<NN>.json"


# --- terms --------------------------------------------------------------------------------
def test_default_terms_have_14_keys_and_validate():
    t = terms.default_terms()
    assert set(t) == set(terms.TERMS_KEYS) and len(t) == 14
    terms.validate_terms(t)


def test_terms_from_config_extracts_flat_set_from_wider():
    wider = {**terms.default_terms(), "network": {"port": 1}, "strategy": {"x": 1}}
    assert terms.terms_from_config(wider) == terms.default_terms()


def test_validate_terms_rejects_missing():
    t = terms.default_terms()
    with pytest.raises(ConfigError):
        terms.validate_terms({**t, "board_size": None})


def test_to_flat_cfg_maps_engine_keys():
    flat = terms.to_flat_cfg(terms.default_terms(), seed=7)
    assert flat["grid_size"] == 7 and flat["max_barriers"] == 14
    assert flat["survival_threshold"] == 35 and flat["seed"] == 7


# --- wire ---------------------------------------------------------------------------------
def test_turn_message_round_trip_and_tolerance():
    m = TurnMessage(step=1, sender="police", commit="c", hint="hi", smell_grid={"0,0": 0.5})
    back = TurnMessage.from_wire({**m.to_wire(), "unknown_future_key": 1})
    assert back.step == 1 and back.sender == "police" and back.smell_grid == {"0,0": 0.5}


def test_turn_message_requires_core_fields():
    with pytest.raises(ValueError):
        TurnMessage.from_wire({"sender": "police", "commit": "c"})


def test_audit_and_negotiation_round_trip():
    a = AuditPayload(
        sender="thief",
        records=[{"payload": {}, "nonce": "n", "commit": "c"}],
        result_claim="survival",
    )
    assert AuditPayload.from_wire(a.to_wire()).result_claim == "survival"
    n = Negotiation(terms={"a": 1}, nonce="x", signature="s", group_id="g", game_uid=None)
    wire = n.to_wire()
    assert "game_uid" not in wire  # None dropped
    assert Negotiation.from_wire(wire).group_id == "g"


# --- delivery (SPEC 7.1 truth table) ------------------------------------------------------
@pytest.mark.parametrize(
    "state,arrival,expected",
    [
        ({"played": {}, "window": 4, "next": 1}, {"step": 1, "commit": "a"}, "apply"),
        ({"played": {"1": "a"}, "window": 4, "next": 2}, {"step": 1, "commit": "a"}, "absorb"),
        (
            {"played": {"1": "a"}, "window": 4, "next": 2},
            {"step": 1, "commit": "b"},
            "equivocation",
        ),
        ({"played": {"1": "a"}, "window": 4, "next": 2}, {"step": 4, "commit": "d"}, "buffer"),
        ({"played": {"1": "a"}, "window": 4, "next": 2}, {"step": 99, "commit": "z"}, "violation"),
        ({"played": {}, "window": 0, "next": 5}, {"step": 2, "commit": "x"}, "discard"),
    ],
)
def test_delivery_decision_truth_table(state, arrival, expected):
    assert delivery_decision(state, arrival) == expected


def test_inbox_dedup_reorder_and_equivocation():
    box = Inbox(window=4)
    assert box.offer({"step": 1, "commit": "a"}) == [{"step": 1, "commit": "a"}]
    assert box.offer({"step": 1, "commit": "a"}) == []  # duplicate absorbed
    assert box.absorbed == 1
    assert box.offer({"step": 3, "commit": "c"}) == []  # buffered ahead of gap
    ready = box.offer({"step": 2, "commit": "b"})  # fills gap, drains buffer
    assert [r["step"] for r in ready] == [2, 3]
    with pytest.raises(EquivocationError):
        box.offer({"step": 1, "commit": "different"})


def test_inbox_flood_raises_protocol_violation():
    with pytest.raises(ProtocolViolationError):
        Inbox(window=4).offer({"step": 50, "commit": "x"})
