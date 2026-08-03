# Evaluation (scenario-diverse, corrected + trap fix)

## Method
600 distinct contract-valid scenarios (grids 7/9/11/13, varied starts/distance, budgets
14/20/28, move limits 35/45/60; same-cell starts rejected), paired baseline vs candidate,
bootstrap 95% CIs (`sim/{scenarios,varied,stats}.py`). corner_trap is a DIAGNOSTIC opponent;
fresh held-out trap opponents (`sim/opponents/trap.py`) validate generalisation and were not
tuned on.

## Thief candidate WITH the decorner trap fix (paired)
| Axis | Baseline | Old candidate | New candidate | 95% CI (new) |
|---|---|---|---|---|
| Primary survival (vs baseline Police) | 0.768 | 0.915 | **0.930** | [0.908, 0.950] |
| paired Δ vs baseline | – | – | +0.16 | [0.132, 0.190] |
| corner_trap (diagnostic) | 0.203 | 0.040 | **0.510** | – |
| cand-vs-cand survival | – | 0.833 | **0.865** | – |
| Police capture (UNCHANGED) | 0.232 | 0.487 | **0.487** | [0.450, 0.527] |

By grid (new thief survival): 7 .888, 9 .921, 11 .967, 13 .944 (all >= 0.888).

## Fresh held-out trap opponents (300 each; baseline / old / new)
edge_herder 0.34 / 0.967 / 0.96 ; choke_controller 0.967 / 0.98 / 0.98 ;
delayed_corner 0.15 / 0.003 / **0.38** ; seal_assist 0.69 / 0.72 / 0.77. No regression; the
corner-herding ones (delayed_corner) recover strongly -> the fix is general, not corner_trap-specific.

## Opponent matrix (old cand -> new cand)
greedy .93->.93, random .96->.938, shortest .93->.93, mobility .93->.945, corner_trap .04->.48,
barrier_heavy .99->.99, deceptive .902->.856, reference(custom adapter) .955->.965.
Regressions >0.02: `deceptive` (-0.046, significant) and `random` (-0.022, borderline) — the
intrinsic cost of corner escape vs randomised pursuers; flagged for review (survival stays 86%/94%).

## Safety
0 technical, 0 illegal, 0 timeouts; p95 <= 3.8 ms. Police strategy byte-unchanged.

## Verdicts
POLICE STRATEGY: PROVEN STRONGER — UNCHANGED.
THIEF STRATEGY: PROVEN STRONGER — TRAP REGRESSION RESOLVED (corner_trap 0.04->0.51 >= baseline
0.20; primary/cvc/fresh-held-out gates met), with a disclosed small deceptive/random trade.
