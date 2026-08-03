"""Fresh held-out trap opponents (sim/opponents/trap.py) are legal in both roles and drive
a full legal sub-game (used only for final Thief-generalisation validation)."""

from thief_agent.domain.board import Board
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.opponents.trap import (
    ChokeControllerBrain,
    DelayedCornerBrain,
    EdgeHerderBrain,
    SealAssistBrain,
)
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.rng import make_rng

CFG = validate(DEFAULT_GAME_CONFIG)
BRAINS = (EdgeHerderBrain, ChokeControllerBrain, DelayedCornerBrain, SealAssistBrain)


def _obs(role):
    return Observation(
        role=role,
        self_pos=(2, 2),
        board_size=7,
        barriers=frozenset(),
        scent={(5, 5): 0.9},
        step=3,
        max_barriers=14,
        barriers_used=0,
    )


def test_trap_opponents_legal_both_roles():
    board = Board(7)
    for cls in BRAINS:
        for role in ("police", "thief"):
            obs = _obs(role)
            act = cls(make_rng(1)).decide(obs)
            assert is_legal(act, obs, board, role)


def test_trap_opponents_drive_a_full_subgame():
    for cls in BRAINS:
        res = run_sub_game(
            cls(make_rng(2)),
            MetaController("thief", make_rng(3), horizon=35, epsilon=0.0),
            {**CFG, "sub_game_number": 1},
            "t",
            DevTestSigner(),
            "0" * 40,
        )
        assert res["illegal"] == 0 and res["outcome"] in {"capture", "survival"}
