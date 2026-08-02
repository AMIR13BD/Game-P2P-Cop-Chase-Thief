# Ablation (scenario-diverse)

Each accepted change affects one role; a matchup exercises one role, so the Police matchup
isolates the Police change and the Thief matchup isolates the Thief change (no in-game
cross-feature interaction). Paired held-out (600 scenarios):

| Feature | Metric | Baseline | +feature | Paired Δ [CI] |
|---|---|---|---|---|
| Police barrier-first | capture | 0.232 | 0.487 | +0.255 [0.210,0.302] |
| Thief escape-default | survival | 0.768 | 0.915 | +0.147 [0.117,0.178] |

Per board: both features help on every grid (see STRATEGY_EVALUATION.md). Interaction
(cand-vs-cand): Police 0.167 capture, Thief 0.833 survival. Each feature is minimal
(selection-only) and independently beneficial; no redundant feature added.
