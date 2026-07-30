"""Deterministic single-sub-game simulation (no network, no I/O)."""

from ..peer.turn_engine import run_sub_game
from ..security.signer import DevTestSigner
from ..strategy.police_greedy import PoliceGreedyBrain
from ..strategy.rng import make_rng
from ..strategy.thief_distance import ThiefDistanceBrain


def simulate(cfg: dict, seed: int, signer=None, group_name: str = "sim") -> dict:
    signer = signer or DevTestSigner()
    police = PoliceGreedyBrain(make_rng(seed))
    thief = ThiefDistanceBrain(make_rng(seed + 7))
    return run_sub_game(police, thief, {**cfg, "sub_game_number": 1}, group_name, signer)
