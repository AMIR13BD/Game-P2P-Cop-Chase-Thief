# Thief Agent — Implementation & Research PLAN

> Repository: `thief/` · Natural role: **THIEF** · Team: `amireman` · Package: `thief_agent`
> Companion to `thief/docs/PRD.md`. Regenerated in Phase 2.1: acyclic phase DAG, phase-dependency table, and a Three-Day Critical Execution Path. Primary competitive role for this repo: **Thief**.

## Conventions
- Python 3.13+, `uv`, `pytest`, CLI-first, automated CI.
- **Every Python file: maximum 150 physical lines** (strict; CI inspects every tracked `.py`, rejects >150 physical lines, prints offending file + exact count, no generated-file bypass, and ships its own positive and negative tests).
- Reuse under the course EULA is allowed; preserve GTAI headers; log every reuse in PRD §20.
- Fail closed on any movement/config ambiguity; legality is never delegated to an LLM.
- The six documents are **created and approved documentation** (not committed — Git is not initialized in this phase).
- External blocker: the official Step-0 signing key is `BLOCKED-EXTERNAL`; the signer stays pluggable (dev/test signer used until then).

## Phase-dependency table (acyclic; every dependency points backward)

| Phase | Title | Direct dependencies | Blocking deliverables | Parallelizable with |
|---|---|---|---|---|
| P0 | Documentation & decisions | — | PRD/PLAN/TODO baseline | — |
| P1 | Repository bootstrap & CI | P0 | installable skeleton + CI | — |
| P2 | Configuration, schemas & validation | P1 | validated config contract | P3,P4 (partial) |
| P3 | Domain rules & movement safety | P2 | legal movement & scoring | P4 |
| P4 | Canonical cryptography, protocol models & negotiation | P2 | commit-reveal + audit + signer | P3 |
| P5 | Commit-reveal execution: state machine & sub-game loop (local) | P3, P4 | local turn loop | — |
| P6 | Six-sub-game series & role alternation (local) | P5 | full local series | — |
| P7 | JSON artifacts & final mutual audit | P4, P6 | four artifacts + audit | P8,P9 |
| P8 | Scent & belief-map system | P3, P6 | belief + scent evidence | P9 |
| P9 | Strategy core: BrainBase, legality firewall, seeding, fallback | P3, P6 | safe brain substrate | P8 |
| P10 | Minimal headless simulator (deterministic) | P3, P9 | seeded match engine | P8 |
| P11 | Baseline legal strategies | P9, P10 | legal reference-comparable play | — |
| P12 | Baseline/reference opponent adapters | P10, P11 | evaluation opponents | P13,P14 |
| P13 | Advanced Police strategy portfolio | P8, P11, P12 | championship Police | P14 |
| P14 | Advanced Thief strategy portfolio | P8, P11, P12 | championship Thief | P13 |
| P15 | Audit-backed opponent profiling | P7, P12 | legal per-series profile | P16 |
| P16 | Meta-controller & adaptation | P13, P14, P15 | context strategy selection | — |
| P17 | Hint & deception layer | P11, P16 | legal NL banter | — |
| P18 | FastMCP peer transport | P4, P6 | networked peer | P7,P8,P9 |
| P19 | Networking reliability | P18 | robust transport | — |
| P20 | Replay Viewer & tamper detection | P7 | cryptographic replay | P21 |
| P21 | Live local-truth GUI | P6, P8 | local-truth GUI | P20 |
| P22 | Gmail OAuth & automatic reporting | P7, P19 | real JSON-attachment send | P20,P21 |
| P23 | Public tunneling & real-network testing | P18, P19 | public URL play | — |
| P24 | Extended opponent library, tournaments, tuning, champion selection & 90% gates | P12, P13, P14, P16 | data-selected champions | P25 |
| P25 | Red-team, anti-overfitting & failure injection | P24 | hardened champions | — |
| P26 | League-readiness rehearsal | P6, P7, P19, P22, P24 | end-to-end dress run | — |
| P27 | Academic README, evidence & screenshots | P20, P21, P24 | submission evidence | — |
| P28 | Final compliance audit, annotated tags & Moodle submission | P26, P27 | tagged submission | — |

