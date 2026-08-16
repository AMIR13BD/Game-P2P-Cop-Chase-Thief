# PRD — Stigmergic scent field (the observation model)

*Per-mechanism PRD required by the software guidelines §2.3. Documents
[`domain/smell.py`](../src/thief_agent/domain/smell.py).*

---

## 1. Description and theoretical background

Neither agent can see the other. The only channel that carries positional information is a
**pheromone field**: each agent deposits a fixed radial kernel around itself every turn,
the field decays, and the opponent perceives the result. This is **stigmergy** — indirect
coordination through traces left in a shared environment, as in ant-colony trail
formation — repurposed here as an adversarial sensor.

The kernel is fixed by the rulebook (Appendix F / Fig. 4) and is a 5×5 radial stencil keyed
by absolute offset from the emitter:

| ∣Δrow∣,∣Δcol∣ | 0,0 | 0,1 · 1,0 | 1,1 | 0,2 · 2,0 | 1,2 · 2,1 | 2,2 |
|---|---:|---:|---:|---:|---:|---:|
| deposit | 0.90 | 0.62 | 0.42 | 0.20 | 0.14 | 0.04 |

Two update rules are implemented, and the distinction is strategically load-bearing:

**`step_update` — additive, saturating (the field we emit and the one gameplay uses).**

```
τ_next(c) = min(0.9, max(0, (1 − ρ)·τ(c) + δ(c)))        ρ = pheromone_decay = 0.10
```

**`compat_update` — max-merge (emit-only, league interop).**

```
τ_next(c) = min(0.9, max((1 − ρ)·τ(c), δ(c)))
```

The difference matters. Max-merge keeps the emitter's *current* cell as the unique 0.9
peak — only the centre deposit is 0.9, neighbours are ≤0.62, and any previous centre has
decayed to ≤0.81 — which hands an adversary a perfect localiser. The additive rule
saturates a whole neighbourhood at the ceiling instead, producing a plateau.

**We deliberately emit the additive field.** Being legally hard to localise is a strategic
choice, not an accident (`peer/net_engine.py`, `emission="spec"`). The cost is that our own
belief must cope with the same plateau — which is exactly why the Bayes filter in
[`PRD_belief_map.md`](PRD_belief_map.md) exists.

## 2. Requirements, expected input/output, performance metrics

| # | Requirement |
|---|---|
| R1 | Deposit the exact rulebook kernel, edge-clipped to in-bounds cells |
| R2 | Decay multiplicatively by `(1 − ρ)` each turn |
| R3 | Clamp intensity at `MAX_INTENSITY = 0.9` |
| R4 | Never produce negative intensity |
| R5 | Drop negligible traces (`< 1e-9`) so the grid stays sparse |
| R6 | Be byte-reproducible so both peers can audit the same field |

**Input** — current grid `{cell: intensity}`, emitter cell, `Board` (for bounds and
barriers), decay ρ.
**Output** — a new grid; the functions are pure and return new dictionaries rather than
mutating.

**Parameters** — `pheromone_center_intensity = 0.9`, `pheromone_decay = 0.10`,
`pheromone_grid_size = 5`. All three are **signed match terms**; they come from
configuration and may never be hardcoded or weakened locally.

**Performance metrics** — localisation error induced in an adversary; time-to-saturation;
grid sparsity (live cells per turn).

## 3. Constraints, limitations, alternatives considered

**Constraints.** The kernel, ρ, centre intensity and grid size are fixed by the signed
agreement — they are three of the 14 terms both peers sign, so a unilateral change would
break the config hash and the match. Edge clipping means corner emitters deposit less total
mass than centre emitters, which is inherent to the rulebook stencil.

**Limitations.**
- The additive field saturates: after enough turns in one region, intensity is uninformative
  there. Measured consequence — in a full 35-step sub-game the field can reach a state where
  a normalised posterior is nearly uniform.
- Because the field is public and symmetric, any information advantage is transient.

**Alternatives considered**

| Alternative | Why rejected |
|---|---|
| Emit the max-merge field | Simpler and it *helps a reference-style Cop localise us* — precisely why we do not emit it. Implemented (`compat_update`) strictly for interop compatibility, never for our own belief or strategy |
| Larger ρ (faster decay) | Would sharpen our own sensing but equally sharpen the opponent's; ρ is a signed term and not ours to change |
| Not emitting at all | Not legal — emission is mandated by the rules |
| Gaussian kernel | Not the rulebook stencil; would break byte-level auditability with the peer |

## 4. Success criteria and test scenarios

**Success criteria**
- S1 Kernel values match the rulebook table exactly at every offset.
- S2 Intensity never exceeds 0.9 nor drops below 0.
- S3 Edge and corner emitters clip without error.
- S4 Repeated emission at one cell saturates rather than overflowing.
- S5 `compat_update` preserves a unique centre peak; `step_update` does not.

**Test scenarios**

| Scenario | Test |
|---|---|
| Kernel shape, clipping, decay, clamp | `tests/unit/test_scent_kernel.py` (domain suite) |
| Interop scent-compatibility semantics | `tests/unit/test_interop_scent_compat.py` |
| Belief behaviour on a saturated field | `tests/unit/test_belief_firewall.py` |
| Real perceived field rebuilt from recorded tracks | `tests/unit/test_gui_tk_layer.py` |

**Reproduction.** The GUI's belief screenshot is produced by replaying a real match's
recorded positions through this exact kernel
([`gui/evidence.py`](../src/thief_agent/gui/evidence.py)) — the same function gameplay
uses, so the picture is the field an agent genuinely perceived.
