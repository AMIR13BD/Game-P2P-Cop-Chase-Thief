# Self-play & scenario-diverse evaluation method

Two harnesses, both deterministic, no cross-repo file copying:

1. `sim/selfplay.py` — faithful frozen-baseline A/B in one process. `BaselineMeta`
   re-declares the frozen selection verbatim; proven identical to a git worktree at the
   baseline commit (per-seed). Used for faithfulness + unit sanity.

2. `sim/scenarios.py` + `sim/varied.py` — **the primary, corrected evaluation.** Generates
   distinct contract-valid scenarios (varied grid/starts/distance/budget/limit; same-cell
   starts rejected), runs ONE deterministic sub-game per scenario (N scenarios = N distinct
   games, not one game repeated under N seeds), and reports rate, unique-trajectory count,
   per-scenario success vector (for paired CIs), board/distance subgroups, latency,
   technical/illegal/timeout counts, and Police barrier metrics measured from the exact
   observation the engine feeds. `sim/stats.py` gives bootstrap rate/paired-difference CIs.

Brains are constructed with `horizon = scenario move limit` (as production does). Both
baseline and candidate receive identical scenarios (paired). Reproducible from the seeds.
