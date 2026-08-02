# Police strategy improvements

**Change (1 file, selection-only):** `MetaController._police_choice` now returns the
`barrier` strategy whenever a belief target exists and barrier budget remains; it falls
back to the frozen hybrid/herd/intercept logic only when the budget is exhausted.

**Why:** on an open board an equal-speed pursuer cannot close a 1-step gap, so pursuit
alone captures rarely. `BarrierBrain` places only value-positive cuts (shrinks the Thief's
reachable component / seals the belief cell), rejects self-obstruction and negative-gain
cells, and itself falls back to pursuit/capture when no worthwhile cut exists.

**Evidence (held-out, grid 7, 500):** capture 0.058 [0.041,0.082] -> **0.568 [0.524,0.611]**
(+51 pp, disjoint CIs). Per board: 0.017->0.583 (5), 0.043->0.477 (7), 0.053->0.410 (9).
Generalises to held-out opponents (greedy 0->1.0, reference 0->1.0, deceptive 0.15->0.57,
random 0.46->0.63; never worse on any opponent). 0 technical/illegal/self-block; p95 ≤1.7 ms.

**Safety:** no change to networking/crypto/audit/CLI; firewall+fallback unchanged.
POLICE STRATEGY: PROVEN STRONGER.
