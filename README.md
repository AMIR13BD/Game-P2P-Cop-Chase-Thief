# Thief Agent — Academic Report

**Distributed Cops-and-Robbers over a Peer-to-Peer Network** — University of Haifa,
Department of Computer Science, *Orchestration of AI Agents*, final project 2026.

| | |
|---|---|
| **Group ID** | `amireman` |
| **Members** | Amir Fadila, Eman Sarhan |
| **This repository** | **Thief agent** (package `thief_agent`) |
| **Companion repository** | **[Police agent → Game-P2P-Cop-Chase-Police](https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police)** |
| **Natural role** | THIEF (the agent implements *both* roles for six-sub-game alternation) |

> This file is the academic report required by §9.4.2 and Appendix C.2 of the rulebook.
> It is a scientific document — the design decisions, their justification, and the
> empirical evidence — not an installation guide. Operational instructions are kept
> short here and expanded in [`docs/OPERATIONS.md`](docs/OPERATIONS.md).

---

## Table of contents

1. [The Dec-POMDP model](#1-the-dec-pomdp-model)
2. [FastMCP orchestration dilemmas](#2-fastmcp-orchestration-dilemmas)
3. [Strategies implemented](#3-strategies-implemented)
4. [Learning curves / reinforcement learning](#4-learning-curves--reinforcement-learning)
5. [Screenshots — Live GUI and Replay](#5-screenshots--live-gui-and-replay)
6. [Companion repository](#6-companion-repository)
7. [Empirical evidence](#7-empirical-evidence)
8. [Repository contents](#8-repository-contents)
9. [Security, secrets and integrity](#9-security-secrets-and-integrity)
10. [Reproducibility](#10-reproducibility)
11. [Submission checklist](#11-submission-checklist)

---

## 1. The Dec-POMDP model

*(Rulebook §9.4.2 item 1; formalism from Chapter 1.3.)*

The race is modelled as a two-agent, zero-sum **decentralised partially observable Markov
decision process**. Neither peer observes the world state; each maintains its own belief
and acts on it. With no referee and no shared memory the process is genuinely
decentralised, not a centralised POMDP with two actuators.

**⟨I, S, {Aᵢ}, T, Ω, O, R, h⟩ as implemented in this repository**

| Element | Implementation |
|---|---|
| **I** — agents | `{police, thief}`, symmetric peers ([`constants.py`](src/thief_agent/constants.py) `Role`) |
| **S** — state space | `(cop_cell, thief_cell, barriers, step)` over a 7×7 grid, cells `(row, col)` from a top-left origin. The barrier set makes \|S\| combinatorial, so the state is never enumerated — only the Thief's reachable component is, which is the quantity that actually decides survival ([`strategy/graph.py`](src/thief_agent/strategy/graph.py)) |
| **Aᵢ** — actions | Thief: `{N,S,E,W,STAY}` only. **The Thief may never place a barrier** — the Barrier Law is a Cop privilege, and [`strategy/firewall.py`](src/thief_agent/strategy/firewall.py) degrades any such proposal to `STAY` rather than emitting an illegal action |
| **T** — transition | Deterministic movement; barriers are irreversible. All stochasticity is the opponent's policy — precisely the unobservable part |
| **Ω** — observations | An `Observation` carries **only** legally visible data: own cell, board size, public barriers, the received scent field, the last verbal hint, step index, barrier quota ([`strategy/base.py`](src/thief_agent/strategy/base.py)). It structurally **cannot** contain a Cop coordinate |
| **O** — observation model | Stigmergic pheromones: a 5×5 kernel (0.90 / 0.62 / 0.42 / 0.20 / 0.14 / 0.04) deposited each turn, decayed by ρ = 0.1, clamped at 0.9 ([`domain/smell.py`](src/thief_agent/domain/smell.py)) — a noisy, additive, saturating sensor |
| **R** — reward | Survival to step 35: Thief 10 / Cop 5. Capture: Thief 5 / Cop 20. Tie 2, technical loss 0 ([`domain/scoring.py`](src/thief_agent/domain/scoring.py)) |
| **h** — horizon | 35 steps — for the Thief this is not a horizon but *the win condition itself* |

### What the Thief's belief must actually estimate

The Thief's inference problem is not symmetric to the Cop's, and treating it as if it were
was our most expensive early mistake. The Cop wants a point estimate to chase. The Thief
needs something stronger: **the set of cells from which the Cop could end the game on its
very next action.** Because a barrier turn does not move the Cop, and the Barrier Law lets
it wall its own cell or any of the four beside it, that set is the closed neighbourhood of
the Cop's true cell — so a merely *probable* estimate is not enough; a confidently wrong
one is fatal.

Two inference layers serve this:

* **[`strategy/belief.py`](src/thief_agent/strategy/belief.py) `BeliefMap`** — the baseline
  normalised posterior over passable cells with a small floor.
* **[`strategy/cop_locate.py`](src/thief_agent/strategy/cop_locate.py) `CopLocator`** — a
  maximum-likelihood tracker. One turn of the Cop's field is
  `τ ← (1−ρ)·min(cap, τ_prev + K(d))`, so given the *previous* broadcast we can predict the
  next one for every hypothetical Cop cell and keep the hypothesis with the smallest error.
  This beats a raw argmax (which saturates into a plateau of tied cells) and beats a plain
  delta peak (which collapses when the Cop stands still on an already-saturated cell). It is
  fused with an exact geometric constraint: **a freshly declared barrier confines the Cop to
  at most five cells**, because Rule 15 makes every wall public and the Barrier Law fixes
  where it may be placed. Measured on real games this locator is **100 % exact**.

  One subtlety cost us 19 % of localisation accuracy until it was found: the Cop may wall
  **the cell it is standing on** (`SELF`), so a barrier is *not* evidence of absence.
  Filtering barrier cells out of the hypothesis set silently discarded the true cell.

**Uncertainty as a resource** (Chapter 1.4). The asymmetry protects us too, and we spend
effort keeping it that way: we emit the *additive spec* scent field rather than a max-merged
one. A max-merge would leave our current cell as a unique 0.9 peak — a perfect localiser
handed to an adversarial Cop. Emitting the saturating field is a deliberate decision to stay
legally hard to localise ([`peer/net_engine.py`](src/thief_agent/peer/net_engine.py),
`emission="spec"`).

---

## 2. FastMCP orchestration dilemmas

*(Rulebook §9.4.2 item 2; Chapters 2 and 8.)*

Every peer is **simultaneously a server and a client** over FastMCP 3.4.5. There is no
central server: our MCP server *is* our public mailbox.

### 2.1 The four receive tools and why the surface is this small

[`interop/server.py`](src/thief_agent/interop/server.py) exposes exactly four tools —
`negotiate`, `receive_turn`, `submit_audit`, `receive_control` — with names and argument
names mirroring the reference exactly. Each drops its message into a thread-safe queue and
returns. **No tool blocks and no tool computes.** A handler that waited for our own turn
would deadlock the instant both peers waited on each other.

### 2.2 Turn management — the ordering dilemma, from the Thief's side

Implemented in [`interop/runtime.py`](src/thief_agent/interop/runtime.py):

* Rounds are **thief-first, then police** — as the Thief we *open* every sub-game, and we
  commit to a cell before seeing the Cop's reply to it.
* The Cop declares a capture claim on its own post-move cell **every** turn. We answer every
  claim truthfully; a false denial would be provable at the audit and would cost the match.
* We are caught iff the claim names our current cell, a declared barrier lands on our cell
  (R46), or a barrier leaves us with no legal move (R47)
  ([`peer/net_engine.py`](src/thief_agent/peer/net_engine.py) `receive`).
* **Stepping onto the Cop is not an auto-capture** — with no referee, capture exists only
  once declared and confirmed. We nevertheless treat co-location as fatal in the strategy,
  because relying on an opponent's failure to claim is not a defence.
* Once caught we seal a `HOLD` and make **no further move** — `concede()` in
  [`interop/engine.py`](src/thief_agent/interop/engine.py). A caught Thief that kept moving
  would be manufacturing an illegal history.
* On reaching step 35 we raise the **survival win-claim** ourselves; the sub-game ends on our
  own 35th move rather than waiting for the peer.

### 2.3 Network-failure handling

| Failure | Mechanism |
|---|---|
| Peer goes silent | [`peer/deadline.py`](src/thief_agent/peer/deadline.py) bounds every wait; a per-turn timeout classifies the sub-game, never hangs |
| Peer stalls mid-series | [`peer/watchdog.py`](src/thief_agent/peer/watchdog.py) heartbeats and forces a deterministic technical loss |
| Transport drop | [`interop/series.py`](src/thief_agent/interop/series.py) isolates the failure to **one sub-game** and reconnects; the series survives |
| Duplicate / reordered / replayed turns | `Inbox` (window 4) enforces exactly-once, in-step-order delivery and raises on equivocation |
| Malformed envelope | Rejected with a reason and a strike — nothing in the receive path may raise, because a crashed peer forfeits |
| Straggler audit after a role swap | Audits bucketed by explicit `sub_game_number`, never by arrival order |

### 2.4 Gatekeeper and Orchestrator

**Gatekeeper** ([`shared/gatekeeper.py`](src/thief_agent/shared/gatekeeper.py)) is the
protective layer between an autonomous agent and a live account: a **token-bucket** rate
limiter ([`shared/rate_limiter.py`](src/thief_agent/shared/rate_limiter.py)) plus a hard
admission capacity of `concurrent_requests + queue_depth`, raising `RateLimitError` /
`QueueFullError` instead of hammering an endpoint. It matters most on the outbound Gmail
path: a Google `429` is not a transient blip, and retrying blindly through it risks account
suspension — so we back off and wait for the next window.

**Orchestrator** — the layered state machine that owns the game, so strategy never touches
the wire:

```
SeriesRuntime      six sub-games, role alternation, consensus, reporting   interop/series.py
   └── SubGameRuntime   one sub-game: turn loop, deadline, mutual audit    interop/runtime.py
         └── SubEngine  wire ⇄ engine translation, capture round-trip      interop/engine.py
               └── PeerHalf   own secret state, sealing, scent, claims     peer/net_engine.py
                     └── Brain   pure decide(Observation) -> Action        strategy/
```

Separation of concerns (Chapter 8.2) is structural: a brain takes an `Observation` and
returns an `Action`, and **every** action passes
[`strategy/firewall.py`](src/thief_agent/strategy/firewall.py), which substitutes a safe
legal fallback for any illegal proposal and counts the substitution. A buggy or adversarial
strategy cannot put an illegal move on the wire.

---

## 3. Strategies implemented

*(Rulebook §9.4.2 item 3; Chapter 6. This is the Thief-side report — the companion
repository documents the same engine from the Cop's side.)*

The move is **always pure Python and always deterministic under a fixed seed.** A language
model never selects a move.

### 3.1 The Thief's problem — and why distance is the wrong objective

The obvious evader maximises Manhattan distance from the pursuer. It loses, and the
measurements say exactly how. Against the current league opponent's Cop, **every single
loss was barrier-driven** — their Rule-46 pounce (a wall dropped on our cell from an adjacent
Cop) or Rule-47 enclosure — and **not one** was a chase. Maximising distance walks straight
into the board edge, where a shrinking component and a one-wall seal finish the job.

The correct objective is therefore not separation but **the shape of the space we keep**.
Distance is demoted to a hard constraint; topology becomes the thing we optimise.

### 3.2 The portfolio

| Brain | Idea |
|---|---|
| `ThiefDistanceBrain` | Baseline: maximise distance from the belief argmax |
| `EscapeBrain` / `EvadeBrain` | Distance with mobility and escape-route awareness |
| `EntropyBrain` | Prefer moves that keep the pursuer's posterior diffuse |
| `DecornerBrain` | Explicit recovery away from corners |
| `EndgameBrain` | Guaranteed-survival play near the threshold |
| `SurvivorBrain` | Safety-constrained mobility with anti-oscillation history |
| **`AntiSqueezeBrain`** | **Current default** — survival-topology evasion (§3.3) |
| `MetaController` | Portfolio controller selecting a brain per turn |

### 3.3 `AntiSqueezeBrain` — optimising survival topology

[`strategy/thief_antisqueeze.py`](src/thief_agent/strategy/thief_antisqueeze.py).

**Hard constraints first**, each applied only while a legal move still survives it:

0. never step onto a cell the Cop may occupy;
1. never end **within one step** of any plausible Cop cell — exactly the pounce range, since
   a barrier turn does not move the Cop and it may wall its own cell or any of the four
   beside it;
2. never accept a cell whose component **one further wall** could collapse.

**Then the objective**, over whatever survives: the worst-case reachable area after the
Cop's best single wall (the anti-squeeze term, and the primary one), current area with the
Cop treated as blocked, the number of safe exits, vertex-disjoint routes to the frontier,
open degree, articulation-point avoidance, corner clearance while the Cop still holds walls,
and anti-loop history. Distance survives only as a tie-break.

The anti-loop term does double duty. Their Cop unlocks its squeeze behaviour only after its
stall detector sees a **repeated `(cop, thief)` position pair**; refusing to replay positions
denies it that trigger entirely.

Two findings were worth more than any coefficient:

* **Deleting the endgame branch.** The earlier evader switched, near step 35, to a
  distance-and-degree score that dropped the corner and `STAY` penalties. It then parked in
  a corner for the last six turns and was walled in. That branch was the *only* remaining
  loss mode once the pounce was closed; removing it took survival from 90 % to 100 %.
  Enclosure is exactly as fatal on step 34 as on step 4, so one objective now governs
  throughout.
* **Fix the objective before improving the sensor.** Feeding a sharper Cop estimate into the
  old distance-first policy made results *worse* — a better estimate simply sharpened the
  flight into the corner. The `CopLocator` of §1 only became an asset after the objective
  was corrected.

### 3.4 Exploiting an opponent's model of us

Their Cop searches for forced capture lines while simulating our replies with a *pure
max-distance flee* model. Because `AntiSqueezeBrain` is not that policy, their "forced"
lines are not forced — a modelling error we obtain for free simply by having the right
objective. The symmetric Cop-side counter is documented in the companion repository.

### 3.5 Verbal hints and the LLM boundary

Hints are free text ≤ 15 words, sanitised for digits, hex blobs and secret-like tokens
([`strategy/hint_filter.py`](src/thief_agent/strategy/hint_filter.py)), so a hint can never
leak a coordinate. Our hints are deliberately compass-free: a parseable direction — true or
false — is information an opponent's detector can exploit in either direction.

An optional OpenAI **advisor** (`gpt-5.4-mini`, [`advisor/`](src/thief_agent/advisor)) may
act as a *selector* over deterministic candidates: the engine generates the legal candidate
set and a fallback, the model picks an `action_id`, and the result passes strict validation,
a hard-safety veto and the firewall. It is **disabled by default** (`OPENAI_ADVISOR`), so
the test suite makes zero API calls and league play is fully deterministic.

---

## 4. Learning curves / reinforcement learning

*(Rulebook §9.4.2 item 4 — conditional on RL being used.)*

**No reinforcement learning is used, so no learning curves are reported.** The rulebook
lists Q-Learning as *one optional tool* (Chapter 6.3) and we deliberately declined it: a
35-step horizon over a combinatorial barrier state yields far too little on-policy data for
tabular Q-learning to converge, and an unconverged policy is strictly worse than a correct
deterministic one. Effort went instead into exact opponent modelling, maximum-likelihood
localisation and topological search — all reproducible and auditable, which an under-trained
policy is not.

The measured strategy comparison in §7 replaces a learning curve as empirical evidence; it
comes from a protocol-faithful harness rather than a training loop.

---

## 5. Screenshots — Live GUI and Replay

*(Rulebook §9.4.2 item 5 — **absolute requirement**; Chapter 7. The requirement is not
formal: the belief map demonstrates genuine probabilistic inference under partial
observation, and `VERIFIED OK` demonstrates that game integrity was cryptographically
preserved.)*

Both are real Tkinter windows. Everything they draw is computed by the same modules the
agent itself uses — the belief heatmap by `strategy/belief.py` and `domain/smell.py`, the
integrity verdict by `gui/replay_verify.py` — so the windows are a presentation layer, never
a second implementation. The images below are unretouched captures of those windows.

### 5.1 Live GUI — board and belief heatmap

![Thief Live GUI showing the belief heatmap over the police's position](docs/images/thief-gui-belief-map.png)

```bash
# generate a deterministic local match that records both tracks, then open the window
uv run python -m thief_agent artifacts --out /tmp/demo --game-id demo --seed 7
uv run python -m thief_agent view --gui --replay-dir /tmp/demo --game-id demo --step 8
```

Window: [`gui/tk_live.py`](src/thief_agent/gui/tk_live.py) and
[`gui/tk_canvas.py`](src/thief_agent/gui/tk_canvas.py); view-model:
[`gui/live_model.py`](src/thief_agent/gui/live_model.py); colours:
[`gui/palette.py`](src/thief_agent/gui/palette.py).

**What the shading means.** Each cell is shaded by *P(opponent = cell)* — bucket 0 (dark)
to bucket 9 (bright red-orange), normalised against the posterior peak. That posterior is
produced by the same `BeliefMap` the strategies consult, updated from the opponent's
received scent field and nothing else. **No opponent position is ever drawn**: only one
marker appears on the board, and it is this agent. The Thief window therefore shows the Thief's
belief about the Cop; the Cop window in the companion repository shows the mirror image.

**Turn indicator** (Chapter 7.3.2): the banner is **green `YOUR TURN`** while the protocol
is in a move-accepting state and **grey `LOCKED`** otherwise, driven by the existing
`status_banner.input_locked`, so the banner cannot disagree with the state machine.

**Where the numbers come from.** `--replay-dir` replays a recorded match's trajectories
through the real emission kernel (`domain/smell.step_update`) to rebuild the exact scent an
agent perceived, then feeds it to the real `BeliefMap`
([`gui/evidence.py`](src/thief_agent/gui/evidence.py)). Nothing is invented for the
screenshot; the capture tool refuses to shoot a uniform map. Without `--replay-dir` the
window opens on the step-1 opening position, whose posterior is legitimately flat.

### 5.2 Replay App — stepping through a match with per-step verification

![Replay viewer showing VERIFIED OK on the official G020 series](docs/images/thief-replay-verified-ok.png)

```bash
uv run python -m thief_agent replay --dir docs/evidence/G020 --game-id G020 --gui
```

Window: [`gui/tk_replay.py`](src/thief_agent/gui/tk_replay.py); panel helpers:
[`gui/replay_panel.py`](src/thief_agent/gui/replay_panel.py); stepping and verdict:
[`gui/replay_model.py`](src/thief_agent/gui/replay_model.py) over the pre-existing
[`gui/replay_verify.py`](src/thief_agent/gui/replay_verify.py).

**Previous** and **Next** walk the reconstructed frames (disabling themselves at the ends);
**Sub-game** cycles through the six logs; the counter reports `frame N / M (step S)`; the
board shows the recorded track with recency shading.

**The badge is a result, not a label.** For every record the viewer recomputes
`SHA-256(nonce, payload)` and compares it with the stored commitment. It paints green
`VERIFIED OK` only when every step reconciles, and red `TAMPERED at steps …` otherwise. The
capture above is the **official counted match G020 vs `Orcai-MJ`** (90 : 30, 6–0), whose
logs are committed under [`docs/evidence/G020/`](docs/evidence/G020/); all six sub-games
verify.

To show that the green badge is earned rather than hard-coded, the same viewer over the
same logs with one record deliberately corrupted in memory:

![Replay viewer showing TAMPERED after a deliberate corruption](docs/images/thief-replay-tampered.png)

**Reproducing the images.** [`scripts/capture_gui.py`](scripts/capture_gui.py) opens the
window and photographs it with `ffmpeg -f x11grab`; it aborts rather than capture a uniform
belief map or a verdict that does not match `--expect`.

---

## 6. Companion repository

*(Rulebook §9.4.2 item 6 and rule 49 — the cross-link is mandatory in both directions.)*

| Repository | Link |
|---|---|
| **Thief (this repo)** | https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Thief |
| **Police (companion)** | **https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police** |

---

## 7. Empirical evidence

### 7.1 League matches played (counted)

Four counted six-sub-game series against four different groups. Every sub-game log verified
untampered on both sides.

| Game | Opponent | Score (`amireman` : opponent) | Result | Logs verified |
|---|---|---|---|---|
| `G002` | `uoh-ay26` | 40 : 60 | loss | 6/6 ✔ |
| `G005` | `saedshki` | 47 : 47 | tie | 6/6 ✔ |
| `G008` | `sharNamr` | 47 : 47 | tie | 6/6 ✔ |
| `G012` | `ahk-yosi` | 40 : 60 | loss | 6/6 ✔ |

This satisfies the "at least two games against different groups" threshold with four.

<!-- FINAL-SUBMISSION TODO: insert verified final match evidence (Orcai-MJ series: game id, score, per-sub-game results, audit status) -->

### 7.2 Strategy measurement — protocol-faithful harness

Measured with the wire capture semantics of §2.2 (thief-first rounds, claim/barrier/
enclosure only, no auto-capture), our real `PeerHalf` against the current opponent's real
published agents. 100 games per cell.

| Matchup | Previous default | Current default |
|---|---|---|
| Our Thief vs their Cop | 37/100 survivals | **100/100 survivals** |
| Our Cop vs their Thief | 0/100 captures | **100/100 captures** (avg step 9.0, 0 barriers) |

The Thief result decomposes cleanly: the previous default lost 63/100, of which **every**
loss was a Rule-46 pounce. Closing the pounce range (§3.3 constraint 1) removed all of them;
deleting the endgame branch removed the residual Rule-47 enclosures.

Against our own held-out sparring registry ([`sim/opponents/`](src/thief_agent/sim/opponents))
the current Thief matches or beats the previous default on every opponent, including the
`corner_trap` pursuer where survival goes from 0.00 to 1.00 — the corner death was a real,
general weakness, not a matchup artefact.

Reproduce the sparring evaluation and ablations:

```bash
uv run python -m thief_agent tournament --seeds 8     # held-out champion selection
uv run python scripts/champion_eval.py                # evaluation harness
```

Tracked evidence: [`evidence/scenario_matchups.csv`](evidence/scenario_matchups.csv),
[`evidence/strategy_summary.json`](evidence/strategy_summary.json),
[`evidence/thief_trap_fix.csv`](evidence/thief_trap_fix.csv). Method and ablations:
[`docs/STRATEGY_EVALUATION.md`](docs/STRATEGY_EVALUATION.md),
[`docs/STRATEGY_ABLATION.md`](docs/STRATEGY_ABLATION.md),
[`docs/SELF_PLAY_METHOD.md`](docs/SELF_PLAY_METHOD.md).

### 7.3 Test suite

**563 tests passing.** Coverage gate `fail_under = 85`; `ruff` lint + format; a 150-line
per-file limit; and an automated secret scan — all enforced in CI
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

```bash
uv run pytest                                   # full suite
uv run python scripts/secret_scan.py            # secret scan
uv run python scripts/check_line_count.py       # size gate
```

---

## 8. Repository contents

*(Rulebook §9.4.1 and rule 50 — README, `config/`, PRD, PLAN and TODO are all mandatory.)*

| Required | Location |
|---|---|
| Academic report | `README.md` (this file) |
| Configuration | [`config/game.json`](config/game.json) (signed shared contract), `config/game.json.example`, `config/game.toml.example`, [`schemas/config.schema.json`](schemas/config.schema.json) |
| PRD | [`docs/PRD.md`](docs/PRD.md) |
| PLAN | [`docs/PLAN.md`](docs/PLAN.md) |
| TODO | [`docs/TODO.md`](docs/TODO.md) |
| Screenshots | [`docs/images/`](docs/images/) |
| Replay evidence (official G020) | [`docs/evidence/G020/`](docs/evidence/G020/) |

Source layout (`src/thief_agent/`): `domain/` board, rules, capture, scent, scoring, crypto ·
`strategy/` brains, belief, firewall · `peer/` sealing, turn engine, deadline, watchdog ·
`interop/` official wire, series, consensus, audit · `infra/` MCP server/client, tunnel,
Gmail · `security/` signing, auth · `report/` artifacts and verification · `gui/` live view
and replay · `sim/` evaluation harness · `sdk/` public facade.

Further reading: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md),
[`docs/MECHANISMS.md`](docs/MECHANISMS.md), [`docs/API.md`](docs/API.md),
[`docs/TESTING.md`](docs/TESTING.md), [`docs/THREAT-MODEL.md`](docs/THREAT-MODEL.md),
[`docs/OPERATIONS.md`](docs/OPERATIONS.md).

---

## 9. Security, secrets and integrity

*(Chapter 5; Appendix C.2.)*

**Commit–reveal over SHA-256.** Each turn seals `commit = SHA256(payload ‖ nonce)` before
the move is revealed ([`domain/crypto.py`](src/thief_agent/domain/crypto.py),
[`peer/sealing.py`](src/thief_agent/peer/sealing.py)). Nonces are withheld until the
end-of-game audit, where each peer re-hashes the *other's* records. Integrity is checked two
independent ways: the reveal hash must match, **and** the revealed record must be the one
actually received during play — so a peer cannot substitute a more convenient history after
the fact.

**Step-0 and computational fairness.** A Step-0 record is sealed before turn 1 carrying the
group identity and the **git commit hash actually being played** (rule 53), stamped
dynamically at the application boundary
([`shared/gitinfo.py`](src/thief_agent/shared/gitinfo.py)).

**Consensus.** A series ends only by explicit mutual agreement: both peers compute a
canonical digest over the sub-game results and exchange signed confirmations. A hash
disagreement or a missing peer confirmation fails closed — no false agreement is recorded
([`interop/consensus.py`](src/thief_agent/interop/consensus.py)).

**Reporting.** The end-of-game report is a structured, machine-readable JSON attachment sent
through the Gmail API with scoped OAuth 2.0 tokens — never a raw password, never free-text
([`infra/gmail_report.py`](src/thief_agent/infra/gmail_report.py),
[`docs/GMAIL-OAUTH.md`](docs/GMAIL-OAUTH.md)). It carries both groups' repository links, the
per-sub-game commit hash and the total tokens consumed (rules 49, 53, 54). Sending is
idempotent — a per-game marker suppresses a duplicate send.

**Secrets are never committed.** [`.gitignore`](.gitignore) excludes `credentials.json`,
`token.json`, `.env`, `*.key`, `*.pem`, and all local artifact/run directories.
`scripts/secret_scan.py` runs in CI. **No credential file has ever been committed to this
repository's history.**

---

## 10. Reproducibility

* **Python 3.13+** with [`uv`](https://docs.astral.sh/uv/); dependencies pinned in `uv.lock`.
* Every brain is deterministic under a fixed seed — same seed, same game
  ([`strategy/rng.py`](src/thief_agent/strategy/rng.py)); enforced by
  `tests/integration/test_determinism.py`.
* Configuration is **data, never hardcoded**: the signed shared contract is
  `config/game.json`, validated against a JSON schema and hashed canonically; a private
  per-peer `game.toml` may never weaken a signed term.

```bash
uv sync                                                  # install (locked)
uv run pytest                                            # 563 tests
uv run python -m thief_agent series --seed 1234          # local six-sub-game series
uv run python -m thief_agent serve --port 8002 --token dev-token          # run as a peer
uv run python -m thief_agent netplay --opponent-url http://host:8001/mcp \
    --token dev-token --counted                          # drive a networked series
```

Optional Gmail extra (only needed to actually send the report): `uv sync --extra gmail`.

---

## 11. Submission checklist

*(Appendix C.3, Table 6.)*

| Item | Required | Status |
|---|---|---|
| Two GitHub repos accessible to the lecturer | public / shared | ✔ Police + Thief |
| Cross-link between repos | present both ways | ✔ §6 |
| README report components (§9.4.2) | complete in both repos | ✔ §1–§6 |
| Belief-map (GUI) screenshot | attached | ✔ [`docs/images/thief-gui-belief-map.png`](docs/images/thief-gui-belief-map.png) — §5.1 |
| Replay screenshot with `VERIFIED OK` | attached | ✔ [`docs/images/thief-replay-verified-ok.png`](docs/images/thief-replay-verified-ok.png) — §5.2 |
| At least 2 games vs different groups | ≥ 2 | ✔ 4 counted (§7.1) |
| End-of-game email, each group separately | both sides sent | ✔ sent for `G002`; per-match thereafter |
| No secrets in the repository | verified | ✔ §9 |
| Annotated tag `v1.0-submission` | pushed | ⬜ **not yet created** — G020 is played and the screenshots are in; the tag waits on the §7.1 final-evidence pass |

Remaining actions are tracked in
[`README_FINALIZATION_CHECKLIST.md`](README_FINALIZATION_CHECKLIST.md).

---

*© 2026 team `amireman` — Amir Fadila, Eman Sarhan. University of Haifa.*
