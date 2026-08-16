# PRD — `RingBreakerBrain` (opponent-adaptive Cop)

*Per-mechanism PRD required by the software guidelines §2.3. Documents the implementation
in [`strategy/police_ringbreak.py`](../src/thief_agent/strategy/police_ringbreak.py) as it
actually is; no planned or aspirational behaviour is described.*

---

## 1. Description and theoretical background

`RingBreakerBrain` is the Cop used in the counted match G020. It is an **opponent-model
exploitation** strategy rather than a search strategy.

The general Cop problem is pursuit under partial observation: the quarry's cell is hidden
and only a decayed pheromone field is visible, so the Cop must act on a belief
distribution (see [`PRD_belief_map.md`](PRD_belief_map.md)). That framing is necessary only
while the opponent's policy is unknown. The Orcai-MJ Thief is a **deterministic ring
runner**: its decision function reads only signals we ourselves emit — our scent field and
our publicly declared barriers. A deterministic function of known inputs is not a
distribution; it is computable.

`OrcaiThiefTracker` ([`strategy/orcai_track.py`](../src/thief_agent/strategy/orcai_track.py))
therefore *reproduces* the opponent's cell by running its decision rule forward, rather
than estimating it. This collapses the belief to a point mass and converts a search
problem into pursuit with perfect information — the classical distinction between
pursuit-evasion on a graph with imperfect information and simple cop-number pursuit, where
a cop that knows the robber's position on a cop-win graph captures in bounded time.

Three consequences drive the policy:

1. **Adjacency is capture.** The opponent's k-th move is already determined when we are
   asked to move in round k, so ending orthogonally adjacent to the modelled cell means we
   step onto it, and the frozen always-claim policy in `PeerHalf` declares it. No protocol
   change is involved.
2. **`STAY` can capture.** Their ring term outweighs their distance term, so they
   sometimes walk onto us. Holding position converts their own scoring error into a
   capture.
3. **Intercept, don't trail.** We aim one ply ahead through their real rule (`peek`),
   cutting the ring rather than chasing around it.

Barriers are treated as a scarce tempo resource, not a primary weapon.

## 2. Requirements, expected input/output, performance metrics

**Functional requirements**

| # | Requirement |
|---|---|
| R1 | Choose a legal action for the Cop from an `Observation` alone — no privileged state |
| R2 | Model the ring-runner opponent exactly while the model agrees with observation |
| R3 | Detect model disagreement and hand over to the general-purpose Cop |
| R4 | Spend a barrier only when the chase has stalled **and** the wall strictly shrinks the opponent's reachable region |
| R5 | Be deterministic under a fixed seed |

**Input** — `Observation` (own cell, board size, public barriers, received scent, last
hint, step index, barrier quota). It structurally cannot contain the opponent's cell.

**Output** — `Action(kind="MOVE"|"STAY"|"BARRIER", direction=…)`, always passing the
firewall in [`strategy/firewall.py`](../src/thief_agent/strategy/firewall.py).

**Tuned constants** (in source, not hardcoded at call sites):

| Constant | Value | Meaning |
|---|---:|---|
| `CONFIDENCE_GATE` | 0.60 | Below this tracker agreement, defer to `ContainBayesBrain` |
| `STALL_WINDOW` | 6 | Rounds without progress before a wall is considered |
| `BARRIER_RESERVE` | 4 | Never drop below this many walls for a mere squeeze |

**Performance metrics** — capture rate; capture step count; decision latency p95 (must
stay far below the 30 s response timeout); fallback rate (fraction of decisions delegated).

## 3. Constraints, limitations, alternatives considered

**Constraints.** Move set is orthogonal + `STAY`; barriers are a Cop privilege capped at
14; the horizon is 35 steps; the Cop never sees the Thief's cell.

**Limitations — stated honestly.**
- The exploitation is only valid against the modelled policy. Against any other opponent
  the tracker's agreement score collapses and the brain becomes `ContainBayesBrain`; it
  can add captures but never subtract them.
- Measured OAT sensitivity ([`research/oat_sensitivity.csv`](research/oat_sensitivity.csv))
  shows the Cop's capture rate collapsing on grids of 11×11 and larger at the agreed
  35-step horizon. This is a genuine boundary of the strategy, not a defect of the
  implementation: the horizon is too short for the pursuit to close on a large board.

**Alternatives considered**

| Alternative | Why rejected |
|---|---|
| Pure greedy Manhattan pursuit | Chases the scent plateau; the additive, saturating field gives a ceiling of tied cells (see [`PRD_scent_stigmergy.md`](PRD_scent_stigmergy.md)) |
| Bayes filter only (`ContainBayesBrain`) | Correct but slower to close against a *known* deterministic policy; retained as the fallback rather than discarded |
| Aggressive early barrier spending | Loses tempo while still closing; walls are irreversible, so early spending forecloses later options |
| Simulating the opponent's whole game tree | Unnecessary — their rule is a function, so one-ply `peek` is exact and cheap |

## 4. Success criteria and test scenarios

**Success criteria**
- S1 Against the modelled ring runner, capture in every sub-game defended.
- S2 Against a non-modelled opponent, never perform worse than `ContainBayesBrain`.
- S3 Zero illegal actions and zero diagonal actions under all seeds.
- S4 Deterministic: identical seed ⇒ identical trajectory.

**Test scenarios** (all in the committed suite)

| Scenario | Test |
|---|---|
| Counter selects and captures the modelled policy | `tests/unit/test_orcai_counter.py` |
| Tracker agreement and model behaviour | `tests/unit/test_orcai_brains.py` |
| Firewall rejects illegal/diagonal actions | `tests/unit/test_belief_firewall.py` |
| Determinism under fixed seed | `tests/integration/test_determinism.py` |
| Barrier legality (R46/R47) | `tests/unit/test_board_rules.py` |

**Empirical result.** In counted match **G020 vs `Orcai-MJ`**, this Cop captured in all
three sub-games it pursued, at step 9 each time — contributing to the 6–0, 90 : 30 result
(README §7.1; logs under [`evidence/G020/`](evidence/G020/)).
