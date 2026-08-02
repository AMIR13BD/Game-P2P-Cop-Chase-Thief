# Evaluation (held-out)

Candidates evaluated **independently vs the untouched frozen baseline** (rule 17).
Held-out seeds (never tuned on): 20000–20499 (B/C, 500), 20000–20299 (D, 300),
21000–21299 (subgroup, 300). Wilson 95% CIs.

## Grid 7 (default)
| Matchup | N | Metric | Baseline [CI] | Candidate [CI] | Δ |
|---|---|---|---|---|---|
| Cand Police vs Base Thief | 500 | capture | 0.058 [0.041,0.082] | **0.568 [0.524,0.611]** | +0.510 |
| Cand Thief vs Base Police | 500 | survival | 0.942 [0.918,0.959] | **1.000 [0.992,1.000]** | +0.058 |
| Cand Police vs Cand Thief | 300 | capture | – | 0.000 [0.000,0.013] | – |
| Cand Thief vs Cand Police | 300 | survival | – | 1.000 [0.987,1.000] | – |

CIs are disjoint from baseline for both headline results -> statistically significant, and
the effect sizes are large (practically significant).

## Safety metrics (all matchups)
technical 0.0, illegal 0, fallback 0.0, timeouts 0; decision p95 ≤ 2.1 ms (budget seconds).
No self-blocking (barrier planner rejects self-obstruction by construction).

## Subgroup protection
Every board (5/7/9) improves on both metrics; no meaningful regression on any subgroup.

## Verdicts
POLICE STRATEGY: PROVEN STRONGER.  THIEF STRATEGY: PROVEN STRONGER.
