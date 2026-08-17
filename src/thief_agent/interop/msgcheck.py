"""Validate an inbound wire message BEFORE it can touch any game state.

An arriving turn is adversarial input. A partially applied bad turn cannot be rolled
back, so everything here is decided up front and the caller only ever sees a message that
is already safe to fold in.

Two shapes of defect, handled differently on purpose:

* **Structurally unusable** — no readable step, no well-formed commit, no sender, or a
  message too large to be a legal 7x7 turn. The message is REFUSED (``None``). It is
  dropped, logged and the sub-game continues; it is deliberately NOT scored as a fault
  against anyone. The lecturer's reference performs no inbound validation at all, so
  there is no precedent for converting an opponent's malformed byte into an outcome, and
  inventing one would let a peer choose our result by sending garbage.
* **A spoiled field inside an otherwise readable turn** — a scent cell with a NaN, an
  off-board barrier, a claim of the wrong arity. The field is dropped and the turn is kept.

Unknown keys are always tolerated: that is the extension seam the league relies on, and a
receiver that refuses them cannot be extended without a flag day.
"""

from ..shared import wirecheck as wc


def _claim_response(raw: object, size: int) -> dict | None:
    """``{"claim": [r, c], "caught": bool}`` — it settles a sub-game, so it is checked
    strictly rather than read with ``.get("caught")`` truthiness."""
    if not isinstance(raw, dict) or not isinstance(raw.get("caught"), bool):
        return None
    cell = wc.as_cell(raw.get("claim"), size)
    return None if cell is None else {"claim": list(cell), "caught": raw["caught"]}


def _win_claim(raw: object) -> dict | None:
    if not isinstance(raw, dict) or not isinstance(raw.get("type"), str):
        return None
    return {"type": raw["type"]}


def clean_turn(raw: object, board_size: int) -> dict | None:
    """A turn message reduced to well-formed fields, or ``None`` to refuse it outright."""
    if not isinstance(raw, dict) or wc.oversized(raw):
        return None
    step = wc.as_step(raw.get("step"))
    sender = raw.get("sender")
    if step is None or not wc.is_commit(raw.get("commit")):
        return None
    if not isinstance(sender, str) or not sender:
        return None
    cells = wc.scent_cells(raw.get("smell_grid"), board_size, board_size * board_size)
    barrier = wc.as_cell(raw.get("barrier_placed"), board_size)
    claim = wc.as_cell(raw.get("capture_claim"), board_size)
    return {
        "step": step,
        "sender": sender,
        "commit": raw["commit"],
        "hint": wc.as_text(raw.get("hint")),
        "smell_grid": {f"{r},{c}": v for (r, c), v in cells.items()},
        "timestamp": wc.as_text(raw.get("timestamp")),
        "barrier_placed": None if barrier is None else list(barrier),
        "capture_claim": None if claim is None else list(claim),
        "claim_response": _claim_response(raw.get("claim_response"), board_size),
        "win_claim": _win_claim(raw.get("win_claim")),
    }


def record_step(record: object) -> int:
    """The step a revealed record claims, or -1 when it does not readably claim one.

    -1 matches no step we ever played, so an unreadable record simply fails to corroborate
    instead of raising out of the audit — which is what a hostile reveal would want.
    """
    payload = record.get("payload") if isinstance(record, dict) else None
    step = wc.as_step(payload.get("step")) if isinstance(payload, dict) else None
    return -1 if step is None else step


def clean_audit(raw: object, max_steps: int) -> dict | None:
    """An audit envelope with a bounded reveal, or ``None`` to refuse it.

    The record CONTENTS are not validated here: each side reveals its own schema and we
    only re-hash it (SPEC §3 makes the payload schema explicitly non-interoperable). Only
    the envelope and the record COUNT are our business.
    """
    if not isinstance(raw, dict) or wc.oversized(raw):
        return None
    records = raw.get("records")
    if not isinstance(records, list):
        return None
    if len(records) > max_steps * wc.AUDIT_RECORDS_PER_STEP:
        return None
    sender, claim = raw.get("sender"), raw.get("result_claim")
    if not isinstance(sender, str) or not isinstance(claim, str):
        return None
    out = {k: v for k, v in raw.items() if k in _AUDIT_KEYS}
    out["records"] = [r for r in records if isinstance(r, dict)]
    return out


_AUDIT_KEYS = frozenset({"sender", "records", "result_claim", "consensus_sha", "sub_game_number"})
