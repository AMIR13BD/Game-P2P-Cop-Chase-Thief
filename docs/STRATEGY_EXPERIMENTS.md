# Experiment log

Dev seeds (diagnosis/tuning): 1–300, 500–649. Held-out (final only): 20000–20499,
20000–20299 (D), 21000–21299 (subgroup). Held-out never used during tuning.

## Accepted
- **P1 Police barrier-first.** Weakness: controller reaches 8% though pure barrier = 60.5%.
  Change: `_police_choice` returns `barrier` whenever a target exists and budget remains.
  Dev (300 seeds): grid5 0.7%->58%, grid7 6.3%->57%, grid9 4.7%->40%. Kept.
- **T1 Thief escape-default.** Weakness: controller 94% (47% vs barrier Police) though pure
  escape/evade = 100%. Change: `_thief_choice` defaults to `escape`, keeps `evade` on
  articulation cells / barrier-heavy opponents, drops endgame-near-limit. Kept.

## Rejected
- **P2 barrier-first + endgame capture-dash near limit (V2).** Hypothesis: a final dash
  raises capture. Result: 52.3% < 56.7% (V1). Reverted — hoarding the dash loses tempo.
- (Considered, not pursued) belief-peak "sharpening": secondary effect; barrier-first gain
  dominated and adding it risked complexity without measured benefit. Left for future work.
