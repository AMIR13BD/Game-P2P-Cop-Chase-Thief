"""Opponent profiling from AUDITED evidence only (P15).

`observe_subgame` runs the integrity audit itself and refuses to ingest anything
that does not verify, so tampered, hidden, or unrevealed data can never enter a
profile. Only fields already made public by a valid audit (revealed positions,
moves, hints, declared intent) are used. Profiles are per-opponent and reset via
the ProfileStore between different opponents."""

import re

from ..peer.audit import run_audit

_SELF = re.compile(r"self=\[(\d+),\s*(\d+)\]")
_GRID = re.compile(r"grid=(\d+)")


def _parse_turn(rec: dict):
    """Extract (role, cell, kind, direction, intent) from one revealed record."""
    p = rec["payload"]
    m = _SELF.search(p.get("state", ""))
    cell = (int(m.group(1)), int(m.group(2))) if m else None
    kind, _, direction = p.get("move", "STAY:None").partition(":")
    g = _GRID.search(p.get("state", ""))
    grid = int(g.group(1)) if g else 0
    return p.get("role"), cell, kind, direction, p.get("intent", "truth"), grid


class OpponentProfile:
    """Accumulated, audit-verified behavioural tendencies for one opponent."""

    def __init__(self, opponent_id: str) -> None:
        self.opponent_id = opponent_id
        self.turns = 0
        self.moves: dict[str, int] = {}
        self.barriers = 0
        self.truthful = 0
        self.corner_entries = 0
        self.sub_games = 0
        self.wins = 0

    def observe_subgame(self, records: list, signer=None, outcome: str | None = None) -> bool:
        """Ingest one sub-game's records IFF they pass the integrity audit."""
        if not run_audit(records, signer)["passed"]:
            return False  # unaudited / tampered evidence is rejected outright
        self.sub_games += 1
        if outcome in ("capture", "survival"):
            self.wins += 1
        for rec in records:
            if rec.get("payload", {}).get("step", 0) == 0:
                continue
            _role, cell, kind, direction, intent, grid = _parse_turn(rec)
            self.turns += 1
            key = direction if kind == "MOVE" else kind
            self.moves[key] = self.moves.get(key, 0) + 1
            self.barriers += 1 if kind == "BARRIER" else 0
            self.truthful += 1 if intent == "truth" else 0
            if cell and grid and cell[0] in (0, grid - 1) and cell[1] in (0, grid - 1):
                self.corner_entries += 1
        return True

    def features(self) -> dict:
        t = max(self.turns, 1)
        top = max(self.moves.values()) if self.moves else 0
        return {
            "opponent_id": self.opponent_id,
            "turns": self.turns,
            "move_preferences": {k: round(v / t, 3) for k, v in self.moves.items()},
            "barrier_tendency": round(self.barriers / t, 3),
            "hint_honesty": round(self.truthful / t, 3),
            "risk_tolerance": round(self.corner_entries / t, 3),
            "predictability": round(top / t, 3),
            "aggression": round(self.barriers / t + top / t, 3),
            "effectiveness": round(self.wins / max(self.sub_games, 1), 3),
        }


class ProfileStore:
    """Holds one profile per opponent; guarantees a clean reset between opponents."""

    def __init__(self) -> None:
        self._by_id: dict[str, OpponentProfile] = {}

    def get(self, opponent_id: str) -> OpponentProfile:
        if opponent_id not in self._by_id:
            self._by_id[opponent_id] = OpponentProfile(opponent_id)
        return self._by_id[opponent_id]

    def reset(self, opponent_id: str) -> None:
        self._by_id.pop(opponent_id, None)
