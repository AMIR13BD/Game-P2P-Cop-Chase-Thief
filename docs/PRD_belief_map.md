# PRD — Belief representation (posterior over the opponent's cell)

*Per-mechanism PRD required by the software guidelines §2.3. Documents
[`strategy/belief.py`](../src/thief_agent/strategy/belief.py) (`BeliefMap`) and
[`strategy/police_contain_bayes.py`](../src/thief_agent/strategy/police_contain_bayes.py)
(`ThiefBeliefFilter`).*

---

## 1. Description and theoretical background

The match is a two-agent **Dec-POMDP**: neither peer observes the world state, and each
must act on its own belief. The observation model is a decayed, saturating pheromone field
(see [`PRD_scent_stigmergy.md`](PRD_scent_stigmergy.md)), so the belief is a distribution
over the opponent's possible cells rather than a point.

Two layers are implemented, because one is not sufficient.

**Layer 1 — `BeliefMap` (normalised posterior).** The baseline. Every passable cell is
weighted by the received scent plus a small floor, barriers are excluded, and the result is
renormalised to a proper distribution:

```
w(c) = 0.01 + scent(c)        for every non-barrier cell c
b(c) = w(c) / Σ w             (uniform fallback when Σ w = 0)
```

The `0.01` floor is deliberate: it keeps every reachable cell strictly possible, so a
transient gap in the scent field cannot make the true cell probability-zero and
permanently unrecoverable. This is the same motivation as additive (Laplace) smoothing.

**Layer 2 — `ThiefBeliefFilter` (recursive Bayes filter).** `BeliefMap` alone fails on this
observation model, and the failure is instructive. Because emission is **additive and
clamped at 0.9**, an opponent that lingers pins an entire 5×5 neighbourhood at the ceiling;
the argmax then becomes a *plateau* and the Cop chases a ghost. The filter therefore
performs the standard two-step recursion:

* **Predict** — the opponent moved to one legal orthogonal neighbour or stayed, uniformly,
  respecting barriers. This is the motion model.
* **Update** — a kernel-shaped likelihood, so a cell scores well when it is hot *and* its
  surrounding ring is warm, which matches how the emission kernel actually deposits.

A hybrid rule then prefers a clear **fresh-emission delta** peak (evidence of a directed
mover) and falls back to the diffuse MAP estimate once the field has saturated.

## 2. Requirements, expected input/output, performance metrics

| # | Requirement |
|---|---|
| R1 | Produce a normalised distribution over passable cells |
| R2 | Assign zero mass to barrier cells |
| R3 | Never assign exactly zero to a reachable non-barrier cell (recoverability) |
| R4 | Degrade to uniform when there is no evidence, rather than failing |
| R5 | Respect barriers in the motion model |
| R6 | Be usable by the GUI without leaking the opponent's true cell |

**Input** — board size, barrier set, received scent grid `{cell: intensity}`.
**Output** — `dist: {cell: probability}`, with `argmax()` and `total()` accessors.

**Performance metrics** — localisation error (Manhattan distance from MAP estimate to the
true cell, measurable in self-play where both tracks are known); fraction of turns where
the MAP is a plateau; update latency.

## 3. Constraints, limitations, alternatives considered

**Constraints.** Only legally visible data may enter: the `Observation` structurally cannot
contain an opponent coordinate. The belief must be computable within the per-move latency
budget on a 7×7 to 13×13 grid.

**Limitations.**
- Under a saturated field the posterior is close to uniform and carries little
  information. This is a property of the *observation model*, not a bug — and it is
  exploited defensively: we deliberately emit the saturating additive field so that an
  adversary localising us faces the same wall (see `PRD_scent_stigmergy.md` §3).
- The motion model is uniform over legal neighbours; it does not model an intelligent
  evader's preference. Where the opponent's policy *is* known and deterministic, the
  belief is bypassed entirely by an exact tracker
  ([`PRD_ringbreaker.md`](PRD_ringbreaker.md)).

**Alternatives considered**

| Alternative | Why rejected / where used |
|---|---|
| Raw argmax over scent | Fails on the saturation plateau — the original measured defect |
| Particle filter | No benefit on ≤169 discrete cells; exact enumeration is cheaper and deterministic |
| Kalman filter | Assumes continuous state and Gaussian noise; the domain is a discrete grid with hard barrier constraints |
| No floor (pure normalisation) | A momentary zero makes the true cell unrecoverable forever |
| Exact opponent model | Strictly better *when the opponent is known*; used in `RingBreakerBrain`, with the belief filter retained as the general-purpose fallback |

## 4. Success criteria and test scenarios

**Success criteria**
- S1 `Σ b(c) = 1` for every non-degenerate input.
- S2 `b(c) = 0` for every barrier cell.
- S3 Empty evidence ⇒ uniform distribution, no exception.
- S4 A single fresh emission ⇒ MAP at the emitting cell.
- S5 The GUI heatmap built from this belief never reveals the opponent's true cell.

**Test scenarios**

| Scenario | Test |
|---|---|
| Normalisation, barrier exclusion, uniform fallback | `tests/unit/test_belief_firewall.py` |
| Bucketing and peak identification for the GUI | `tests/unit/test_gui_tk_layer.py` |
| Hidden-position guarantee (exactly one marker drawn) | `tests/unit/test_gui.py`, `test_gui_tk_layer.py` |
| Reconstruction of a real perceived field from recorded evidence | `tests/unit/test_gui_tk_layer.py` |
| Bayes-filter localisation | `tests/unit/test_orcai_brains.py` |

**Empirical artefact.** The committed screenshot
[`images/thief-gui-belief-map.png`](images/thief-gui-belief-map.png) is this posterior
rendered live from a real recorded match — the 0-9 buckets are `b(c)` normalised against
the peak.
