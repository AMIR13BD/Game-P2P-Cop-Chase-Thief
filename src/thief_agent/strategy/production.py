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
    policy = advisor_policy()
    if policy is not None:
        from .ai_brain import AIPrimaryBrain

        return AIPrimaryBrain(role, make_rng(seed), horizon=horizon, policy=policy, seed=seed)
    return production_brain(role, seed, horizon, profile, credibility)
