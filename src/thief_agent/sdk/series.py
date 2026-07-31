"""Run a local six-sub-game series with role alternation and fresh per-game state.

Each sub-game runs under safe_play (defined failures -> technical 0/0) and a final
mutual audit; a failed audit is a technical loss."""

from ..constants import Role, complement
from ..peer.audit import run_audit
from ..peer.technical import safe_play, technical_result
from ..peer.turn_engine import run_sub_game
from ..strategy.police_greedy import PoliceGreedyBrain
from ..strategy.rng import make_rng
from ..strategy.thief_distance import ThiefDistanceBrain

SUB_GAMES = 6


def role_for(natural: Role, sub_game: int) -> Role:
    """Natural role on odd sub-games (1,3,5); swapped on even (2,4,6)."""
    return natural if sub_game % 2 == 1 else complement(natural)


def run_series(
    cfg: dict,
    natural_role: Role,
    group_name: str,
    signer,
    seed: int = 1234,
    github_commit: str = "uncommitted",
) -> dict:
    subs: list[dict] = []
    role_seq: list[str] = []
    self_total = opp_total = 0
    for n in range(1, SUB_GAMES + 1):
        self_role = role_for(natural_role, n)
        role_seq.append(self_role.value)
        police = PoliceGreedyBrain(make_rng(seed + n))
        thief = ThiefDistanceBrain(make_rng(seed + 100 + n))
        res = safe_play(
            lambda p=police, t=thief, i=n: run_sub_game(
                p, t, {**cfg, "sub_game_number": i}, group_name, signer, github_commit
            )
        )
        if res["outcome"] != "technical":
            audit = run_audit(res["records"], signer)
            if not audit["passed"]:
                res = technical_result("audit_failed", {"failed_steps": audit["failed_steps"]})
        if self_role is Role.POLICE:
            self_s, opp_s = res["police_score"], res["thief_score"]
        else:
            self_s, opp_s = res["thief_score"], res["police_score"]
        self_total += self_s
        opp_total += opp_s
        subs.append(
            {
                "sub_game": n,
                "self_role": self_role.value,
                "outcome": res["outcome"],
                "self_score": self_s,
                "opp_score": opp_s,
                "steps": res["steps"],
                "records": res["records"],
                "trajectory": res["trajectory"],
                "illegal": res["illegal"],
                "diagonal": res["diagonal"],
            }
        )
    tie = self_total == opp_total
    return {
        "sub_games": subs,
        "role_sequence": role_seq,
        "self_total": self_total,
        "opp_total": opp_total,
        "series_tie": tie,
        "winner": "tie" if tie else ("self" if self_total > opp_total else "opp"),
    }
