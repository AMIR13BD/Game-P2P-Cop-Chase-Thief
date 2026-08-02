# Police strategy improvements (corrected evidence)

**Change (selection-only, `MetaController._police_choice`):** prefer `barrier` containment
whenever a belief target exists and budget remains; fall back to frozen hybrid/herd/intercept
when exhausted. `BarrierBrain` places only value-positive cuts, rejects self-obstruction and
negative-gain cells, and falls back to pursuit/capture otherwise.

**Scenario-diverse evidence (600 distinct scenarios, paired):**
capture 0.232 [0.197,0.268] -> **0.487 [0.450,0.527]**, paired Δ **+0.255 [0.210,0.302]**.
Improves on **every** board (7/9/11/13) and **every** tested opponent (greedy .14->.55,
random .69->.86, shortest .14->.24, mobility .09->.47, corner_trap .46->.71,
barrier_heavy .14->.24, deceptive .46->.71, custom-reference .12->.61) — **no observed
regression**. Barrier instrumentation: 6.0 barriers/game, useful_rate **1.0**,
zero/negative **0**, self-obstruction **0**, total reachable-area reduction 12,779,
capture-via-barrier-action 133, avg budget remaining 15. 0 technical/illegal; p95 <=2.85 ms.

POLICE STRATEGY: PROVEN STRONGER.
