# Thief strategy improvements (corrected + anti-herding trap fix)

## Base change (accepted earlier)
`MetaController._thief_choice` defaults to `escape` (distance + mobility + disjoint routes);
`evade` on articulation cells / barrier-heavy opponents. Scenario-diverse paired survival
0.768 -> 0.915.

## Trap fix (this task) — resolves the corner_trap regression
**Root cause (from failed trajectories):** `escape` maximises distance, which on an open
board means moving ALONG the low-degree boundary; an equal-speed herder (e.g. corner_trap)
pins the thief in a corner (traced: thief (0,3)->(0,4)->..->(0,6)->..->(6,6), captured).

**Smallest general fix (topology-only, no opponent name/position/seed/map):** add one
selection branch — if the board has **no barriers** AND the thief's cell has **legal-degree
<= 2** (a corner on an open board), select the new **`decorner`** brain
(`strategy/thief_decorner.DecornerBrain`): EvadeBrain's safety terms with **legal-degree
ranked above distance**, so it climbs OUT of the corner instead of fleeing deeper. The
existing `EvadeBrain` (and the frozen baseline that delegates to it) is left byte-unchanged.

**Results (paired, scenario-diverse):**
- corner_trap survival: baseline 0.203, old candidate 0.040 -> **new 0.510** (gate >=0.20 met).
- primary survival: 0.915 -> **0.930** (>=0.90; +0.015).
- cand-vs-cand survival: 0.833 -> **0.865** (>=0.80).
- Fresh HELD-OUT trap opponents (created after selection): delayed_corner 0.003->**0.38**
  (generalises!), edge_herder 0.967->0.96, choke_controller 0.98->0.98, seal_assist 0.72->0.77.
- 0 technical/illegal/timeouts; p95 <= 3.8 ms.

**Honest trade (flagged for review):** vs the two RANDOMISED opponents the corner rule
causes a small survival dip (opponent matrix, 200 scenarios): `random` 0.97 -> 0.925
(-0.045) and `deceptive` 0.875 -> 0.835 (-0.040). This is the INTRINSIC cost of corner
escape: breaking a herd requires bold moves toward/past the pursuer, which is slightly
suboptimal vs an erratic pursuer (a "never step closer" variant removes the dip but also
removes the corner_trap fix, reverting it to 0.04). Survival vs both remains high
(~93% / ~84%) and every other opponent/board improves or ties.
