# Strategy baseline (frozen)

Baseline commits (never modified): **Police `00de656`**, **Thief `ac8d585`**.
Both agents share a symmetric strategy layer; production gameplay uses
`strategy.meta.MetaController` (deterministic, epsilon=0, firewall-guarded) for both roles.

## Frozen behaviour (verified)
- Deterministic under a fixed seed: identical (outcome, steps, illegal) on repeated runs.
- `sim/selfplay.BaselineMeta` re-declares the frozen selection **verbatim** and reproduces
  the frozen master worktree **byte-identically per seed** (police seeds 1–120, thief 1–100).

## Baseline results (production MetaController vs itself)
| Matchup | N | Metric | Rate | 95% CI |
|---|---|---|---|---|
| Baseline Police vs Baseline Thief | 500 | capture | 0.058 | [0.041, 0.082] |
| Baseline Thief vs Baseline Police | 500 | survival | 0.942 | [0.918, 0.959] |

Mean steps-to-capture ≈ 27.9; 0 technical, 0 illegal, p95 decision ≤ 2.1 ms.
Interpretation: on an open board an equal-speed pursuer cannot close the gap, so the
baseline Police rarely captures (large headroom); the Thief is near the survival ceiling.