**DAG verification:** phase cycles = 0; missing phase deps = 0 (graph is a DAG).

## Three-Day Critical Execution Path

Batches group the phases above; each batch ends at a named gate. Advanced tasks are preserved (P2) even when scheduled Post-core.
- **Day 1 — foundation & local play → gate `G-MINPLAYABLE`.** P0 Documentation · P1 Bootstrap+CI · P2 Config · P3 Domain/movement · P4 Crypto/protocol/negotiation · P5 Local execution · P6 Six-sub-game series · P8 Scent/belief (core) · P9 Strategy core · P10 Minimal simulator · P11 Baseline strategies. Exit: legal local six-sub-game play with commit-reveal audit and zero technical losses.
- **Day 2 — networked strength & evidence → gate `G-PRACTICE`.** P7 Artifacts+final audit · P18 FastMCP · P19 Reliability · P12 Opponent adapters · P13 Advanced Police · P14 Advanced Thief · P15 Profiling · P16 Meta-controller · P20 Replay Viewer · P21 Live GUI · P17 Hints (start). Exit: uncounted networked practice match with GUI + `Verified OK` replay.
- **Day 3 — competition, reporting & submission → gates `G-COUNTEDREADY` then `G-SUBMISSION`.** P22 Gmail · P23 Tunnel · P24 Extended opponents/tournaments/tuning/champion+90% gates · P25 Red-team/anti-overfit/failure · P26 League rehearsal · P27 README/evidence/screenshots · P28 Compliance/tags/Moodle. Exit: counted-match-ready, then final tagged submission.
- **Post-core — deeper research (all P2).** Bayesian/evolutionary optimization, extended anti-overfitting sweeps, expanded red-team scenarios, optional LLM providers, official-signer integration (`BLOCKED-EXTERNAL`).

**Four readiness gates:** `G-MINPLAYABLE` (minimum playable) · `G-PRACTICE` (uncounted student-practice) · `G-COUNTEDREADY` (counted-match readiness) · `G-SUBMISSION` (final submission).

## Phases (detail)

### P0 — Documentation & decisions
- **Objective.** Lock the corrected Phase-2.1 documentation and team decisions.
- **Direct dependencies.** —
- **Blocking deliverables.** PRD/PLAN/TODO baseline
- **Parallelizable with.** —
- **Planned files.** docs/PRD.md, docs/PLAN.md, docs/TODO.md
- **Testing.** cross-doc traceability + DAG validation scripts
- **Exit criteria.** six created & approved documents; zero graph defects
- **Risks / Fallback.** scope drift / documented erratum
- **Evidence.** created & approved documentation set

### P1 — Repository bootstrap & CI
- **Objective.** Independently installable package, CLI, and CI enforcing tests+lint+format+types+line-limit+secret-scan.
- **Direct dependencies.** P0
- **Blocking deliverables.** installable skeleton + CI
- **Parallelizable with.** —
- **Planned files.** pyproject.toml, src/thief_agent/cli.py, scripts/check_line_count.py, scripts/secret_scan.py, .github/workflows/ci.yml
- **Testing.** uv sync; -m thief_agent --help; CI green
- **Exit criteria.** fresh clone runs; CI enforces max-150-physical-lines with no bypass
- **Risks / Fallback.** toolchain drift / pin lockfile
- **Evidence.** CI run log

### P2 — Configuration, schemas & validation
- **Objective.** Load/validate shared game.json + private game.toml; enforce Appendix F; config hashing.
- **Direct dependencies.** P1
- **Blocking deliverables.** validated config contract
- **Parallelizable with.** P3,P4 (partial)
- **Planned files.** src/thief_agent/shared/config.py, schemas/config.schema.json
- **Testing.** FX unchanged; MM raise-only; NG default New York; byte-identity
- **Exit criteria.** all Appendix F params validated; config_sha256 stable
- **Risks / Fallback.** schema drift / PDF wins; version schemas
- **Evidence.** validation report

