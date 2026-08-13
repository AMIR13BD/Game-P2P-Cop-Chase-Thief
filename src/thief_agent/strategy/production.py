"""Production brain factory (single source of truth for real gameplay).

Default local/network gameplay uses the adaptive MetaController for BOTH roles,
deterministic under a fixed seed (no random exploration in production), preserving
the existing legality firewall + fallback and any audited opponent profile/credibility.
Baseline brains stay available for explicit baseline tests/tournaments only."""

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
    """Optional SPECIALISED police strategy from POLICE_STRATEGY (robust default = None).

    `contain` selects ContainBrain (shortest-path + Chebyshev edge-cornering + value-gated
    barriers). Measured to capture the current uoh-ay26 thief far more (~0.47 -> ~0.79) and
    to score >= the portfolio in the exact six-game series, but it is LESS robust vs pure
    corner-hugging evaders, so it is a per-match opt-in, never the default (avoids overfit)."""
    strat = os.environ.get("POLICE_STRATEGY", "").strip().lower()
    if strat == "contain":
        from .police_contain import ContainBrain

        return ContainBrain(make_rng(seed), horizon=horizon, seed=seed)
    if strat == "contain_bayes":  # EXPERIMENTAL: ContainBrain chase + Bayesian localisation
        from .police_contain_bayes import ContainBayesBrain

        return ContainBayesBrain(make_rng(seed), horizon=horizon, seed=seed)
    return None


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
    if role == "police":
        specialist = police_specialist(seed, horizon)
        if specialist is not None:
            return specialist
    policy = advisor_policy()
    if policy is not None:
        from .ai_brain import AIPrimaryBrain

        return AIPrimaryBrain(role, make_rng(seed), horizon=horizon, policy=policy, seed=seed)
    return production_brain(role, seed, horizon, profile, credibility)
