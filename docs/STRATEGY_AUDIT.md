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

> NOTE: the percentages in this section are DEV DIAGNOSTICS on the fixed default board
> (grid 7, cop (0,0), thief (3,3)); they motivated the changes but are NOT the acceptance
> evidence. The scenario-diverse, paired numbers in STRATEGY_EVALUATION.md supersede them
> (e.g. "escape survives 100%" holds only on that one fixed config — see the corner_trap
> regression and the 0.833 cand-vs-cand survival in the corrected evaluation).

## Weaknesses (evidence-backed; dev diagnostics on the fixed default board)
- **The MetaController mis-selects.** Pure `BarrierBrain` captured **60.5%** vs the baseline
  Thief but the controller picked it rarely -> only **8%**. Pure `EscapeBrain`/`EvadeBrain`
  survived **100% on that fixed board** (not in general) but the controller reached only 94%
  (and 47% vs strong barrier play) because it defaults to `entropy` and switches to
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
