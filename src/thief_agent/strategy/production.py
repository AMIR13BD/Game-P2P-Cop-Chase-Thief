"""Production brain factory (single source of truth for real gameplay).

Default local/network gameplay uses the adaptive MetaController for BOTH roles,
deterministic under a fixed seed (no random exploration in production), preserving
the existing legality firewall + fallback and any audited opponent profile/credibility.
Baseline brains stay available for explicit baseline tests/tournaments only."""

from .meta import MetaController
from .police_greedy import PoliceGreedyBrain
from .rng import make_rng
from .thief_distance import ThiefDistanceBrain

DEFAULT_HORIZON = 35


def production_brain(role, seed, horizon=DEFAULT_HORIZON, profile=None, credibility=0.5):
    """Adaptive MetaController for `role`, deterministic and firewall-guarded."""
    mc = MetaController(role, make_rng(seed), horizon=horizon, epsilon=0.0, profile=profile)
    mc.credibility = credibility
    return mc


def baseline_brain(role, seed):
    """Explicit baseline brain (baseline tests/tournaments only)."""
    rng = make_rng(seed)
    return PoliceGreedyBrain(rng) if role == "police" else ThiefDistanceBrain(rng)


def make_gameplay_brain(
    role, seed, horizon=DEFAULT_HORIZON, profile=None, credibility=0.5, baseline=False
):
    """The one entry production paths call: adaptive by default, baseline on request."""
    if baseline:
        return baseline_brain(role, seed)
    return production_brain(role, seed, horizon, profile, credibility)
