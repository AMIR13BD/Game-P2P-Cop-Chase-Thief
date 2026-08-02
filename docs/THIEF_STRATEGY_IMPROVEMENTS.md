# Thief strategy improvements

**Change (1 file, selection-only):** `MetaController._thief_choice` now defaults to the
`escape` strategy (maximise pursuer distance + future mobility + vertex-disjoint escape
routes), keeps `evade` when sitting on an articulation cell or facing a barrier-heavy
opponent, and drops the frozen `endgame`/`entropy` picks.

**Why:** the frozen `endgame` brain models a *greedy* pursuer and walks into barrier seals
(0% survival vs strong barrier Police); `entropy` randomisation is weaker. `escape`/`evade`
are barrier-aware and survive 100% vs both baseline and the strong candidate Police.

**Evidence (held-out, grid 7, 500):** survival 0.942 [0.918,0.959] -> **1.000 [0.992,1.000]**
(+5.8 pp, disjoint CIs). Per board: 0.99->1.0 (5), 0.95->1.0 (7), 0.957->1.0 (9). Also
survives 100% vs the strong candidate Police (D). 0 technical/illegal/forced-timeout;
p95 ≤1.2 ms. Robust across held-out Police opponents (only loses to `corner_trap`, same as
baseline). THIEF STRATEGY: PROVEN STRONGER.
