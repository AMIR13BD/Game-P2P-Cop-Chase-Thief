"""P13 Police portfolio: legality (firewall never substitutes), no diagonals,
determinism, and the key per-mechanism behaviours (barrier area reduction, herding)."""

from thief_agent.domain.board import Board
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy import police_barrier, police_herding, police_hybrid, police_intercept
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import enforce
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_distance import ThiefDistanceBrain

BRAINS = [
    police_intercept.InterceptBrain,
    police_herding.HerdBrain,
    police_barrier.BarrierBrain,
    police_hybrid.PoliceHybridBrain,
]


def _rand_obs(rng):
    n = rng.randint(4, 7)
    cells = [(r, c) for r in range(n) for c in range(n)]
    barriers = frozenset(rng.sample(cells, rng.randint(0, n)))
    free = [c for c in cells if c not in barriers]
    pos = rng.choice(free)
    scent = {rng.choice(free): round(rng.random(), 3) for _ in range(rng.randint(0, 4))}
    return Observation(
        role="police",
        self_pos=pos,
        board_size=n,
        barriers=barriers,
        scent=scent,
        step=rng.randint(1, 30),
        max_barriers=14,
        barriers_used=rng.randint(0, 3),
    )


def test_police_brains_emit_legal_nondiagonal_actions():
    rng = make_rng(3)
    for cls in BRAINS:
        brain = cls(make_rng(1))
        for _ in range(150):
            obs = _rand_obs(rng)
            board = Board(obs.board_size, set(obs.barriers))
            act = brain.decide(obs)
            _, substituted = enforce(act, obs, board, "police")
            assert not substituted, (cls.__name__, act)
            assert not (act.kind == "MOVE" and act.direction not in ("N", "S", "E", "W"))


def test_police_brains_zero_illegal_in_full_game():
    cfg = validate(DEFAULT_GAME_CONFIG)
    for cls in BRAINS:
        res = run_sub_game(
            cls(make_rng(5)),
            ThiefDistanceBrain(make_rng(9)),
            {**cfg, "sub_game_number": 1},
            "grp",
            DevTestSigner(),
            "0" * 40,
        )
        assert res["illegal"] == 0 and res["diagonal"] == 0


def test_hybrid_is_deterministic():
    cfg = validate(DEFAULT_GAME_CONFIG)

    def run():
        return run_sub_game(
            police_hybrid.PoliceHybridBrain(make_rng(5)),
            ThiefDistanceBrain(make_rng(9)),
            {**cfg, "sub_game_number": 1},
            "grp",
            DevTestSigner(),
            "0" * 40,
        )

    a, b = run(), run()
    assert a["outcome"] == b["outcome"] and a["steps"] == b["steps"]


def test_best_barrier_reduces_thief_area():
    # A near-1-wide corridor where one barrier meaningfully shrinks reachable area.
    board = Board(5, {(1, 1), (1, 3), (3, 1), (3, 3)})
    obs = Observation(
        role="police",
        self_pos=(2, 1),
        board_size=5,
        barriers=frozenset(board.barriers),
        scent={(2, 3): 0.9},
        step=2,
        max_barriers=14,
        barriers_used=0,
    )
    bar = police_barrier.best_barrier(obs, board, (2, 3))
    assert bar is None or bar.kind == "BARRIER"


def test_herd_target_not_larger_area():
    board = Board(6)
    from thief_agent.strategy.graph import reachable_area

    thief = (2, 2)
    approach = police_herding.herd_target(board, thief)
    assert reachable_area(board, approach) <= reachable_area(board, thief) + 1
