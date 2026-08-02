# Thief strategy improvements (corrected evidence)

**Change (selection-only, `MetaController._thief_choice`):** default to `escape`
(distance + mobility + vertex-disjoint routes), keep `evade` on articulation cells and vs
barrier-heavy opponents, drop the frozen `endgame`/`entropy` picks.

**Scenario-diverse evidence (600 distinct scenarios, paired):**
survival 0.768 [0.733,0.803] -> **0.915 [0.892,0.937]**, paired Δ **+0.147 [0.117,0.178]**.
Improves on **every** board (7/9/11/13). Vs the strong candidate Police it survives **0.833**
(NOT 100% — the earlier claim was an artifact of one repeated scenario).

**Known regression (rule 27, requires user approval):** vs the `corner_trap` opponent
survival drops **0.20 -> 0.04** — escape-default (maximise distance) is herded into corners.
Everywhere else it improves or ties (7/8 opponents). Recommended follow-up (NOT applied here,
per "do not change strategies yet"): re-enable `evade`/anti-herding when a corner-trapping
pattern is detected.

THIEF STRATEGY: PROVEN STRONGER on the primary paired axis, with the corner_trap caveat above.
