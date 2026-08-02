# Strategy audit (Phase 1)

## Architecture
- Entry: `strategy.production.make_gameplay_brain` -> `MetaController` (both roles).
- Selection: `MetaController.select` -> `_police_choice` / `_thief_choice` pick ONE whole
  brain from `strategy.registry` per turn; `firewall.enforce` guarantees legality; a
  guaranteed legal `fallback.safe_fallback` exists.
- Belief: `belief.BeliefMap` normalises received **scent** (opponent pheromone), `argmax`
  = estimated opponent cell. Police also uses audited-credible hints (`hints.biased_target`).
- Building blocks: `graph` (BFS/components/reachable area), `connectivity` (articulation
  points/bridges), `disjoint` (vertex-disjoint paths via max-flow), `predict`, `pathing`,
  `search` (anytime/iterative-deepening with wall-clock deadline), `profiling` (audited
  opponent model). Police brains: greedy/intercept/**barrier**/herd/hybrid. Thief brains:
  distance/**escape**/**evade**/entropy/endgame/hybrid.
- Barriers are placed **adjacent to the placer** (`rules.legal_barrier_targets`), budget
  `max_barriers=14`; `police_barrier.best_barrier` skips self-obstruction and negative-gain
  cells (tempo cost). Timeouts: per-turn budget seconds; searches deadline-bounded.

## Strengths
Rich, correct primitives; deterministic; firewall + fallback; audited-only profiling;
bounded search; barrier planner already avoids self-blocking and wasted (negative) cuts.

## Weaknesses (evidence-backed)
- **The MetaController mis-selects.** Pure `BarrierBrain` captures **60.5%** vs the baseline
  Thief but the controller picks it rarely -> only **8%**. Pure `EscapeBrain`/`EvadeBrain`
  survive **100%** (even vs the strong barrier Police) but the controller reaches only 94%
  (and just 47% vs strong barrier play) because it defaults to `entropy` and switches to
  `endgame` near the limit — `endgame` models a *greedy* pursuer and walks into barrier
  seals (0% vs barrier Police).
- Belief `argmax` saturates at 0.9 across recent trail cells (tie-break by coordinate) —
  a secondary, smaller inaccuracy.

## Highest-value hypotheses
- Police: **prefer barrier containment** whenever budget remains (H-P1).
- Thief: **default to escape** (distance+mobility+disjoint routes), keep evade on
  articulation/barrier-heavy opponents; drop the harmful endgame-near-limit switch (H-T1).

## Files likely to change / risk
`strategy/meta.py` (selection only) — low risk, no protocol/crypto/network touched; brains
unchanged. Risk: over-committing barriers could self-block — mitigated because `best_barrier`
already rejects self-obstruction and negative-gain cuts.