### P3 — Domain rules & movement safety
- **Objective.** Board geometry, N/S/E/W/STAY only, fail-closed, barriers, capture, scoring.
- **Direct dependencies.** P2
- **Blocking deliverables.** legal movement & scoring
- **Parallelizable with.** P4
- **Planned files.** src/thief_agent/domain/board.py, moveset.py, rules.py, capture.py, scoring.py
- **Testing.** only 5 actions legal; diagonals rejected; malformed fail-closed
- **Exit criteria.** 100% legal-move tests; zero diagonals
- **Risks / Fallback.** legacy king default / reject-by-default allow-list
- **Evidence.** movement + scoring suites

### P4 — Canonical cryptography, protocol models & negotiation
- **Objective.** Canonical JSON, SHA-256 commit, nonce, protocol models, Step-0 sealing, pluggable signer, mutual audit, negotiation.
- **Direct dependencies.** P2
- **Blocking deliverables.** commit-reveal + audit + signer
- **Parallelizable with.** P3
- **Planned files.** src/thief_agent/domain/crypto.py, protocol.py, peer/sealing.py, security/signer.py, domain/negotiation.py
- **Testing.** golden vectors vs reference; tamper detection; refuse mismatch
- **Exit criteria.** byte-compatible commit; audit passes/fails correctly
- **Risks / Fallback.** serialization mismatch / golden vectors vs reference
- **Evidence.** crypto golden vectors

### P5 — Commit-reveal execution: state machine & sub-game loop (local)
- **Objective.** State machine with allow-list, orchestrator entry point, commit-ack-reveal-move loop; technical-loss path.
- **Direct dependencies.** P3, P4
- **Blocking deliverables.** local turn loop
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/peer/state_machine.py, orchestrator.py, turn_handler.py
- **Testing.** illegal transition -> FAILURE; local sub-game completes
- **Exit criteria.** one local sub-game plays end-to-end
- **Risks / Fallback.** deadlock / watchdog-forced loss
- **Evidence.** state-machine tests

### P6 — Six-sub-game series & role alternation (local)
- **Objective.** 3/3 role alternation and a full six-sub-game local series with fresh per-sub-game state.
- **Direct dependencies.** P5
- **Blocking deliverables.** full local series
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/sdk/series.py
- **Testing.** parity odd=natural/even=swapped; 6 sub-games; state reset
- **Exit criteria.** full local series with correct roles/scores
- **Risks / Fallback.** role desync / parity re-derivation + assert
- **Evidence.** series test + result JSON

### P7 — JSON artifacts & final mutual audit
- **Objective.** Declaration/config/log/result writers with schema validation; mutual-agreement hash; final audit.
- **Direct dependencies.** P4, P6
- **Blocking deliverables.** four artifacts + audit
- **Parallelizable with.** P8,P9
- **Planned files.** src/thief_agent/report/artifacts.py, report_writer.py, peer/audit.py
- **Testing.** schema valid; audit pass/fail; 4 links + series summary
- **Exit criteria.** four artifacts produced & cross-verified
- **Risks / Fallback.** schema mismatch / interop w/ reference schema
- **Evidence.** sample artifacts + audit report

### P8 — Scent & belief-map system
- **Objective.** 5x5 scent (0.9/0.10), belief distribution, likelihood, age, hint parser, live-info firewall.
- **Direct dependencies.** P3, P6
- **Blocking deliverables.** belief + scent evidence
- **Parallelizable with.** P9
- **Planned files.** src/thief_agent/domain/smell.py, strategy/belief.py, scent_model.py, hint_parser.py, firewall_info.py
- **Testing.** formula match; localization improves; no audit-only leakage
- **Exit criteria.** belief+scent measurably affect decisions
- **Risks / Fallback.** belief collapse / uniform floor + smoothing
- **Evidence.** belief-accuracy plots

### P9 — Strategy core: BrainBase, legality firewall, seeding, fallback
- **Objective.** Brain interface, legality firewall, seeded RNG, guaranteed legal fallback, search core.
- **Direct dependencies.** P3, P6
- **Blocking deliverables.** safe brain substrate
- **Parallelizable with.** P8
- **Planned files.** src/thief_agent/strategy/base.py, firewall.py, rng.py, fallback.py
- **Testing.** illegal proposal replaced; deterministic; fallback under pressure
- **Exit criteria.** 100% legal output; reproducible; <5% deadline fallback
- **Risks / Fallback.** fallback bias / documented safe-move ordering
- **Evidence.** legality + determinism tests

