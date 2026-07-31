"""One peer's half of a distributed sub-game: computes its own (secret) moves and
emits only public turn messages. Capture is resolved by public capture-claims."""

from ..domain import smell
from ..domain.board import Board
from ..domain.crypto import seal
from ..domain.protocol import build_payload
from ..domain.rules import step as step_move
from ..strategy.base import Observation
from ..strategy.belief import BeliefMap
from ..strategy.firewall import enforce
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
            barriers_used=0,
        )
        act, _ = enforce(self.brain.decide(obs), obs, self.board, self.role)
        hint = self.brain.hint(obs)
        if act.kind == "MOVE":
            self.pos = step_move(self.pos, act.direction)
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
        }

    def receive(self, msg: dict) -> bool:
        """Absorb opponent public message; return True if their claim captures me."""
        self.recv_hint = msg.get("hint", "")
        self.recv_scent = _grid_in(msg.get("scent"))
        claim = msg.get("claim")
        return bool(self.role == "thief" and claim is not None and tuple(claim) == self.pos)
