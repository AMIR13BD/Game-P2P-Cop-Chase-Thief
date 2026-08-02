# Ablation

The two accepted changes live in `MetaController.select`. Because each matchup exercises a
single role, matchup **B isolates the Police change** and **C isolates the Thief change**;
there is no cross-role interaction within one game, so B and C are clean single-feature
ablations. Held-out (grid 7, 500 games):

| Variant | Metric | Baseline | +feature | Delta |
|---|---|---|---|---|
| +Police barrier-first (B) | capture | 0.058 | 0.568 | +0.510 |
| +Thief escape-default (C) | survival | 0.942 | 1.000 | +0.058 |

Per-board (300 games each): Police capture grid5 0.017->0.583, grid7 0.043->0.477,
grid9 0.053->0.410; Thief survival grid5 0.99->1.0, grid7 0.95->1.0, grid9 0.957->1.0.
No board subgroup regresses. Both features are minimal (selection-only) and each is
independently beneficial; no redundant feature was added.