### P10 — Minimal headless simulator (deterministic)
- **Objective.** In-process no-network match engine + deterministic seeds + batch runner.
- **Direct dependencies.** P3, P9
- **Blocking deliverables.** seeded match engine
- **Parallelizable with.** P8
- **Planned files.** src/thief_agent/sim/engine.py, seeds.py, batch.py
- **Testing.** determinism; >=10,000-turn timeout sweep; sim/networked parity
- **Exit criteria.** thousands of games reproducible from seeds
- **Risks / Fallback.** sim/real divergence / cross-check sim vs networked
- **Evidence.** batch reports

### P11 — Baseline legal strategies
- **Objective.** PoliceGreedyBrain + ThiefDistanceBrain behind firewall/fallback.
- **Direct dependencies.** P9, P10
- **Blocking deliverables.** legal reference-comparable play
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/strategy/police_greedy.py, thief_distance.py
- **Testing.** 100% legal; beats random in sim (NOT tournament %)
- **Exit criteria.** baselines play full series legally
- **Risks / Fallback.** fallback bias / safe ordering
- **Evidence.** legality tests

### P12 — Baseline/reference opponent adapters
- **Objective.** Reference-baseline adapter + core opponent adapters for evaluation.
- **Direct dependencies.** P10, P11
- **Blocking deliverables.** evaluation opponents
- **Parallelizable with.** P13,P14
- **Planned files.** src/thief_agent/sim/opponents/reference.py
- **Testing.** each opponent legal; deterministic
- **Exit criteria.** reference + core opponents available
- **Risks / Fallback.** homogeneous pool / add adversarial opponents (P25)
- **Evidence.** opponent catalog

### P13 — Advanced Police strategy portfolio
- **Objective.** Belief/intercept/cutplanner/search Police brains + hybrid + all FR-STRATEGY-POLICE mechanisms.
- **Direct dependencies.** P8, P11, P12
- **Blocking deliverables.** championship Police
- **Parallelizable with.** P14
- **Planned files.** src/thief_agent/strategy/police_*.py, graph_cuts.py, search_core.py
- **Testing.** per-mechanism unit tests; beats greedy in sim
- **Exit criteria.** hybrid legal + beats greedy baseline in sim
- **Risks / Fallback.** search too slow / iterative deepening + time-sliced fallback
- **Evidence.** mechanism ablations

### P14 — Advanced Thief strategy portfolio
- **Objective.** Mobility/entropy/deception/search Thief brains + hybrid + all FR-STRATEGY-THIEF mechanisms.
- **Direct dependencies.** P8, P11, P12
- **Blocking deliverables.** championship Thief
- **Parallelizable with.** P13
- **Planned files.** src/thief_agent/strategy/thief_*.py, escape_routes.py, trap_risk.py
- **Testing.** per-mechanism unit tests; beats greedy in sim
- **Exit criteria.** hybrid legal + beats greedy baseline in sim
- **Risks / Fallback.** over-random weak / survival-search floor
- **Evidence.** mechanism ablations

### P15 — Audit-backed opponent profiling
- **Objective.** Opponent profile store + post-audit feature extraction + reset; audit-records only.
- **Direct dependencies.** P7, P12
- **Blocking deliverables.** legal per-series profile
- **Parallelizable with.** P16
- **Planned files.** src/thief_agent/strategy/opponent_profile.py, feature_extract.py
- **Testing.** persists across 6 sub-games; resets per opponent; audit-only
- **Exit criteria.** profile from audited records only
- **Risks / Fallback.** stale profile / profile reset invariant
- **Evidence.** profile-traceability test

### P16 — Meta-controller & adaptation
- **Objective.** Meta-controller selects/mixes brains by role/profile/topology/score/budget.
- **Direct dependencies.** P13, P14, P15
- **Blocking deliverables.** context strategy selection
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/strategy/meta_controller.py
- **Testing.** meta >= best single brain on held-out
- **Exit criteria.** meta-controller improves win rate
- **Risks / Fallback.** overfitting profile / conservative default mixture
- **Evidence.** A/B vs static

