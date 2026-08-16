"""Pure view-model for the replay viewer: frame stepping plus the real integrity verdict.

The VERIFIED OK / TAMPERED label is never assembled here. It is delegated to
`replay_verify.replay_status`, which recomputes each record's SHA-256 commitment from the
revealed (nonce, payload) pair, so the badge the window paints is the output of the actual
cryptographic check and cannot be set independently of it."""

import os

from ..report import ids
from .replay_controls import status_line, step_controls
from .replay_data import board_at, load_log, reconstruct
from .replay_verify import replay_status


class ReplayModel:
    """One sub-game: reconstructed frames, a cursor, and its cryptographic verdict."""

    def __init__(self, records, board_size: int, sub_game: int = 1) -> None:
        self.records = records or []
        self.board_size = board_size
        self.sub_game = sub_game
        self.frames = reconstruct(self.records)
        self.status = replay_status(self.records)
        self.index = 0

    @property
    def total(self) -> int:
        return len(self.frames)

    @property
    def verified(self) -> bool:
        """The real per-step SHA-256 verdict for this sub-game."""
        return bool(self.status.get("verified"))

    def integrity_text(self) -> str:
        """ "VERIFIED OK" or "TAMPERED at steps ..." straight from the verifier."""
        return status_line(self.status)

    def controls(self) -> dict:
        return step_controls(self.index, self.total)

    def go(self, index: int) -> None:
        self.index = step_controls(index, self.total)["index"]

    def step_forward(self) -> None:
        self.go(self.index + 1)

    def step_back(self) -> None:
        self.go(self.index - 1)

    def trail(self, idx: int) -> dict:
        """role -> the cells that role is recorded as having occupied up to `idx`."""
        walked: dict = {"police": [], "thief": []}
        for frame in self.frames[: idx + 1]:
            if frame.cell is not None and frame.role in walked:
                walked[frame.role].append(tuple(frame.cell))
        return walked

    def current(self) -> dict:
        """The renderable frame at the cursor: revealed board, step, and stepper bounds."""
        controls = self.controls()
        idx = controls["index"]
        frame = self.frames[idx] if self.frames else None
        pos = board_at(self.frames, idx) if self.frames else {}
        return {
            "sub_game": self.sub_game,
            "index": idx,
            "total": self.total,
            "has_prev": controls["has_prev"],
            "has_next": controls["has_next"],
            "step": getattr(frame, "step", 0),
            "mover": getattr(frame, "role", ""),
            "action": _action_text(frame),
            "hint": getattr(frame, "hint", "") or "",
            "police": pos.get("police"),
            "thief": pos.get("thief"),
            "trail": self.trail(idx),
            "barriers": [tuple(b) for b in pos.get("barriers", ())],
            "board_size": self.board_size,
            "verified": self.verified,
            "integrity": self.integrity_text(),
            "failed_steps": list(self.status.get("failed_steps", ())),
        }


def _action_text(frame) -> str:
    if frame is None:
        return "-"
    direction = getattr(frame, "direction", None)
    kind = getattr(frame, "kind", "") or "-"
    return f"{kind}:{direction}" if direction else kind


def load_sub_games(directory, game_id, board_size, count: int = 6) -> list[ReplayModel]:
    """Every sub-game of a recorded series that has replayable records, in order."""
    models: list[ReplayModel] = []
    for number in range(1, count + 1):
        records = load_log(os.path.join(directory, ids.log_name(game_id, number)))
        if records:
            models.append(ReplayModel(records, board_size, number))
    return models


def series_verdict(models) -> tuple[bool, str]:
    """(all_verified, summary) across a loaded series."""
    if not models:
        return False, "NO REPLAYABLE LOGS"
    bad = [m.sub_game for m in models if not m.verified]
    if bad:
        return False, "TAMPERED in sub-games " + ", ".join(str(n) for n in bad)
    return True, f"VERIFIED OK - {len(models)}/{len(models)} sub-games"
