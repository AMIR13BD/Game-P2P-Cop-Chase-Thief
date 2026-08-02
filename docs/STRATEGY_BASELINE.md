# Strategy baseline (frozen)

Baseline commits (never modified): **Police `00de656`**, **Thief `ac8d585`** (branch
`master`). Production gameplay = `strategy.meta.MetaController` (deterministic, epsilon=0).

## Faithfulness
`sim/selfplay.BaselineMeta` re-declares the frozen selection verbatim and reproduces the
frozen master worktree **byte-identically per seed** (police 1–120, thief 1–100).

## Baseline results — scenario-diverse (600 distinct scenarios)
| Matchup | Metric | Rate | 95% CI |
|---|---|---|---|
| Baseline Police vs Baseline Thief | capture | 0.232 | [0.197, 0.268] |
| Baseline Thief vs Baseline Police | survival | 0.768 | [0.733, 0.803] |

(The earlier single-config figures — 0.058 capture / 0.942 survival — reflected ONE repeated
scenario and are superseded by these scenario-diverse numbers.)