### P17 — Hint & deception layer
- **Objective.** Template default (0 tokens), word-cap/no-numeric policy, bluff classifier, optional LLM providers.
- **Direct dependencies.** P11, P16
- **Blocking deliverables.** legal NL banter
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/strategy/talk_providers.py, hint_policy.py, bluff_classifier.py
- **Testing.** <= word cap; no numeric coords; template zero tokens
- **Exit criteria.** full series playable at zero tokens
- **Risks / Fallback.** LLM hallucination in logic / text-only sandbox
- **Evidence.** hint-legality tests

### P18 — FastMCP peer transport
- **Objective.** Server+client, auth+revocation, endpoint exchange.
- **Direct dependencies.** P4, P6
- **Blocking deliverables.** networked peer
- **Parallelizable with.** P7,P8,P9
- **Planned files.** src/thief_agent/infra/mcp_server.py, mcp_client.py, peer/handshake.py
- **Testing.** local handshake; auth reject; malformed reject
- **Exit criteria.** two local peers connect/authenticate/exchange
- **Risks / Fallback.** FastMCP drift / pin + adapter
- **Evidence.** handshake test

### P19 — Networking reliability
- **Objective.** Retries/backoff/timeout/watchdog/deadline/idempotency/ordering/rate-limit/gatekeeper/reconnect/technical-loss.
- **Direct dependencies.** P18
- **Blocking deliverables.** robust transport
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/infra/mcp_client.py, peer/deadline.py, watchdog.py, shared/rate_limiter.py, gatekeeper.py
- **Testing.** dup/delayed/reordered/malformed tolerated; zero-hang
- **Exit criteria.** no timeout losses; no state corruption
- **Risks / Fallback.** deadlock / watchdog-forced loss
- **Evidence.** reliability suite

### P20 — Replay Viewer & tamper detection
- **Objective.** Reconstruct log; per-step verify; config-hash; Verified OK/TAMPERED; malformed-safe.
- **Direct dependencies.** P7
- **Blocking deliverables.** cryptographic replay
- **Parallelizable with.** P21
- **Planned files.** src/thief_agent/gui/replay*.py
- **Testing.** 100% tamper detection; safe on malformed
- **Exit criteria.** Verified OK + TAMPERED screenshots
- **Risks / Fallback.** missed tamper / fail-closed on verify error
- **Evidence.** tamper suite + screenshots

### P21 — Live local-truth GUI
- **Objective.** Board/scent/belief-heatmap/banner/event-log; no bird's-eye; hidden-opponent test.
- **Direct dependencies.** P6, P8
- **Blocking deliverables.** local-truth GUI
- **Parallelizable with.** P20
- **Planned files.** src/thief_agent/gui/board_view.py, heatmap.py, status_banner.py
- **Testing.** no opponent true position in model
- **Exit criteria.** local-truth GUI + screenshot
- **Risks / Fallback.** accidental full-board reveal / model-level omission + test
- **Evidence.** GUI screenshot

### P22 — Gmail OAuth & automatic reporting
- **Objective.** gmail.send OAuth, MIME JSON attachment, fixed recipient, dev-draft vs counted-send, 429 backoff, dedup.
- **Direct dependencies.** P7, P19
- **Blocking deliverables.** real JSON-attachment send
- **Parallelizable with.** P20,P21
- **Planned files.** src/thief_agent/infra/gmail_sender.py, oauth.py, report/mail_payload.py
- **Testing.** MIME attachment built w/o send; dedup; scope=send-only
- **Exit criteria.** counted-match send works; dev never sends
- **Risks / Fallback.** 429 lockout / rate-limit + retry; manual resend
- **Evidence.** sent id + unit MIME test

### P23 — Public tunneling & real-network testing
- **Objective.** Tunnel adapter + real cross-network handshake and series.
- **Direct dependencies.** P18, P19
- **Blocking deliverables.** public URL play
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/infra/tunnel.py
- **Testing.** two peers over public URL; reconnect after drop
- **Exit criteria.** live cross-network series
- **Risks / Fallback.** tunnel instability / reconnect+resume; alternate tunnel
- **Evidence.** cross-network run log

