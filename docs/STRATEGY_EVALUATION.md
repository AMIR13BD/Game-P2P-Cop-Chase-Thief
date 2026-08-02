# Evaluation (scenario-diverse, corrected)

## Correction notice
The earlier evaluation ran "500 seeds" on ONE fixed configuration (grid 7, cop (0,0),
thief (3,3), default budget/limit). Because production agents are deterministic (epsilon=0),
different seeds produced the **same** trajectory, so that benchmark measured one scenario
repeatedly. It overstated results (Thief "100% survival"; "Police never regresses"). This
corrected benchmark uses genuinely distinct, contract-valid, **paired** scenarios.

## Method
`sim/scenarios.generate` + `sim/varied.evaluate`: **600 distinct scenarios** (seed 12345),
varying grid {7,9,11,13}, both start cells (distinct), spatial distance, barrier budget
{14,20,28} and move/survival limit {35,45,60} — all within Appendix F (grid>=7,
barriers>=14, moves>=35). Baseline and candidate receive the **same** scenario (paired);
95% CIs by bootstrap (rate) and paired bootstrap (difference). Unique trajectories: 568/600.

## Headline (paired, held-out)
| Side | Baseline [CI] | Candidate [CI] | Paired Δ [CI] |
|---|---|---|---|
| Police capture | 0.232 [0.197,0.268] | **0.487 [0.450,0.527]** | **+0.255 [0.210,0.302]** |
| Thief survival | 0.768 [0.733,0.803] | **0.915 [0.892,0.937]** | **+0.147 [0.117,0.178]** |

Paired-difference CIs exclude 0 → statistically significant; effect sizes large.

## By board size (grid) — no regression on any board
Police capture: 7 .355->.572, 9 .245->.550, 11 .176->.418, 13 .146->.403.
Thief survival: 7 .645->.855, 9 .755->.914, 11 .824->.954, 13 .854->.938.

## Candidate vs candidate (corrects the false "100%")
Cand Police vs Cand Thief: capture **0.167**; Thief survival vs Cand Police **0.833** (NOT 100%).

## Opponent matrix (200 varied scenarios; base->cand)
'reference' is a CUSTOM reference-baseline adapter in THIS repo — NOT the official
lecturer/reference implementation.

| opponent | set | police capture | thief survival |
|---|---|---|---|
| greedy | tuning | 0.14->0.55 | 0.91->0.93 |
| random | tuning | 0.69->0.86 | 0.94->0.97 |
| shortest | tuning | 0.14->0.24 | 0.91->0.93 |
| mobility | tuning | 0.09->0.47 | 0.92->0.93 |
| corner_trap | held_out | 0.46->0.71 | **0.20->0.04 (REGRESSION)** |
| barrier_heavy | held_out | 0.14->0.24 | 0.99->0.99 |
| deceptive | held_out | 0.46->0.71 | 0.86->0.88 |
| reference (custom) | held_out | 0.12->0.61 | 0.94->0.95 |

Police improves on **every** opponent (no regression). Thief improves/ties on 7/8 but
**regresses vs corner_trap** (escape-default is herded into corners) — a real subgroup
regression flagged for user approval (rule 27).

## Safety (all matchups)
0 technical, 0 illegal, 0 timeouts; decision p95 <= 2.85 ms.

## Verdicts (corrected)
POLICE STRATEGY: PROVEN STRONGER (broad, no regression).
THIEF STRATEGY: PROVEN STRONGER on the primary paired axis, WITH a corner_trap subgroup
regression requiring user approval; recommended follow-up: restore `evade` against
corner-herding opponents (not done here — "do not change strategies yet").
