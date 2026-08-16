# PRD — `AntiSqueezeBrain` (topology-first Thief)

*Per-mechanism PRD required by the software guidelines §2.3. Documents the implementation
in [`strategy/thief_antisqueeze.py`](../src/thief_agent/strategy/thief_antisqueeze.py).*

---

## 1. Description and theoretical background

`AntiSqueezeBrain` is the Thief used in the counted match G020. Its thesis is that on this
board the Thief does not lose a **chase** — it loses a **topology**.

The naive evader maximises Manhattan distance from the estimated Cop. Measured against the
Orcai-MJ Cop, *every* loss of the distance-first evader was barrier-driven, never a chase:
either a Rule-46 pounce (a wall dropped onto our cell by an adjacent Cop) or a Rule-47
enclosure (a wall leaving us no legal move). Maximising distance walks the Thief to the
board edge, where the reachable component is small and a single wall completes the seal.

The correct objective is therefore not distance but the **shape of the space retained**.
This is graph-theoretic rather than metric: what matters is the size of the reachable
component, its resilience to one adversarial edge deletion, and the number of
vertex-disjoint escape routes — the intuition behind Menger's theorem, where connectivity
between a vertex and a frontier is bounded by the number of disjoint paths, so an evader
with several disjoint routes cannot be severed by one cut.

Distance is demoted to a tie-break. It is retained as a hard *constraint* (never step
adjacent to a possible Cop) but removed as the *objective*.

## 2. Requirements, expected input/output, performance metrics

**Functional requirements**

| # | Requirement |
|---|---|
| R1 | Choose a legal Thief action from an `Observation` alone |
| R2 | Never step onto a cell the Cop may occupy |
| R3 | Never end within one step of any plausible Cop cell (exactly pounce range) |
| R4 | Never accept a cell whose component one further wall could collapse |
| R5 | Among survivors, maximise worst-case reachable area after the Cop's best single wall |
| R6 | Deny the opponent's stall detector the repeated position pair that unlocks its squeeze |
| R7 | Be deterministic under a fixed seed |

**Hard-constraint tiers** — applied in order, each tier active only while a legal move
survives it. R2 → R3 → R4. If a tier would eliminate every option, it is relaxed rather
than producing an illegal move.

**Objective over survivors** (in the implemented order): worst-case reachable area after
the Cop's best single wall; current area with the Cop blocked; safe exits;
vertex-disjoint routes to the frontier; open degree; corner clearance while the Cop still
holds walls; anti-loop history; then Manhattan distance as tie-break.

**Input / Output** — as for the Cop: an `Observation` in, a firewall-clean `Action` out.
The Cop's cell is *estimated* by `CopLocator` from the public scent field and the public
Barrier Law, never observed.

**Performance metrics** — survival rate to the 35-step horizon; steps survived; number of
turns spent inside pounce range (target: zero); decision latency p95.

## 3. Constraints, limitations, alternatives considered

**Constraints.** The Thief may not place barriers (Cop privilege; the firewall degrades an
illegal Thief barrier to `STAY`). Movement is orthogonal + `STAY`. The Thief must survive
35 steps to win.

**Limitations.**
- Cop localisation is an estimate. On a saturated scent field the estimate widens, which
  makes the constraint tiers conservative and can cost board area.
- The objective is greedy over one adversarial wall, not a full minimax over the Cop's
  remaining barrier budget; a multi-wall trap planned several turns ahead is not modelled.

**Alternatives considered**

| Alternative | Why rejected |
|---|---|
| Maximise Manhattan distance | The measured failure mode — walks into the edge and dies to one wall |
| Random walk / mixed strategy | Unpredictable to the Cop, but also gives up the disjoint-route structure that actually prevents sealing |
| Full minimax over the Cop's barrier budget | Exponential in remaining walls; cannot meet the per-move latency budget |
| Sharper Cop estimate alone | Explicitly counter-productive: fed to a distance-first policy, a better estimate merely sharpens the flight into the corner. Fixing the *objective* is what makes the better estimate safe to use |

## 4. Success criteria and test scenarios

**Success criteria**
- S1 Survive the full horizon against the modelled squeeze Cop.
- S2 Zero turns ending within pounce range while a non-pounce option exists.
- S3 Zero illegal actions; an attempted Thief barrier degrades to `STAY`.
- S4 Deterministic under fixed seed.

**Test scenarios**

| Scenario | Test |
|---|---|
| Anti-squeeze objective and tier ordering | `tests/unit/test_orcai_brains.py` |
| Counter-strategy end-to-end selection | `tests/unit/test_orcai_counter.py` |
| Thief barrier illegal ⇒ degraded to STAY | `tests/unit/test_belief_firewall.py` |
| Herding / decorner regression | `tests/unit/test_board_rules.py`, `docs/STRATEGY_ABLATION.md` |
| Determinism | `tests/integration/test_determinism.py` |

**Empirical result.** In counted match **G020 vs `Orcai-MJ`**, this Thief survived the full
35 steps in all three sub-games it defended (README §7.1).
