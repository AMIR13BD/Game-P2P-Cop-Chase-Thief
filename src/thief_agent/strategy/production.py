"""Production brain factory (single source of truth for real gameplay).

Selection order, highest priority first, so every existing opt-in keeps its meaning:

  1. an EXPLICIT ``POLICE_STRATEGY`` / ``THIEF_STRATEGY`` environment choice;
  2. the OpenAI-primary advisor, when ``OPENAI_ADVISOR`` explicitly enables it;
  3. the default championship brain for the role.

The default changed on measured evidence. Protocol-faithful benchmarking against the
Orcai-MJ public agents (their real ``RingRunnerThief`` / ``TrapperPolice``, our real
``PeerHalf``, wire capture semantics) put the old MetaController default at 0/20
captures as Cop, because its barrier-first portfolio rule spends the turn placing
walls instead of closing; and the distance-first evader at 9/20 survivals as Thief,
losing every game to a barrier pounce or an enclosure. The two brains selected here
score 20/20 and 20/20 on the same benchmark, and match or beat the previous defaults
against every opponent in our own sparring registry (``sim/opponents``), so this is a
strict improvement rather than a matchup-specific gamble.

Both defaults degrade safely: ``RingBreakerBrain`` scores its opponent model against
the scent actually broadcast and hands the turn to ``ContainBayesBrain`` when the
model stops describing the opponent, and ``AntiSqueezeBrain`` is a general
topological evader with no opponent-specific assumption in it at all. The
MetaController portfolio remains available via ``*_STRATEGY=meta``.
"""

import os

from .meta import MetaController
from .police_greedy import PoliceGreedyBrain
from .rng import make_rng
from .thief_distance import ThiefDistanceBrain

DEFAULT_HORIZON = 35


def advisor_policy() -> str | None:
    """Championship OpenAI-primary policy from the environment, or None (deterministic).

    OPENAI_ADVISOR enables the AI-primary layer; OPENAI_ADVISOR_POLICY in {A,B,C}
    (default C = every turn). Kept OFF by default so the whole test-suite makes ZERO
    real API calls; the real non-counted demo opts in explicitly."""
    if os.environ.get("OPENAI_ADVISOR", "").strip().lower() in ("", "0", "false", "no"):
        return None
    pol = os.environ.get("OPENAI_ADVISOR_POLICY", "C").strip().upper()
    return pol if pol in ("A", "B", "C") else "C"


def police_specialist(seed, horizon):
    """An EXPLICIT ``POLICE_STRATEGY`` choice, or None when the caller made none.

    `contain` selects ContainBrain (shortest-path + Chebyshev edge-cornering + value-gated
    barriers). Measured to capture the current uoh-ay26 thief far more (~0.47 -> ~0.79) and
    to score >= the portfolio in the exact six-game series, but it is LESS robust vs pure
    corner-hugging evaders, so it is a per-match opt-in, never the default (avoids overfit).
    `contain_bayes` adds Bayesian localisation; `meta` restores the portfolio controller."""
    strat = os.environ.get("POLICE_STRATEGY", "").strip().lower()
    if strat == "contain":
        from .police_contain import ContainBrain

        return ContainBrain(make_rng(seed), horizon=horizon, seed=seed)
    if strat == "contain_bayes":  # ContainBrain chase + Bayesian localisation
        from .police_contain_bayes import ContainBayesBrain

        return ContainBayesBrain(make_rng(seed), horizon=horizon, seed=seed)
    if strat == "ringbreak":
        return default_police(seed, horizon)
    if strat == "meta":
        return MetaController("police", make_rng(seed), horizon=horizon, epsilon=0.0)
    return None


def thief_specialist(seed, horizon):
    """An EXPLICIT ``THIEF_STRATEGY`` choice, or None when the caller made none."""
    strat = os.environ.get("THIEF_STRATEGY", "").strip().lower()
    if strat == "survivor":
        from .thief_survivor import SurvivorBrain

        return SurvivorBrain(make_rng(seed), horizon=horizon, seed=seed)
    if strat == "antisqueeze":
        return default_thief(seed, horizon)
    if strat == "meta":
        return MetaController("thief", make_rng(seed), horizon=horizon, epsilon=0.0)
    return None


def default_police(seed, horizon):
    """Opponent-adaptive Cop: exact ring-runner counter over a ContainBayes fallback."""
    from .police_ringbreak import RingBreakerBrain

    return RingBreakerBrain(make_rng(seed), horizon=horizon, seed=seed)


def default_thief(seed, horizon):
    """Topology-first evader: survival area and escape structure over raw distance."""
    from .thief_antisqueeze import AntiSqueezeBrain

    return AntiSqueezeBrain(make_rng(seed), horizon=horizon, seed=seed)


def production_brain(role, seed, horizon=DEFAULT_HORIZON, profile=None, credibility=0.5):
    """Adaptive MetaController for `role`, deterministic and firewall-guarded."""
    mc = MetaController(
        role, make_rng(seed), horizon=horizon, epsilon=0.0, profile=profile, strategy_seed=seed
    )
    mc.credibility = credibility
    return mc


def baseline_brain(role, seed):
    """Explicit baseline brain (baseline tests/tournaments only)."""
    rng = make_rng(seed)
    return PoliceGreedyBrain(rng) if role == "police" else ThiefDistanceBrain(rng)


def make_gameplay_brain(
    role, seed, horizon=DEFAULT_HORIZON, profile=None, credibility=0.5, baseline=False
):
    """The one entry production paths call: adaptive by default, baseline on request.

    When OPENAI_ADVISOR is enabled the OpenAI-primary brain wraps the deterministic
    engine (candidate generation + hard safety + fallback); it degrades to pure
    deterministic play whenever the key/API is unavailable."""
    if baseline:
        return baseline_brain(role, seed)
    chosen = police_specialist(seed, horizon) if role == "police" else thief_specialist(seed, horizon)
    if chosen is not None:
        return chosen
    policy = advisor_policy()
    if policy is not None:
        from .ai_brain import AIPrimaryBrain

        return AIPrimaryBrain(role, make_rng(seed), horizon=horizon, policy=policy, seed=seed)
    return default_police(seed, horizon) if role == "police" else default_thief(seed, horizon)
