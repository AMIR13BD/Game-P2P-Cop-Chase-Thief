"""Deliberate replay-tampering fixtures (P20 test support): produce corrupted copies
of a records list so the replay verifier's TAMPERED path can be exercised. Never
mutates the input."""

import copy


def _step_match(rec, step) -> bool:
    return isinstance(rec, dict) and rec.get("payload", {}).get("step") == step


def tamper_commit(records: list, step: int = 1) -> list:
    """Return a copy with the commitment of the record at `step` corrupted."""
    out = copy.deepcopy(records)
    for rec in out:
        if _step_match(rec, step):
            rec["commit"] = "0" * 64
    return out


def tamper_payload(records: list, step: int = 1) -> list:
    """Return a copy with the payload at `step` altered (commit no longer matches)."""
    out = copy.deepcopy(records)
    for rec in out:
        if _step_match(rec, step):
            rec["payload"]["move"] = "MOVE:TAMPER"
    return out
