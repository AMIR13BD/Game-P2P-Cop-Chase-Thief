"""Replay reconstruction (P20): rebuild per-turn frames from AUDITED records.

Post-audit both peers' true positions are revealed, so replay may legally show full
truth. Malformed records/logs are skipped safely -- the viewer never crashes."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..domain.rules import barrier_cell

_SELF = re.compile(r"self=\[(\d+),\s*(\d+)\]")


@dataclass
class Frame:
    step: int
    role: str
    cell: tuple | None
    kind: str
    direction: str | None
    hint: str
    barriers: list = field(default_factory=list)


def _parse(rec):
    p = rec.get("payload") if isinstance(rec, dict) else None
    if not isinstance(p, dict):
        return None
    m = _SELF.search(p.get("state", ""))
    cell = (int(m.group(1)), int(m.group(2))) if m else None
    kind, _, direction = str(p.get("move", "STAY:None")).partition(":")
    return p.get("step"), p.get("role"), cell, kind, direction, p.get("hint", "")


def reconstruct(records) -> list[Frame]:
    """Turn frames (step>0) with accumulated barriers; malformed records skipped."""
    frames: list[Frame] = []
    barriers: list[list] = []
    for rec in records or []:
        parsed = _parse(rec)
        if parsed is None:
            continue
        step, role, cell, kind, direction, hint = parsed
        if not isinstance(step, int) or step <= 0:
            continue  # step-0 declaration is not a turn frame
        if kind == "BARRIER" and cell is not None and direction in ("SELF", "N", "S", "E", "W"):
            barriers.append(list(barrier_cell(cell, direction)))
        frames.append(Frame(step, role, cell, kind, direction, hint, [list(b) for b in barriers]))
    return frames


def load_log(path) -> list:
    """Load the records list from a log artifact; [] on missing/malformed (fail closed)."""
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    recs = obj.get("records") if isinstance(obj, dict) else None
    return recs if isinstance(recs, list) else []


def board_at(frames: list[Frame], idx: int) -> dict:
    """Latest known police/thief cells and barriers up to and including frame `idx`."""
    police = thief = None
    barriers: list = []
    for f in frames[: idx + 1]:
        if f.role == "police":
            police = f.cell
        elif f.role == "thief":
            thief = f.cell
        barriers = f.barriers
    return {"police": police, "thief": thief, "barriers": barriers}


def render_truth_board(size: int, police, thief, barriers=()) -> str:
    """Post-audit board showing BOTH revealed positions (P for police, T for thief)."""
    bset = {tuple(b) for b in barriers}
    rows = []
    for r in range(size):
        cells = []
        for c in range(size):
            cell = (r, c)
            if police and cell == tuple(police):
                ch = "P"
            elif thief and cell == tuple(thief):
                ch = "T"
            elif cell in bset:
                ch = "#"
            else:
                ch = "·"
            cells.append(ch)
        rows.append(" ".join(cells))
    return "\n".join(rows)
