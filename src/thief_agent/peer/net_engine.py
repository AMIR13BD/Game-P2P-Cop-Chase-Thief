"""One peer's half of a distributed sub-game: computes its own (secret) moves and
emits only public turn messages. Capture is resolved by public capture-claims."""

from ..domain import capture as cap
from ..domain import smell
from ..domain.board import Board
from ..domain.crypto import seal
from ..domain.protocol import build_payload
from ..domain.rules import barrier_cell
from ..domain.rules import step as step_move
from ..strategy.base import Observation
from ..strategy.belief import BeliefMap
from ..strategy.firewall import enforce
from ..strategy.hint_filter import sanitize
from .sealing import make_step0_record


def _grid_out(g: dict) -> dict:
    return {f"{r},{c}": v for (r, c), v in g.items()}


def _grid_in(d: dict) -> dict:
    return {tuple(int(x) for x in k.split(",")): v for k, v in (d or {}).items()}


class PeerHalf:
    def __init__(self, role, cfg, brain, group, github_commit, signer, sub_game=1):
        self.role, self.cfg, self.brain = role, cfg, brain
        self.board = Board(cfg["grid_size"])
        self.pos = tuple(cfg["cop_start"]) if role == "police" else tuple(cfg["thief_start"])
        self.rho = cfg["pheromone_decay"]
        self.own_scent = smell.step_update({}, self.pos, self.board, self.rho)
        self.recv_scent: dict = {}
        self.recv_hint = ""
        self.step = 0
        self.barriers_used = 0
        self.records = [make_step0_record(group, sub_game, signer, github_commit)]

    def _belief_peak(self):
        b = BeliefMap(self.board)
        b.update(self.recv_scent)
        return b.argmax()

    def act(self) -> dict:
        self.step += 1
        obs = Observation(
            role=self.role,
            self_pos=self.pos,
            board_size=self.board.size,
            barriers=frozenset(self.board.barriers),
            scent=dict(self.recv_scent),
            last_hint=self.recv_hint,
            step=self.step,
            max_barriers=self.cfg["max_barriers"],
            barriers_used=self.barriers_used,
        )
        act, _ = enforce(self.brain.decide(obs), obs, self.board, self.role)
        hint = sanitize(self.brain.hint(obs))  # 15-word + leak filter stays enforced
        barrier_placed = None
        if act.kind == "MOVE":
            self.pos = step_move(self.pos, act.direction)
        elif act.kind == "BARRIER":  # police only (firewall guarantees this)
            cell = barrier_cell(self.pos, act.direction)
            self.board.add_barrier(cell)
            self.barriers_used += 1
            barrier_placed = [cell[0], cell[1]]
        self.own_scent = smell.step_update(self.own_scent, self.pos, self.board, self.rho)
        payload = build_payload(
            self.step,
            self.role,
            f"grid={self.board.size};self={list(self.pos)}",
            f"{act.kind}:{act.direction}",
            "truth",
            hint,
        )
        self.records.append({"payload": payload, **seal(payload)})
        claim = (
            list(self.pos) if (self.role == "police" and self.pos == self._belief_peak()) else None
        )
        return {
            "step": self.step,
            "sender": self.role,
            "commit": self.records[-1]["commit"],
            "hint": hint,
            "scent": _grid_out(self.own_scent),
            "claim": claim,
            "barrier_placed": barrier_placed,
        }

    def hold(self) -> dict:
        """A HOLD turn: seal the CURRENT (unchanged) position — no move. Used for the caught
        concession so a caught thief does not step off its cell (reference send_final /
        MoveType.HOLD semantics)."""
        self.step += 1
        self.own_scent = smell.step_update(self.own_scent, self.pos, self.board, self.rho)
        payload = build_payload(
            self.step,
            self.role,
            f"grid={self.board.size};self={list(self.pos)}",
            "HOLD:-",
            "truth",
            "",
        )
        self.records.append({"payload": payload, **seal(payload)})
        return {
            "step": self.step,
            "sender": self.role,
            "commit": self.records[-1]["commit"],
            "hint": "",
            "scent": _grid_out(self.own_scent),
            "claim": None,
            "barrier_placed": None,
        }

    def _apply_barrier(self, bp) -> bool:
        """Apply a peer's public barrier declaration on the Thief's board, keeping both
        boards identical. Rejects malformed/out-of-bounds/duplicate cells. Returns True
        if the barrier captures or traps this Thief."""
        if self.role != "thief" or not isinstance(bp, list) or len(bp) != 2:
            return False
        try:
            cell = (int(bp[0]), int(bp[1]))
        except (TypeError, ValueError):
            return False
        if not self.board.in_bounds(cell) or cell in self.board.barriers:
            return False  # out-of-bounds / duplicate barrier rejected
        self.board.add_barrier(cell)
        return cap.barrier_captures(cell, self.pos) or cap.thief_trapped(self.pos, self.board)

    def receive(self, msg: dict) -> bool:
        """Absorb opponent public message; apply any declared barrier; return True if
        their barrier or capture-claim captures me."""
        self.recv_hint = msg.get("hint", "")
        self.recv_scent = _grid_in(msg.get("scent"))
        caught_by_barrier = self._apply_barrier(msg.get("barrier_placed"))
        claim = msg.get("claim")
        caught_by_claim = self.role == "thief" and claim is not None and tuple(claim) == self.pos
        return bool(caught_by_barrier or caught_by_claim)