### P24 — Extended opponent library, tournaments, tuning, champion selection & 90% gates
- **Objective.** Opponent library; round-robin; Elo; CIs; ablations; sweeps; optimization; champion-vs-challenger; 90% gates.
- **Direct dependencies.** P12, P13, P14, P16
- **Blocking deliverables.** data-selected champions
- **Parallelizable with.** P25
- **Planned files.** src/thief_agent/sim/tournament.py, elo.py, stats.py, sweep.py, optimize.py, champion.py
- **Testing.** reproducible standings; 90% gates measured
- **Exit criteria.** evidence-selected hybrids beat prior champions
- **Risks / Fallback.** overfitting tuning set / held-out validation
- **Evidence.** win-rate matrix + Elo + CIs

### P25 — Red-team, anti-overfitting & failure injection
- **Objective.** Adversarial seed/scenario search; held-out validation; fault injection; every exploit -> regression.
- **Direct dependencies.** P24
- **Blocking deliverables.** hardened champions
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/sim/exploit_search.py, faults.py, tests/regression/*
- **Testing.** no open catastrophic exploit; regressions green
- **Exit criteria.** exploits converted to permanent regression tests
- **Risks / Fallback.** unknown unknowns / nightly red-team in CI
- **Evidence.** exploit log -> regression suite

### P26 — League-readiness rehearsal
- **Objective.** Full pipeline: negotiate->6 sub-games->audit->artifacts->send(dev)->counters, min2/max10/no-dup.
- **Direct dependencies.** P6, P7, P19, P22, P24
- **Blocking deliverables.** end-to-end dress run
- **Parallelizable with.** —
- **Planned files.** src/thief_agent/sim/league_rehearsal.py, docs/RUNBOOK.md
- **Testing.** counted-counter; both-sides send; no duplicate result
- **Exit criteria.** rehearsed counted match passes every gate
- **Risks / Fallback.** ops errors live / runbook + warm-ups
- **Evidence.** rehearsal transcript

### P27 — Academic README, evidence & screenshots
- **Objective.** 6-section academic README, research report, GUI + replay screenshots, reuse register.
- **Direct dependencies.** P20, P21, P24
- **Blocking deliverables.** submission evidence
- **Parallelizable with.** —
- **Planned files.** README.md, docs/RESEARCH-REPORT.md, docs/images/*
- **Testing.** README completeness; cross-link to sibling repo
- **Exit criteria.** README + evidence complete; 4 links assembled
- **Risks / Fallback.** missing evidence / regenerate from lab artifacts
- **Evidence.** rendered README + screenshots

### P28 — Final compliance audit, annotated tags & Moodle submission
- **Objective.** Compliance checklist vs rules+Appendix F; final secret scan; annotated v1.0-submission tag; Moodle by both members.
- **Direct dependencies.** P26, P27
- **Blocking deliverables.** tagged submission
- **Parallelizable with.** —
- **Planned files.** docs/COMPLIANCE-CHECKLIST.md, docs/RUNBOOK.md
- **Testing.** full suite green; secret scan clean; tag on reviewed commit
- **Exit criteria.** tag pushed; both members submit; cross-links live
- **Risks / Fallback.** late regressions / freeze + tag known-good
- **Evidence.** tag object + checklist + receipts

## Traceability (PRD -> PLAN)
ARCH->P1,P5,P6 · CONFIG->P2 · GAME/MOVE/SCENT->P3,P8 · BELIEF->P8 · CRYPTO/AUDIT->P4,P7 · STATE/RELIABILITY->P5,P19 · MCP/NET->P18,P19,P23 · STRATEGY(§16-19)->P9-P17,P24-P25 · FR-STRATEGY-POLICE-*->P13 · FR-STRATEGY-THIEF-*->P14 · HINT->P17 · GUI->P21 · REPLAY->P20 · REPORT->P7,P22 · SECURITY->P1,P22,P25 · LEAGUE->P26 · SUBMISSION->P27,P28 · Acceptance(§21)->P24,P25,P26,P28.
