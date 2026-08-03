# Experiment log

Dev/tuning: corner_trap (300 @ seed 4242) used as DIAGNOSTIC only. Primary 600 @ 12345,
opponent matrix 200/500 @ 777, cand-vs-cand 600 @ 12345. Fresh held-out trap opponents
300 @ seeds 9001-9004, created AFTER candidate selection and not tuned on.

## Accepted (earlier)
- Police barrier-first `_police_choice` (+0.255 capture).
- Thief escape-default `_thief_choice` (+0.147 survival).

## Trap-fix experiments (this task)
Diagnosis: per-brain vs corner_trap — endgame 0.76, hybrid 0.27, entropy 0.16,
escape/evade/distance 0.03-0.04. Escape/evade get edge-herded into corners; endgame is
barrier-blind.

Tried and REJECTED:
- A. trap->EvadeBrain (unmodified): evade 0.03 vs corner_trap -> no help.
- B. no-barriers->endgame: corner_trap 0.76 but primary 0.80 (<0.90) and cvc 0.70 (<0.80)
  (endgame barrier-blind, punished by the barrier Police early).
- B'. late-game (no-barrier) endgame window K=6..20: primary/cvc fine but corner_trap only
  0.04-0.10 (thief already cornered by late game).
- escape-move-reduces-degree -> endgame (P2): primary 0.917, corner_trap 0.737, but cvc 0.578.
- threat-distance gate on decorner (K=2..4): fixes deceptive but corner_trap drops to 0.17.
- "pinned" gate: identical to no-gate (no discrimination).
- decorner "never step closer": deceptive fixed but corner_trap back to 0.04 (corner escape
  needs bold moves) -> rejected.

ACCEPTED (smallest passing): no-barriers AND legal-degree<=2 -> `decorner` (mobility-first
evade). Passes primary/corner_trap/cvc/fresh-held-out gates; small intrinsic deceptive/random
trade disclosed.

Evaluation-hygiene fix: reverted an earlier mistake where the degree term was added directly
to the shared EvadeBrain (it leaked into the frozen BaselineMeta and shifted Police capture
0.487->0.465). Moved to the new DecornerBrain; EvadeBrain/baseline restored (capture 0.4867).
