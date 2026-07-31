"""Metric accumulation for the evaluation harness (P12). Tracks outcome rates,
scores, legality, fallback/timeout rates and decision-time distribution."""

from dataclasses import dataclass, field


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolation percentile (q in [0,1]) of a value list."""
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


@dataclass
class MatchStats:
    games: int = 0
    captures: int = 0
    survivals: int = 0
    technical: int = 0
    self_score: int = 0
    opp_score: int = 0
    illegal: int = 0
    diagonal: int = 0
    fallbacks: int = 0
    timeouts: int = 0
    steps: int = 0
    decision_times: list[float] = field(default_factory=list)

    def add(self, res: dict, self_s: int, opp_s: int, times: list, budget_s: float) -> None:
        self.games += 1
        self.captures += 1 if res["outcome"] == "capture" else 0
        self.survivals += 1 if res["outcome"] == "survival" else 0
        self.technical += 1 if res["outcome"] == "technical" else 0
        self.self_score += self_s
        self.opp_score += opp_s
        self.illegal += res["illegal"]
        self.diagonal += res["diagonal"]
        self.steps += res["steps"]
        self.decision_times += times
        self.timeouts += sum(1 for t in times if t > budget_s)

    def summary(self, role: str) -> dict:
        g = max(self.games, 1)
        decisions = max(len(self.decision_times), 1)
        ms = [t * 1000 for t in self.decision_times]
        return {
            "games": self.games,
            "capture_rate": round(self.captures / g, 3),
            "survival_rate": round(self.survivals / g, 3),
            "technical_rate": round(self.technical / g, 3),
            "avg_self_score": round(self.self_score / g, 2),
            "avg_opp_score": round(self.opp_score / g, 2),
            "illegal_actions": self.illegal,
            "diagonal_actions": self.diagonal,
            "fallback_rate": round(self.fallbacks / decisions, 4),
            "timeouts": self.timeouts,
            "decision_ms_mean": round(sum(ms) / decisions, 4),
            "decision_ms_p50": round(percentile(ms, 0.50), 4),
            "decision_ms_p95": round(percentile(ms, 0.95), 4),
        }
