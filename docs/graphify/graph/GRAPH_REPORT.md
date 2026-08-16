# Graph Report - thief  (2026-08-17)

## Corpus Check
- 344 files · ~175,839 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3231 nodes · 7385 edges · 177 communities (163 shown, 14 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 638 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Action
- reachable_area
- Observation
- evaluation.py
- Thief Agent — TODO (atomic, execution-ready checklist)
- test_orcai_counter.py
- board.py
- Thief Agent — Product Requirements Document (PRD)
- production.py
- Board
- Thief Agent — Academic Report
- test_gmail.py
- exceptions.py
- test_gui_tk_layer.py
- firewall.py
- emit_series
- Loopback
- DevTestSigner
- default_terms
- official_result
- confirm.py
- Phases (detail)
- Cross-team FRIENDLY interoperability — implementation & proof
- canonical_json
- thief_antisqueeze.py
- test_gui.py
- net_runtime.py
- replay_model.py
- interop/engine.py
- test_hints.py
- make_rng
- interop/series.py
- _official_email
- scenarios.py
- identity_for
- defaults.py
- evidence.py
- turn_engine.py
- test_interop_capture_finalization.py
- test_interop_consensus_envelope.py
- properties
- TurnMessage
- ReplayModel
- test_transport.py
- Role
- test_gatekeeper_deadline.py
- run_networked
- submission.py
- test_reconnect_series.py
- config_validate.py
- tk_replay.py
- mcp_server.py
- AuditPayload
- test_interop_test22_series.py
- test_netplay_official_email.py
- properties
- properties
- signer.py
- commands_gui.py
- make_tunnel
- friendly.py
- run_audit
- test_reliability.py
- test_technical_loss.py
- SubEngine
- test_interop_capture_claim_policy.py
- tunnel.py
- validate
- test_interop_official_email.py
- main
- BaselineMeta
- test_interop_mutual_confirmation.py
- test_net_layer.py
- server.py
- McpTransport
- problems_with
- test_interop_negotiate.py
- verify_series
- test_contain_bayes.py
- test_orcai_brains.py
- BlackBoxPeer
- properties
- AgentSDK
- test_mutual_audit.py
- test_advisor.py
- test_advisor_client.py
- test_interop_core.py
- smell.py
- pheromones
- RuntimeError
- config_sha256
- GridCanvas
- README.md
- QUALITY-25010.md
- required
- properties
- net_engine.py
- test_interop_peer_commit_sources.py
- version.py
- test_interop_barrier_encoding.py
- _Stub
- capture.py
- PeerHalf
- CopLocator
- required
- make_charts.py
- TacticalAdvisor
- IdemCache
- net_reconnect.py
- Architecture — Police/Thief P2P Agent
- Cost audit — total AI / API cost of this project
- Per-mechanism PRDs
- Product quality — ISO/IEC 25010 mapping
- required
- required
- properties
- OpenAIClient
- ValueError
- ProtocolError
- palette.py
- GUI guide — screens, workflow, interactions, accessibility
- Operations Manual — launch, replay, GUI, Gmail, tunnels, recovery
- enum
- champion_eval.py
- reliability.py
- SubGameRuntime
- test_idempotency.py
- test_interop_final_audit_lifecycle.py
- test_interop_demo_email.py
- test_interop_role_swap_handshake.py
- test_interop_scent_compat.py
- Evaluation (scenario-diverse, corrected + trap fix)
- derive_game_ids
- required
- PeerServer
- EventLog
- commits.py
- test_signer_state.py
- test_interop_demo_readiness.py
- test_interop_transport.py
- Prompt-engineering log
- Strategy audit (Phase 1)
- Testing & Coverage
- protocol.py
- _FakeTransport
- test_net_series_boundary.py
- Gmail OAuth setup (BLOCKED-EXTERNAL)
- PRD — API Gatekeeper, rate limiting and overflow queueing
- Submission checklist & evidence index
- score_outcome
- Official match G020 — replay evidence
- PRD — `AntiSqueezeBrain` (topology-first Thief)
- PRD — Belief representation (posterior over the opponent's cell)
- PRD — `RingBreakerBrain` (opponent-adaptive Cop)
- PRD — Stigmergic scent field (the observation model)
- Tournament methodology & results
- _FakeResp
- test_quality_gates.py
- test_sdk.py
- SDK / API reference
- Strategy baseline (frozen)
- Experiment log
- Thief strategy improvements (corrected + anti-herding trap fix)
- Signer
- offenders
- scan
- test_e2e_network.py
- Reproduction (corrected)
- shape_official_result
- seeds.py
- COMPLIANCE-CHECKLIST.md
- POLICE_STRATEGY_IMPROVEMENTS.md
- advisor/__init__.py
- sdk/__init__.py
- security/__init__.py
- opponents/__init__.py
- thief-agent

## God Nodes (most connected - your core abstractions)
1. `Board` - 216 edges
2. `Observation` - 163 edges
3. `Action` - 117 edges
4. `BeliefMap` - 79 edges
5. `make_rng()` - 69 edges
6. `BrainBase` - 64 edges
7. `DevTestSigner` - 59 edges
8. `Thief Agent — TODO (atomic, execution-ready checklist)` - 59 edges
9. `validate()` - 46 edges
10. `MetaController` - 43 edges

## Surprising Connections (you probably didn't know these)
- `test_openai_client_no_key_returns_none()` --uses--> `OpenAIClient`  [INFERRED]
  tests/unit/test_advisor_client.py → src/thief_agent/advisor/client.py
- `test_role_for_alternates()` --uses--> `Role`  [INFERRED]
  tests/unit/test_net_layer.py → src/thief_agent/constants.py
- `test_bounds_and_neighbors()` --uses--> `Board`  [INFERRED]
  tests/unit/test_board_rules.py → src/thief_agent/domain/board.py
- `test_spec_emission_unchanged_and_differs_from_compat()` --uses--> `Board`  [INFERRED]
  tests/unit/test_interop_scent_compat.py → src/thief_agent/domain/board.py
- `test_edge_clipping()` --uses--> `Board`  [INFERRED]
  tests/unit/test_scent.py → src/thief_agent/domain/board.py

## Import Cycles
- None detected.

## Communities (177 total, 14 thin omitted)

### Community 0 - "Action"
Cohesion: 0.07
Nodes (56): Latency-injected opponent (P24 robustness): wraps any opponent with a bounded,…, Reference-style opponent: a competent, balanced baseline (shortest-path pursuit…, ReferenceBrain, Opponent registry with an explicit tuning / held-out split. Champion selection…, GreedyBrain, MobilityBrain, RandomWalkBrain, Baseline (tuning-set) opponents: greedy, random-walk, shortest-path, mobility.… (+48 more)

### Community 1 - "reachable_area"
Cohesion: 0.06
Nodes (50): _BarrierProbe, Scenario-diverse paired evaluation with real barrier instrumentation. Runs one…, articulation_points(), bridges(), _dfs_order(), Cell, Connectivity structure of the passable board: articulation points and bridges…, Cells whose removal disconnects their component (over all components). (+42 more)

### Community 2 - "Observation"
Cohesion: 0.06
Nodes (30): AIPrimaryBrain, _same(), Observation, BeliefMap, Cell, Weight cells by received scent (+ small floor), zero barriers, renormalize., is_legal(), BarrierBrain (+22 more)

### Community 3 - "evaluation.py"
Cohesion: 0.05
Nodes (48): main(), measure(), Wilson score interval - correct for proportions near 0 or 1, unlike normal CI., Baseline config with exactly one parameter changed (survival tracks max_moves)., Cop capture rate and decision latency against one opponent thief on `cfg`., sweep(), variant(), wilson() (+40 more)

### Community 4 - "Thief Agent — TODO (atomic, execution-ready checklist)"
Cohesion: 0.03
Nodes (59): A. Bootstrap & engineering quality, A. Bootstrap & engineering quality, A. Bootstrap & engineering quality, A. Bootstrap & engineering quality, A. Bootstrap & engineering quality, B. Compliance & configuration, B. Compliance & configuration, C. Domain rules & movement safety (+51 more)

### Community 5 - "test_orcai_counter.py"
Cohesion: 0.05
Nodes (41): Pure game domain: geometry, rules, scoring, scent, crypto, protocol., OrcaiBelief, Cell, Faithful local model of the Orcai-MJ public Thief policy and the belief it acts…, Their ``update_from_smell``: posterior proportional to prior *…, Their ring index: distance to the nearest board edge., Every cell on a given ring -- the Thief's attractor loop for ring 1., The cell their RingRunnerThief moves to from `pos` believing the cop is at… (+33 more)

### Community 6 - "board.py"
Cohesion: 0.06
Nodes (35): Discrete N x N board geometry with barriers. Orthogonal neighbors only., Minimal deterministic headless simulator and batch runner., Normalized belief distribution over opponent cells, from legally visible data., bfs_first_step(), _dir_from(), _first_hop(), Cell, Shortest-path helper (BFS) over passable cells; returns the first step… (+27 more)

### Community 7 - "Thief Agent — Product Requirements Document (PRD)"
Cohesion: 0.04
Nodes (46): 10. FastMCP and networking, 11. Cryptographic protocol, 12. Required JSON artifacts, 13. Gmail / OAuth reporting, 14. Live GUI, 15. Replay Viewer, 16. Competitive strategy architecture, 17. Thief championship strategy requirements (primary role) (+38 more)

### Community 8 - "production.py"
Cohesion: 0.07
Nodes (34): ContainBayesBrain, ContainBrain with the Bayesian belief filter as its localisation front-end., Opponent-adaptive Cop: exact ring-runner counter, ContainBayes fallback., RingBreakerBrain, advisor_policy(), baseline_brain(), default_police(), default_thief() (+26 more)

### Community 9 - "Board"
Cohesion: 0.07
Nodes (22): Board, Cell, Reproducible offline self-play A/B benchmark for strategy evaluation. Compares…, Free natural-language hint generation and consumption (P17). Hints are…, _confidence(), Adaptive meta-controller (P16): selects a whole strategy from the portfolio…, If an AUDIT-credible directional hint shifts the belief cell, pursue it. Gated…, _corner_pressure() (+14 more)

### Community 10 - "Thief Agent — Academic Report"
Cohesion: 0.05
Nodes (41): 10. Reproducibility, 11. Token usage and project cost, 12.1 Research and results analysis, 12.2 Per-mechanism PRDs, 12.3 Interface and quality documentation, 12. Repository research and quality docs, 13.1 System requirements, 13.2 Installation (+33 more)

### Community 11 - "test_gmail.py"
Cohesion: 0.08
Nodes (27): Networking infrastructure: real FastMCP server/client transport and reliability., _args(), _counted_result(), _friendly_result(), no_real_send(), fixture, The DEMO-ONLY --demo-allow-uncounted override: a friendly/uncounted result may…, Six clean sub-games but NO counted-two-peer agreement (a friendly result). (+19 more)

### Community 12 - "exceptions.py"
Cohesion: 0.10
Nodes (30): audit_records(), commit_of(), fresh_nonce(), Any, Commit-reveal over SHA-256. Canonical serialization and commit format are…, Generate a fresh nonce and its commitment for a payload., Re-verify every {payload, nonce, commit}. Returns pass/verified/failed., seal() (+22 more)

### Community 13 - "test_gui_tk_layer.py"
Cohesion: 0.09
Nodes (34): Local, offline visualization (P20 replay viewer + P21 GUI). Two presentation…, is_uniform(), legend_rows(), live_state(), Pure view-model for the live GUI: everything the window draws, computed without…, The complete renderable state for one live frame, from a single Observation., True when every cell shares one bucket -- a flat, uninformative prior., (label, value) pairs for the window's side panel. (+26 more)

### Community 14 - "firewall.py"
Cohesion: 0.09
Nodes (30): _barrier_candidates(), candidate_actions(), _dest(), Cell, Deterministic, role-safe tactical features + legal candidate enumeration. Every…, Legal move/STAY candidates plus, for the Police, top value-positive barriers., Compact JSON-able context: globals, opponent belief, and per-candidate features., tactical_context() (+22 more)

### Community 15 - "emit_series"
Cohesion: 0.10
Nodes (30): build_config(), build_declaration(), build_log(), log_sha256(), Builders for the declaration, config, and log artifacts (mandatory field sets)., terms_of(), emit_series(), Deterministically write the full four-artifact set for a completed series. Each… (+22 more)

### Community 16 - "Loopback"
Cohesion: 0.08
Nodes (25): Boxes, Loopback, Shared in-process loopback transport for interop integration tests (no…, _identity(), _play(), End-to-end reporting integration: a real in-process six-sub-game series must…, The peer identity a side advertises. ``declare_commit=False`` reproduces a peer…, The G012 case: the peer's identity block carried no commit. Its signed Step-0… (+17 more)

### Community 17 - "DevTestSigner"
Cohesion: 0.09
Nodes (24): DevTestSigner, Development/test signer. Signatures are labelled 'devtest:'. Each instance may…, OpponentProfile, _parse_turn(), ProfileStore, Opponent profiling from AUDITED evidence only (P15). `observe_subgame` runs the…, Extract (role, cell, kind, direction, intent) from one revealed record., Accumulated, audit-verified behavioural tendencies for one opponent. (+16 more)

### Community 18 - "default_terms"
Cohesion: 0.08
Nodes (30): build_parser(), _friendly(), main(), ArgumentParser, Command line for the official-protocol interop adapter. python -m…, Official-protocol (reference-v3) cross-team interoperability adapter. A neutral…, demo_email(), DEMO ONLY: email the generated result JSON to an explicit non-lecturer… (+22 more)

### Community 19 - "official_result"
Cohesion: 0.09
Nodes (33): assert_compliant(), Raise ValueError listing every blocking problem, so an incomplete report is…, identities(), official_result(), One synthetic OFFICIAL six-sub-game result, built through the real production…, Per-sub-game runtime summaries: alternating roles, alternating peer runtime…, The exact document a counted run would write to ``result_<game_id>.json``., summaries() (+25 more)

### Community 20 - "confirm.py"
Cohesion: 0.12
Nodes (33): confirmation_summary(), final_hash(), make_confirmation(), True two-peer final confirmation (P22). Each peer signs its OWN canonical…, Canonical SHA-256 of the final result summary both peers must agree on., A peer's signed confirmation of the final result hash., Role-symmetric canonical final both peers hash identically (group-keyed)., Responder-side `confirm` handler: independently HASH the canonical final and… (+25 more)

### Community 21 - "Phases (detail)"
Cohesion: 0.06
Nodes (35): Conventions, P0 — Documentation & decisions, P10 — Minimal headless simulator (deterministic), P11 — Baseline legal strategies, P12 — Baseline/reference opponent adapters, P13 — Advanced Police strategy portfolio, P14 — Advanced Thief strategy portfolio, P15 — Audit-backed opponent profiling (+27 more)

### Community 22 - "Cross-team FRIENDLY interoperability — implementation & proof"
Cohesion: 0.06
Nodes (33): 10. Audit behaviour, 11. Artifact comparison, 12. Independent sparring result (LIVE, two real servers), 13. Black-box peer result, 14. Mixed-tunnel result, 15. FRIENDLY email hard-block result, 16–20. Gates (this repo), 1. Mandatory incompatibilities fixed (+25 more)

### Community 23 - "canonical_json"
Cohesion: 0.11
Nodes (29): canonical_json(), Key-order-independent, compact JSON so both peers hash identical bytes., build_config(), build_log(), build_result(), The four official submission artifacts (App. F table 20) — declaration, config,…, _result_rows(), canon_hash() (+21 more)

### Community 24 - "thief_antisqueeze.py"
Cohesion: 0.08
Nodes (25): _capture_cells(), Cell, Faithful sparring proxy for the public uoh-ay26 policy (their pinned SHAs).…, Cells the cop reaches next turn (move or STAY): its neighbours and itself., _threat(), UohCopBrain, UohThiefBrain, Locate the pursuing Cop from the data the protocol legally puts on the wire.… (+17 more)

### Community 25 - "test_gui.py"
Cohesion: 0.12
Nodes (29): _norm_scent(), player_marker_count(), Local-truth board view + scent overlay (P21). Renders ONLY the local player's…, Accept {(r,c): v} or {'r,c': v}; return a {(r,c): float} map., Number of player markers on a rendered local board (must always be 1)., render_board(), _scent_char(), belief_buckets() (+21 more)

### Community 26 - "net_runtime.py"
Cohesion: 0.09
Nodes (26): agree_config(), check_compatibility(), local_hello(), Pure handshake/negotiation logic: version & schema compatibility, canonical…, Raise ConfigError on protocol or schema mismatch., Return the agreed config hash; raise ConfigError on canonical mismatch., brain(), exchange_confirmation() (+18 more)

### Community 27 - "replay_model.py"
Cohesion: 0.11
Nodes (27): board_at(), Frame, load_log(), _parse(), Replay reconstruction (P20): rebuild per-turn frames from AUDITED records.…, Turn frames (step>0) with accumulated barriers; malformed records skipped., Load the records list from a log artifact; [] on missing/malformed (fail…, Latest known police/thief cells and barriers up to and including frame `idx`. (+19 more)

### Community 28 - "interop/engine.py"
Cohesion: 0.11
Nodes (23): delivery_decision(), EquivocationError, Inbox, ProtocolViolationError, Exception, The at-least-once receiver contract (SPEC §7.1) — exactly-once logical…, A second, DIFFERENT commit for a step already played — tampering evidence., An arrival past the reorder window — the flood rule. (+15 more)

### Community 29 - "test_hints.py"
Cohesion: 0.10
Nodes (26): credibility_from_records(), hint_direction(), is_valid(), is_within_cap(), leaks_information(), Public-safety filtering and audited credibility for free-language hints (P17).…, True if the hint exposes any digit (coordinate/position/index) or secret…, Return the hint unchanged if valid, else a safe generic default (fail-closed). (+18 more)

### Community 30 - "make_rng"
Cohesion: 0.15
Nodes (27): MetaController, production_brain(), Adaptive MetaController for `role`, deterministic and firewall-guarded., make_rng(), _obs(), Anti-herding trap fix: the Thief switches to DecornerBrain only when cornered…, test_decorner_moves_out_of_corner_legally(), test_survivor_climbs_out_of_corner_legally() (+19 more)

### Community 31 - "interop/series.py"
Cohesion: 0.11
Nodes (27): canonical_rows(), consensus_sha(), preimage(), The per-sub-game consensus facts, keyed by GROUP so both peers hash identically., The AGREED consensus object: EXACTLY {game_id, game_uid, sub_games}, each sub-…, SHA-256 over the canonical bytes of the AGREED preimage (identical on both…, Odd sub-games play the natural role; even ones play the opposite (alternation)., role_for() (+19 more)

### Community 32 - "_official_email"
Cohesion: 0.15
Nodes (26): _official_email(), After the counted audit passes, write the ONE reference-shaped result and email…, build_service(), email_settings(), Resolve [email] settings: recipient + mode (draft = never sends)., Build the Gmail service from an existing send-only token. Clear BLOCKED-…, _body(), _dryrun() (+18 more)

### Community 33 - "scenarios.py"
Cohesion: 0.11
Nodes (25): distance_bucket(), generate(), Deterministic, contract-valid scenario generator for scenario-diverse…, `count` distinct contract-valid scenarios, deterministic under `seed`., _scenario(), start_class(), paired_diff_ci(), _percentiles() (+17 more)

### Community 34 - "identity_for"
Cohesion: 0.12
Nodes (24): Negotiator, One peer's side of the agreement handshake for a single sub-game., identity_for(), mcp_servers_for(), This peer's static per-GROUP identity, exchanged in the handshake (roles…, Our public MCP address(es) for the identity, keyed role -> URL (both roles…, _capture_friendly(), Final-audit metadata the peer checks: our members are non-empty and our real… (+16 more)

### Community 35 - "defaults.py"
Cohesion: 0.10
Nodes (19): Random, Appendix F default game contract (schema_version 1.2). Single source for…, Strategy: interfaces, firewall, RNG, belief, fallback and baseline brains., Deterministic seeded RNG so runs are reproducible., _rand_obs(), P13 Police portfolio: legality (firewall never substitutes), no diagonals,…, test_best_barrier_reduces_thief_area(), test_hybrid_is_deterministic() (+11 more)

### Community 36 - "evidence.py"
Cohesion: 0.11
Nodes (24): build_parser(), capture_live(), capture_replay(), grab(), ArgumentParser, In-memory only: corrupt one record so the RED badge can be demonstrated…, Photograph exactly this Tk toplevel via ffmpeg's X11 window capture., _tampered() (+16 more)

### Community 37 - "turn_engine.py"
Cohesion: 0.10
Nodes (17): _obs(), Local sub-game engine: commit-reveal per turn, scent, capture/survival checks.…, run_sub_game(), Batch simulation: accumulate turns and count…, run_batch(), Deterministic single-sub-game simulation (no network, no I/O)., simulate(), _last_police_kind() (+9 more)

### Community 38 - "test_interop_capture_finalization.py"
Cohesion: 0.15
Nodes (20): _pair(), _peer_turn(), Regression for the TEST22 friendly series against Orcai-MJ. Our Cop captured on…, Only the Cop may conclude capture from claim_response.caught., A silent peer keeps the timeout verdict, but our records are still sent., Scripted peer: queues turn messages, records what we send., A turn, then the courtesy-flush COPY of it (same step, same commit)., The TEST22 sub-game 2/4/6 shape: peer replays its last turn carrying… (+12 more)

### Community 39 - "test_interop_consensus_envelope.py"
Cohesion: 0.14
Nodes (22): _peer(), The final post-series consensus AuditPayload envelope, agreed VERBATIM with…, Scenario K support: a silent peer yields None (results are never rewritten…, Scenario L: symmetric — each running role sends its own wire role and accepts…, Captures our outbound audit and replays one scripted peer response (wire dict…, Scenario E: result_claim='consensus' (not 'series_consensus') -> not accepted., Scenario F: a consensus sender must be a WIRE ROLE. A group id / non-role…, Scenario F': a peer may label the envelope with its NATURAL role OR the role it… (+14 more)

### Community 40 - "properties"
Cohesion: 0.08
Nodes (25): concurrent_requests, max_retries, queue_depth, requests_per_minute, retry_backoff_sec, minimum, type, minimum (+17 more)

### Community 41 - "TurnMessage"
Cohesion: 0.10
Nodes (16): One half-turn. The commit is sent; the nonce is withheld until the audit., TurnMessage, Capture requires a DECLARED Capture Claim + truthful caught=true (PDF §3.5,…, Scenario 1: a Cop turn with NO Capture Claim never catches the thief — even on…, Scenario 2 (+8): Capture Claim on the thief's TRUE cell -> caught=true; the…, Scenario 3 (+8): a claim at the WRONG cell -> caught=false; play continues and…, Scenario 8: when the Cop actually issues a Capture Claim (its cell == belief…, _Stay (+8 more)

### Community 42 - "ReplayModel"
Cohesion: 0.11
Nodes (14): clamp_index(), Replay viewer controls (P20): the VERIFIED OK / TAMPERED status line and the…, Stepper state: clamped index plus whether prev/next are available., Human-readable integrity banner for a replay., status_line(), step_controls(), _action_text(), One sub-game: reconstructed frames, a cursor, and its cryptographic verdict. (+6 more)

### Community 43 - "test_transport.py"
Cohesion: 0.14
Nodes (18): PeerClient, Async FastMCP client wrapper: bearer-header auth, one call per request (robust)., _call(), fixture, P18 transport gate: real FastMCP servers launched as separate localhost…, servers(), _spawn(), test_config_mismatch_refused() (+10 more)

### Community 44 - "Role"
Cohesion: 0.19
Nodes (18): complement(), Immutable physics vocabulary. Orthogonal movement only; diagonals never exist., The opposite role (used for six-sub-game alternation)., Role, Single entry-point facade for every agent business operation. External…, Run a local six-sub-game series with role alternation and fresh per-game state.…, Natural role on odd sub-games (1,3,5); swapped on even (2,4,6)., role_for() (+10 more)

### Community 45 - "test_gatekeeper_deadline.py"
Cohesion: 0.14
Nodes (14): QueueFullError, RateLimitError, Outgoing request rate exceeded the configured limit., Bounded request queue is full (DoS guard)., Gatekeeper, DoS guard: enforce max concurrency + bounded queue and a per-minute rate.…, Token-bucket rate limiter (requests per minute) with a stable long-run rate., TokenBucket (+6 more)

### Community 46 - "run_networked"
Cohesion: 0.11
Nodes (14): ReliableCaller, Fail closed on a malformed endpoint or a non-local http:// (TLS) endpoint used…, validate_public_endpoint(), Mutable progress for one series so it can resume across reconnects., run_networked(), _Series, Drive a distributed six-sub-game series over real FastMCP transport., fixture (+6 more)

### Community 47 - "submission.py"
Cohesion: 0.13
Nodes (21): group_block(), One group's static declaration block: identity, members, repos, MCP servers,…, _canonical_fingerprint(), _ended(), enrich_result(), _mutual_clean(), Shape the result to the mandatory report schema of book ch.9: top-level…, OUR side of the AGREED consensus digest over {game_id, game_uid, sub_games};… (+13 more)

### Community 48 - "test_reconnect_series.py"
Cohesion: 0.16
Nodes (14): _Connector, _Ctx, _FakeClient, _outs(), Regression for the public reconnect-continuation defect (public-smoke-006/007):…, Benign responder; optionally raises `err` at the Nth start_subgame (session…, Scripts one _Ctx per connection attempt from a list of (kind, arg) plans., _Resp (+6 more)

### Community 49 - "config_validate.py"
Cohesion: 0.15
Nodes (18): Fail-closed validation of the configured move set. Diagonals are always illegal., Return the canonical legal token tuple, or raise ConfigError (fail closed).…, validate_move_set(), ConfigError, Raised on missing, malformed, or spec-violating configuration., _check_positions(), _check_values(), flatten() (+10 more)

### Community 50 - "tk_replay.py"
Cohesion: 0.14
Nodes (13): info_text(), Pure presentation helpers for the replay viewer: trail shading and the info…, Recency-shaded wash over the cells each side is recorded as having occupied., Naive word wrap; the info panel is a fixed-width Tk label, not a text widget., The right-hand panel: where we are in the log and what the verifier concluded., trail_fills(), wrap(), The windowed Replay Viewer (rulebook Chapter 7.4): stepper + integrity badge.… (+5 more)

### Community 51 - "mcp_server.py"
Cohesion: 0.15
Nodes (15): _brain(), build_server(), PeerConfig, FastMCP, Real FastMCP peer server: bearer auth+revocation, version/schema/config-hash…, make_terms(), Launch a peer's real FastMCP HTTP server as an independent process., run() (+7 more)

### Community 52 - "AuditPayload"
Cohesion: 0.13
Nodes (13): AuditExchangeMixin, The peer's end-of-game audit FOR THIS sub-game. When the peer tags its envelope…, Discard stragglers/duplicates of THIS sub-game so the next sub-game's fresh…, Audit half of ``SubGameRuntime`` (see runtime.py for the turn loop)., Integrity (re-hash with our serializer) AND binding (revealed == received in…, AuditPayload, Negotiation, End-of-game reveal: every record with its nonce, for the OPPONENT to re-hash. (+5 more)

### Community 53 - "test_interop_test22_series.py"
Cohesion: 0.16
Nodes (18): _exchange_consensus(), Send OUR digest and (bounded) wait for the PEER's over the final-audit channel.…, _ConsensusTransport, _envelope(), Series-level regression for the TEST22 shape: aggregation, alternation,…, Roles alternate, so the peer may label with its natural OR last-sub-game role., Our natural role is thief: odd sub-games thief (survival), even police…, Guards the contrast: the old misclassification really did cost the points. (+10 more)

### Community 54 - "test_netplay_official_email.py"
Cohesion: 0.16
Nodes (12): FakeSDK, full_result(), Fixtures for the counted netplay official-email test: a FULL internal counted…, _args(), _BM, Counted netplay: after the audit passes on the FULL artifacts, write the ONE…, _SR, test_audit_failure_blocks_email() (+4 more)

### Community 55 - "properties"
Cohesion: 0.10
Nodes (21): type, type, properties, items, maxItems, minItems, type, minimum (+13 more)

### Community 56 - "properties"
Cohesion: 0.10
Nodes (21): type, minimum, type, minimum, type, properties, minimum, type (+13 more)

### Community 57 - "signer.py"
Cohesion: 0.18
Nodes (17): cmd_artifacts(), cmd_netplay(), cmd_series(), cmd_serve(), cmd_simulate(), Namespace, CLI command handlers (kept separate so cli.py stays within the line limit).…, _sdk() (+9 more)

### Community 58 - "commands_gui.py"
Cohesion: 0.15
Nodes (19): build_observation(), _cfg(), cmd_replay(), cmd_view(), _frame_index(), natural_role(), Namespace, CLI handlers for the visual layer: the live GUI window and the replay viewer.… (+11 more)

### Community 59 - "make_tunnel"
Cohesion: 0.13
Nodes (16): ConfiguredTunnel, LocalTunnel, make_tunnel(), _port_open(), Select a tunnel adapter from config. provider='local' (default) or a configured…, True if the URL is a well-formed http(s) MCP endpoint., Localhost 'tunnel': no external provider (default; always available)., Wrap an externally-provided public HTTPS URL (provider process is external). (+8 more)

### Community 60 - "friendly.py"
Cohesion: 0.16
Nodes (16): build_declaration(), emit_artifacts(), FriendlyResult, Path, FRIENDLY execution mode — a full official six-sub-game series that is…, Stand up our server, dial the opponent, play a full friendly series, write…, Write the four official artifacts for a completed series into one flat…, run_friendly() (+8 more)

### Community 61 - "run_audit"
Cohesion: 0.16
Nodes (15): Series-level identity, MCP declaration, peer-commit resolution and the dropped-…, run_audit(), _step_of(), make_step0_record(), Any, Step-0 declaration: hardware + code version + group + Git commit, sealed &…, step0_payload(), Best-effort local machine spec for the Step-0 declaration (stdlib only). (+7 more)

### Community 62 - "test_reliability.py"
Cohesion: 0.23
Nodes (18): ExhaustedRetriesError, All retries exhausted; caller maps this to a technical loss., _caller(), _ok(), _ok_send(), test_bounded_memory_cache(), test_correlation_mismatch_rejected(), test_deadline_enforced() (+10 more)

### Community 63 - "test_technical_loss.py"
Cohesion: 0.16
Nodes (13): IllegalTransitionError, Raised when the state machine is asked for a disallowed transition., Standard game state machine with an allow-list of transitions. Illegal…, StateMachine, Technical-loss result and a guarded runner for defined failure modes. Defined…, Run fn(); map defined failures to a technical result, re-raise anything else., safe_play(), technical_result() (+5 more)

### Community 64 - "SubEngine"
Cohesion: 0.12
Nodes (11): TurnMessage, Caught: seal a HOLD (no move) and deliver the honest claim_response. A caught…, Fold an inbound turn into our belief/scent/barriers; resolve capture/survival., One side of one sub-game against a remote opponent (fresh per sub-game)., LLM tokens this sub-game actually consumed, for the mandatory report (book App.…, Compute+seal one of our turns (via our brain) and build its wire message., SubEngine, Reference terms -> the flat config key names our gameplay engine consumes. (+3 more)

### Community 65 - "test_interop_capture_claim_policy.py"
Cohesion: 0.16
Nodes (13): _cfg(), _cop(), _Move, The Cop ALWAYS declares a Capture Claim for its own post-move cell — every…, Scenario A + E: Cop claims its landing cell; a Thief elsewhere returns…, Scenario C: even on STAY the Cop declares a claim for its current cell., Scenario I: the claim is the Cop's own cell REGARDLESS of where scent/belief…, Scenario B + D + F: Cop lands on the Thief's [5,6], always claims [5,6]; the… (+5 more)

### Community 66 - "tunnel.py"
Cohesion: 0.19
Nodes (16): Provider-neutral public-endpoint (tunnel) adapter (P23 connectivity). An…, Optional public-tunnel HTTP headers from PT_TUNNEL_HEADERS, e.g. a provider…, tunnel_headers(), default_connect(), _headers(), Optional public-tunnel headers (PT_TUNNEL_HEADERS): supply a provider warning-…, test_authorization_override_is_rejected(), test_configured_header_is_attached_with_bearer() (+8 more)

### Community 67 - "validate"
Cohesion: 0.22
Nodes (15): Appendix F specification tables: required fields, fixed values, minimums,…, validate(), _cfg(), parametrize, test_missing_category_fails_closed(), test_missing_one_field_fails_closed(), test_start_position_off_board_rejected(), test_unknown_field_rejected() (+7 more)

### Community 68 - "test_interop_official_email.py"
Cohesion: 0.16
Nodes (11): _BM, _DemoRun, OFFICIAL counted mode on the friendly transport: --counted reuses the exact…, Fail closed: a clean series whose result lacks a book-mandatory field is NOT…, _SR, test_counted_emails_lecturer_once(), test_counted_never_mails_a_report_missing_a_mandatory_field(), test_counted_not_clean_sends_nothing() (+3 more)

### Community 69 - "main"
Cohesion: 0.19
Nodes (14): build_parser(), main(), ArgumentParser, CLI entry point: argparse wiring only (handlers live in commands.py)., Module entry point: `python -m thief_agent ...`., CLI dispatch coverage for the non-network subcommands, driven in-process…, test_artifacts_subcommand_emits_and_verifies(), test_parser_requires_subcommand() (+6 more)

### Community 70 - "BaselineMeta"
Cohesion: 0.17
Nodes (13): BaselineMeta, _factory(), four_matchups(), Frozen baseline selection (commit 00de656 / ac8d585), used only for A/B…, Aggregate metrics for the `measure` side of police_cls-vs-thief_cls over seeds., A/B/C/D summary dict. Candidate = current MetaController; Baseline =…, run_matchup(), _obs() (+5 more)

### Community 71 - "test_interop_mutual_confirmation.py"
Cohesion: 0.17
Nodes (16): _enriched(), _play(), mutual_agreement.confirmed requires ALL of: clean peer logs, per-sub-game…, Both peers genuinely EXCHANGE digests over the final-audit channel: each…, Scenario 4: local survival vs peer capture -> result_agreed=false ->…, Scenario 5: results agree, logs clean, but the exchanged digests differ -> not…, Scenario 6: clean logs + results agree + a matching exchanged peer digest ->…, Scenario 7: no peer digest received (None) -> sha_match false -> confirmed… (+8 more)

### Community 72 - "test_net_layer.py"
Cohesion: 0.15
Nodes (10): _Data, _FakeClient, _FakeRC, _half(), In-process coverage of the peer network layer: PeerHalf message logic and the…, test_make_send_correlates_ids(), test_peer_half_act_emits_public_message(), test_peer_half_receive_absorbs_opponent() (+2 more)

### Community 73 - "server.py"
Cohesion: 0.20
Nodes (12): NetworkError, Base for transport/reliability failures., McpTransport: the peer-to-peer 'network' — my inboxes + the opponent's URL.…, build_peer_server(), _ensure_port_free(), PeerInboxes, FastMCP, This peer's OWN FastMCP server — the four official receive tools, and nothing… (+4 more)

### Community 74 - "McpTransport"
Cohesion: 0.17
Nodes (5): McpTransport, One peer's view of the wire: push to opponent, pull from own inboxes., Retry until the opponent's server is up (peers may start seconds apart)., (Re)send our SAME negotiate offer, best-effort. Transient HTTP 502 /…, MUTUAL per-sub-game handshake. A single successful POST is NOT sufficient: the…

### Community 75 - "problems_with"
Cohesion: 0.19
Nodes (13): _hex(), _own_group(), _own_values(), problems_with(), Fail-closed check that an official ``result_<game_id>.json`` carries every…, Non-blocking gaps the OPPONENT alone could have filled. Report them loudly:…, Our own group id. Our builder always writes ``groups = [ours, theirs]``., Everything we ourselves must have filled in — never excusable. (+5 more)

### Community 76 - "test_interop_negotiate.py"
Cohesion: 0.23
Nodes (13): NegotiationRefusedError, Exception, A greeting we refuse on the record: terms mismatch, bad signature, or no group., _canon(), _neg(), Unit tests for the interop signed-terms negotiation gate and the official…, _ref_sig(), test_negotiation_happy_path_derives_shared_ids() (+5 more)

### Community 77 - "verify_series"
Cohesion: 0.37
Nodes (15): verify_series(), _emit(), _rewrite(), test_broken_hash_link_fails(), test_malformed_json_fails(), test_missing_artifact_fails(), test_modified_configuration_fails(), test_modified_declaration_fails() (+7 more)

### Community 78 - "test_contain_bayes.py"
Cohesion: 0.20
Nodes (10): Cell, Histogram (Bayes) filter over the Thief's current cell. Uses only received…, ThiefBeliefFilter, _game(), Dedicated tests for the experimental contain_bayes police (ContainBayesBrain +…, _sup(), test_fresh_delta_beats_stale_then_saturation_maps(), test_initial_belief_point_mass_and_uniform() (+2 more)

### Community 79 - "test_orcai_brains.py"
Cohesion: 0.21
Nodes (13): AntiSqueezeBrain, Cell, _broadcast(), _obs(), Orcai-MJ counter, brain half: capture-on-adjacency, the STAY capture, safe…, The scent field an agent standing on `cell` actually puts on the wire., Their ring term outweighs distance, so they do step onto us; STAY + claim ends…, _step() (+5 more)

### Community 80 - "BlackBoxPeer"
Cohesion: 0.26
Nodes (7): BlackBoxPeer, canon(), commit(), game_uid(), An INDEPENDENT minimal reference-v3 peer built ONLY from the wire spec, stdlib…, Black-box interop: our production runtime plays a full six-sub-game series…, test_our_runtime_plays_an_independent_blackbox_peer()

### Community 81 - "properties"
Cohesion: 0.13
Nodes (15): hint_max_words, map_area, minimum, type, type, properties, hint_max_words, map_area (+7 more)

### Community 82 - "AgentSDK"
Cohesion: 0.14
Nodes (8): __getattr__(), Thief agent for the distributed P2P Police-Thief league (team `amireman`). The…, Lazily expose the SDK facade so importing the package stays cheap., AgentSDK, Run a local six-sub-game series with role alternation and mutual audit., Run a deterministic headless batch and return aggregate counters., Write the four artifacts, then run the integrity audit over them., Run the strict counted-match cross-repo audit over emitted artifacts.

### Community 83 - "test_mutual_audit.py"
Cohesion: 0.39
Nodes (14): verify_match(), _build(), Finding 1: strict cross-repo match audit (verify_match) fails closed on…, _rw(), test_baseline_match_audit_passes(), test_declaration_missing_github_commit_fails(), test_modified_opponent_commit_fails(), test_modified_opponent_hardware_fails() (+6 more)

### Community 84 - "test_advisor.py"
Cohesion: 0.32
Nodes (12): _ctx(), MockClient, _obs(), _peak(), OpenAI tactical-advisor tests. ZERO real API calls (mock client / fake SDK):…, test_candidates_are_all_legal(), test_context_compact_and_no_hidden_truth(), test_hard_safety_veto_blocks_unsafe_thief_move() (+4 more)

### Community 85 - "test_advisor_client.py"
Cohesion: 0.17
Nodes (9): _ctx(), _FakeResp, _FakeSDK, MockClient, _peak(), OpenAI advisor, client half: no-key fallback, usage accounting and response…, test_openai_client_malformed_output_falls_back(), test_openai_client_no_key_returns_none() (+1 more)

### Community 86 - "test_interop_core.py"
Cohesion: 0.15
Nodes (9): _canon(), parametrize, Unit tests for the interop adapter's pure layers: ids, terms, wire, delivery,…, _ref_uid(), test_delivery_decision_truth_table(), test_game_uid_matches_independent_reference_and_is_uuid(), test_inbox_dedup_reorder_and_equivocation(), test_inbox_flood_raises_protocol_violation() (+1 more)

### Community 87 - "smell.py"
Cohesion: 0.22
Nodes (13): Grid, compat_update(), decay(), emission_delta(), Cell, Stigmergic scent: the fixed 5x5 radial kernel from the PDF, edge-clipped, with…, The 5x5 kernel deposited around `centre`, clipped to in-bounds cells only., Pure decay: multiply every cell by (1-rho); drop negligible traces. (+5 more)

### Community 88 - "pheromones"
Cohesion: 0.14
Nodes (14): pheromone_center_intensity, pheromone_decay, pheromone_grid_size, const, const, const, additionalProperties, properties (+6 more)

### Community 89 - "RuntimeError"
Cohesion: 0.18
Nodes (10): RuntimeError, Raised to route a sub-game to the 0/0 technical-loss outcome., TechnicalLossError, bootstrap(), credentials_path(), Gmail OAuth wiring (P23): send-only credentials/token loaded ONLY from ignored…, Run the OAuth installed-app flow to mint a send-only token. BLOCKED-EXTERNAL:…, token_path() (+2 more)

### Community 90 - "config_sha256"
Cohesion: 0.22
Nodes (11): Per-step cryptographic verification and config-hash check for the replay viewer…, True iff the config's canonical SHA-256 matches the recorded config_sha256., verify_config_hash(), config_sha256(), Cryptographic config lock: config_sha256 = SHA256(canonical_json(config) bytes)., test_changed_value_changes_hash(), test_golden_hash_stable_and_cross_repo(), test_int_and_float_not_byte_identical() (+3 more)

### Community 91 - "GridCanvas"
Cohesion: 0.20
Nodes (7): GridCanvas, A square board canvas with per-cell fill colours, markers and barrier hatching., Repaint the whole board. `markers` maps cell -> (text, colour)., LiveWindow, Open the live window, paint `state`, and return the Tk root (caller runs the…, Board + belief heatmap + green YOUR TURN / grey LOCKED banner for one agent., show()

### Community 92 - "README.md"
Cohesion: 0.23
Nodes (3): Self-play & scenario-diverse evaluation method, Ablation (scenario-diverse), Finalization checklist

### Community 93 - "QUALITY-25010.md"
Cohesion: 0.17
Nodes (9): 1. Description and theoretical background, 2. Requirements, expected input/output, performance metrics, 3. Constraints, limitations, alternatives considered, 4. Success criteria and test scenarios, PRD — Commit-reveal integrity and mutual audit, Reuse register (course EULA), Cryptographic notes and the external boundary, Secrets policy (+1 more)

### Community 94 - "required"
Cohesion: 0.15
Nodes (12): board_and_agents, movement_and_barriers, network_and_league, pheromones, rate_limiter_gatekeeper, schema_version, scoring, world (+4 more)

### Community 95 - "properties"
Cohesion: 0.15
Nodes (13): const, const, capture_cop, capture_thief, survival_cop, survival_thief, technical_loss, tie_score (+5 more)

### Community 96 - "net_engine.py"
Cohesion: 0.18
Nodes (9): build_payload(), The sealed record: richer than (state|move|intent|nonce) per book ch5. ``move``…, _grid_in(), _grid_out(), One peer's half of a distributed sub-game: computes its own (secret) moves and…, Apply a peer's public barrier declaration on the Thief's board, keeping both…, Absorb opponent public message; apply any declared barrier; return True if…, Caught concession: seal the CURRENT (unchanged) position with the legal no-move… (+1 more)

### Community 97 - "test_interop_peer_commit_sources.py"
Cohesion: 0.19
Nodes (12): _peer_commit(), The peer's runtime SHA for THIS sub-game, as the peer itself declared it: from…, Where the peer's per-sub-game runtime SHA may come from, and where it may NOT.…, A peer that declares its commit BESIDE the identity (not inside it) is still…, g1/3/5 the peer is Police, g2/4/6 it is Thief: each row keeps that sub-game's…, _step0(), test_greeting_top_level_is_read_when_identity_has_none(), test_identity_is_preferred_and_alias_accepted() (+4 more)

### Community 98 - "version.py"
Cohesion: 0.22
Nodes (11): load_json(), load_toml(), merge(), Any, Path, Load the shared signed game.json and (optionally) the private game.toml.…, Load a shared game config, validating its declared version at startup (§8.1).…, Shallow merge where shared (signed) keys win over private keys. (+3 more)

### Community 99 - "test_interop_barrier_encoding.py"
Cohesion: 0.24
Nodes (8): _BarrierBrain, _legal_move(), _MoveBrain, _police(), Barrier encoding on the peer-facing wire/audit. Per the HW PDF §3.4, a Cop…, test_barrier_turn_seals_stay_and_separate_barrier_placed(), test_no_barrier_move_token_across_a_multi_step_police_run(), test_normal_move_still_moves_and_has_no_barrier_field()

### Community 100 - "_Stub"
Cohesion: 0.21
Nodes (7): Police end-of-game lifecycle: at the signed 35-step threshold with no capture,…, Feeds pre-built thief turns then goes silent; records nothing else it needs., n valid thief turns with the survival end-signal STRIPPED (simulate a peer that…, _Stub, test_police_early_peer_silence_is_timeout_not_survival(), test_police_self_concludes_survival_at_threshold(), _thief_turns()

### Community 101 - "capture.py"
Cohesion: 0.26
Nodes (10): barrier_captures(), captured_by_landing(), Cell, Capture predicates: landing, barrier-on-thief, and trapped-thief., True when every orthogonal neighbor is impassable (barrier and/or edge)., thief_trapped(), test_barrier_on_thief_captures(), test_capture_by_landing() (+2 more)

### Community 102 - "PeerHalf"
Cohesion: 0.26
Nodes (8): PeerHalf, A normal stay-in-place must serialize as the legal token 'STAY', not…, test_normal_stay_serializes_as_stay_token(), _AlwaysBarrier, Network barrier protocol: the Police declares and applies a barrier, the peer…, test_network_barrier_capture_and_thief_cannot_place(), test_network_barriers_synchronize(), _thief()

### Community 103 - "CopLocator"
Cohesion: 0.23
Nodes (8): CopLocator, _error(), _predict(), Cell, The field a Cop standing on `centre` would broadcast next, given `prev`., Maximum-likelihood tracker for a scent-emitting agent. ``barrier_law`` applies…, One turn of Cop motion: stay put, or step to a passable orthogonal neighbour., Fold one received message into the estimate; returns the plausible Cop cells.

### Community 104 - "required"
Cohesion: 0.18
Nodes (11): diversity_reward, max_games_per_team, min_games_to_pass, num_games, response_timeout_sec, token_budget_per_series, watchdog_timeout_sec, additionalProperties (+3 more)

### Community 105 - "make_charts.py"
Cohesion: 0.40
Nodes (10): chart_horizon(), chart_matchups(), chart_oat(), main(), Grid x horizon interaction: where the self-play capture rate collapses., Paired strategy benchmark: baseline vs candidate, with 95% intervals., OAT sensitivity: capture rate vs each parameter, one line per opponent., read() (+2 more)

### Community 106 - "TacticalAdvisor"
Cohesion: 0.24
Nodes (5): Tactical advisor: decides WHEN to consult OpenAI (call policy A/B/C), validates…, Wraps an OpenAIClient with a benchmarkable call policy and hard validation., Hard-safety veto set: OpenAI may never move the Thief onto a cell the cop can…, Return (action_id, source). source in {det-skip, openai, veto, fallback}., TacticalAdvisor

### Community 107 - "IdemCache"
Cohesion: 0.31
Nodes (7): IdemCache, Server-side idempotency: dedup by (session, request_id). A repeated request_id…, test_cache_is_bounded(), test_cache_scoped_by_session_token(), test_dedup_same_request_returns_cached_without_recompute(), test_fingerprint_ignores_rid_and_sid(), test_same_id_changed_payload_rejected()

### Community 108 - "net_reconnect.py"
Cohesion: 0.27
Nodes (10): A never-empty technical reason: many tunnel drops carry no message., transport_reason(), is_recoverable(), _leaf_ok(), _leaves(), Session isolation + transport-error classification for reconnect-safe series…, Run make_coro() in a child task; return the exception it raised (or None)…, True iff EVERY leaf is a transport-class failure, so the series may reconnect.… (+2 more)

### Community 109 - "Architecture — Police/Thief P2P Agent"
Cohesion: 0.20
Nodes (9): Architecture — Police/Thief P2P Agent, C4 — Level 1: System context, C4 — Level 2: Containers (per peer, one process), C4 — Level 3: Components (strategy), C4 — Level 4: Code (see the module map below and `docs/API.md`)., Counted-match final confirmation (P22), Deployment / network view, Module / package map (+1 more)

### Community 110 - "Cost audit — total AI / API cost of this project"
Cohesion: 0.20
Nodes (9): 1. Summary, 2. Claude Code — development usage, 3. OpenAI advisor — never used, 4. Gameplay runtime LLM usage — zero, across every game, 5. Deduplication method, 6. External services, 7. What this audit could NOT measure, 8. Reproducing these numbers (+1 more)

### Community 111 - "Per-mechanism PRDs"
Cohesion: 0.20
Nodes (9): Adaptive meta-controller (`strategy/meta`, `strategy/registry`), Audit-gated profiling (`strategy/profiling`), Commit-reveal integrity (`domain/crypto`, `peer/audit`, `peer/sealing`), Free-language hints & deception (`strategy/hints`, `strategy/hint_filter`), Gmail reporting & connectivity (`infra/gmail_*`, `infra/tunnel`), Per-mechanism PRDs, Reliability & DoS resistance (`infra/reliability`, `peer/watchdog`, `shared/gatekeeper`, `infra/idempotency`), Scent, belief & strategy portfolio (`domain/smell`, `strategy/*`) (+1 more)

### Community 112 - "Product quality — ISO/IEC 25010 mapping"
Cohesion: 0.20
Nodes (10): 1. Functional suitability, 2. Performance efficiency, 3. Compatibility, 4. Usability, 5. Reliability, 6. Security, 7. Maintainability, 8. Portability (+2 more)

### Community 113 - "required"
Cohesion: 0.20
Nodes (10): axis_origin_corner, axis_start_index, cop_start, grid_size, num_agents, thief_start, additionalProperties, required (+2 more)

### Community 114 - "required"
Cohesion: 0.20
Nodes (10): capture_cop, capture_thief, survival_cop, survival_thief, technical_loss, tie_score, scoring, additionalProperties (+2 more)

### Community 115 - "properties"
Cohesion: 0.20
Nodes (10): minimum, type, minimum, type, properties, max_barriers, max_moves, survival_threshold (+2 more)

### Community 116 - "OpenAIClient"
Cohesion: 0.24
Nodes (5): model_name(), OpenAIClient, Thin, defensive wrapper over the official OpenAI SDK (Responses API). Contract:…, One client per agent. Lazily constructs the SDK client; degrades to None., Ask the model to select an action_id. Returns the id or None (fallback).

### Community 117 - "ValueError"
Cohesion: 0.27
Nodes (8): ArtifactError, Raised on missing/malformed/schema-invalid or mismatched artifact evidence., parametrize, test_log_malformed_summary_rejected(), test_missing_required_field_rejected(), test_non_object_rejected(), test_unknown_kind_rejected(), ValueError

### Community 118 - "ProtocolError"
Cohesion: 0.27
Nodes (5): ProtocolError, Response correlation/session/ordering violation., Deadline, Deadline tracking so no operation waits forever., make_send()

### Community 119 - "palette.py"
Cohesion: 0.20
Nodes (9): banner_style(), integrity_style(), label_color(), Colour vocabulary for the Tk presentation layer (P20 replay viewer, P21 live…, Readable text colour for a bucket label drawn on top of `heat_color(bucket)`., Marker colour for the local player (blue Cop, amber Thief)., (text, background) for the turn indicator: grey LOCKED or green YOUR TURN., (background, foreground) for the replay integrity badge. (+1 more)

### Community 120 - "GUI guide — screens, workflow, interactions, accessibility"
Cohesion: 0.22
Nodes (8): 1.1 Live GUI, 1.2 Replay Viewer, 1. Screens and states, 2. Typical workflows, 3. Interactions and feedback, 4. Accessibility, 5. Reproducing the screenshots, GUI guide — screens, workflow, interactions, accessibility

### Community 121 - "Operations Manual — launch, replay, GUI, Gmail, tunnels, recovery"
Cohesion: 0.22
Nodes (8): Failure & recovery behaviour, Gmail reporting (P23), Launch commands (both roles), Live GUI (P21) — Tkinter window or headless text, Local counted-match rehearsal (P26), Operations Manual — launch, replay, GUI, Gmail, tunnels, recovery, Replay viewer (P20), Tunnel setup (provider-neutral)

### Community 122 - "enum"
Cohesion: 0.22
Nodes (9): E, N, S, STAY, W, enum, items, type (+1 more)

### Community 123 - "champion_eval.py"
Cohesion: 0.39
Nodes (8): _bench(), main(), _meta(), _play(), Offline OLD-vs-NEW strategy evaluation (no network, no Gmail, no counted mode).…, _simple(), _uoh_cop(), _uoh_thief()

### Community 124 - "reliability.py"
Cohesion: 0.31
Nodes (7): new_session_id(), Reliability wrapper around an async transport send: request IDs + correlation,…, A per-invocation session id. Each netplay run gets a fresh, unique id so its…, Regression for the persistent-responder idempotency collision (public-smoke-003…, _run_ids(), test_persistent_idem_cache_no_false_collision_but_still_anti_replay(), test_two_runs_unique_session_and_disjoint_request_ids()

### Community 125 - "SubGameRuntime"
Cohesion: 0.36
Nodes (4): TurnMessage, Runs one sub-game (police or thief) against a remote opponent., Honour a terminal ANSWER carried by a redelivered turn. Exactly-once delivery…, SubGameRuntime

### Community 126 - "test_idempotency.py"
Cohesion: 0.25
Nodes (6): StreamableHttpTransport, fixture, Finding 2: server-side idempotency over the real transport. A retried identical…, server(), _tp(), _wait()

### Community 127 - "test_interop_final_audit_lifecycle.py"
Cohesion: 0.31
Nodes (8): _free_port(), The final-audit shutdown race, reproduced at the socket level (no gameplay, no…, Drive one peer ``submit_audit`` whose response is still flushing when we shut…, BEFORE: killing the server the moment the audit is drained loses the peer's 200., AFTER: PeerServer.stop keeps serving until the peer's submit_audit fully…, _run_final_audit_scenario(), test_abrupt_shutdown_drops_final_audit_response(), test_graceful_stop_delivers_final_audit_response()

### Community 128 - "test_interop_demo_email.py"
Cohesion: 0.33
Nodes (6): FRIENDLY CLI auto-email: with --demo-email-recipient a CLEAN run auto-sends the…, _Rec, _setup(), test_friendly_auto_emails_result_with_flag(), test_friendly_no_email_when_not_clean(), test_friendly_without_flag_sends_nothing()

### Community 129 - "test_interop_role_swap_handshake.py"
Cohesion: 0.36
Nodes (8): Role-swap negotiation race regression (peer router swaps the active role-agent…, Our 1st offer is accepted+lost by the old agent; the new agent posts its offer…, test_bounded_timeout_no_infinite_hang(), test_duplicate_offers_are_safe(), test_normal_negotiation_still_works(), test_role_swap_first_offer_lost_then_resent_completes(), test_stale_prev_subgame_offer_is_skipped(), _transport()

### Community 130 - "test_interop_scent_compat.py"
Cohesion: 0.25
Nodes (8): _argmax(), League-interop scent emission (compat, max-merge). Reproduces the real G002 g01…, A reference-style Cop that trusts the strongest received scent cell localizes…, Adversarial interop MUST emit the spec/additive field (emit-only), NOT the…, test_compat_current_cell_is_unique_peak_over_real_sequence(), test_reference_style_cop_localizes_current_cell_incl_step13(), test_spec_emission_unchanged_and_differs_from_compat(), test_subengine_emits_spec_additive_scent_not_compat_beacon()

### Community 131 - "Evaluation (scenario-diverse, corrected + trap fix)"
Cohesion: 0.25
Nodes (7): Evaluation (scenario-diverse, corrected + trap fix), Fresh held-out trap opponents (300 each; baseline / old / new), Method, Opponent matrix (old cand -> new cand), Safety, Thief candidate WITH the decorner trap fix (paired), Verdicts

### Community 132 - "derive_game_ids"
Cohesion: 0.25
Nodes (6): Negotiation, derive_game_ids(), Return (game_id, game_uid) — identical for both peers, order-independent., Agreed, My agreement message: signed terms + identity + pairing fields., Check an inbound greeting; raise NegotiationRefusedError with a diagnosis, or…

### Community 133 - "required"
Cohesion: 0.25
Nodes (8): max_barriers, max_moves, move_set, survival_threshold, additionalProperties, required, type, movement_and_barriers

### Community 134 - "PeerServer"
Cohesion: 0.29
Nodes (5): Server, PeerServer, A running peer MCP server: its inboxes plus a drain-aware graceful stop. Closes…, Linger until the peer's final request has fully drained, then stop gracefully., Thread

### Community 136 - "commits.py"
Cohesion: 0.32
Nodes (7): from_identity(), from_records(), hex40(), Where a peer's per-sub-game runtime commit SHA legitimately comes from…, The value iff it is exactly 40 hex characters, else "" (never a partial match)., First 40-hex commit declared in any of the given dicts (identity, raw greeting,…, The commit revealed in the peer's Step-0 ``system_spec`` record for this sub-…

### Community 137 - "test_signer_state.py"
Cohesion: 0.25
Nodes (4): Local peer orchestration: state machine, sealing, audit, turn engine., test_devtest_signer_marks_output(), test_illegal_transition_raises(), test_official_signer_blocked_external()

### Community 138 - "test_interop_demo_readiness.py"
Cohesion: 0.36
Nodes (7): _legal_move(), _play(), One local two-peer SIX-sub-game series over the exact friendly transport…, The default template scenario is all-survival, so the capture contract is…, _self_pos(), test_capture_leg_is_truthful_with_no_post_capture_move(), test_two_peer_six_game_demo_contract()

### Community 139 - "test_interop_transport.py"
Cohesion: 0.43
Nodes (7): _headers(), Transport / tunnel-independence for the interop client: the wire is provider-…, test_bearer_and_tunnel_header_coexist(), test_bearer_only_for_ngrok_style_peer_needs_no_header(), test_no_token_no_tunnel_header_is_empty(), test_optional_localtonet_header_applies_when_configured(), test_tunnel_header_cannot_override_authorization()

### Community 140 - "Prompt-engineering log"
Cohesion: 0.29
Nodes (7): Development prompting (how the code was built), Iteration history — three cases where the first answer was wrong, Lessons learned, Prompt-engineering log, Representative development prompts and what they produced, Runtime prompting (agent play): none for moves, What is deliberately not here

### Community 141 - "Strategy audit (Phase 1)"
Cohesion: 0.29
Nodes (6): Architecture, Files likely to change / risk, Highest-value hypotheses, Strategy audit (Phase 1), Strengths, Weaknesses (evidence-backed; dev diagnostics on the fixed default board)

### Community 142 - "Testing & Coverage"
Cohesion: 0.29
Nodes (6): Coverage of external/uncoverable code, Current status (both repos), Gate configuration, How to run, Test layout, Testing & Coverage

### Community 143 - "protocol.py"
Cohesion: 0.29
Nodes (5): Protocol data models. Local Day-1 uses StepRecord; TurnMessage documents the…, A sealed per-turn record: full payload plus its nonce and commitment., Public fields a peer would send per turn. True move/position/verdict and the…, StepRecord, TurnMessage

### Community 145 - "test_net_series_boundary.py"
Cohesion: 0.33
Nodes (4): _FakeResponder, Regression: a six-sub-game networked series crosses the game-2 -> game-3…, A benign in-process responder: valid, correlated replies; never captures., test_six_subgames_cross_boundary_without_technical()

### Community 146 - "Gmail OAuth setup (BLOCKED-EXTERNAL)"
Cohesion: 0.33
Nodes (5): Behaviour guarantees (already implemented + tested), Gmail OAuth setup (BLOCKED-EXTERNAL), One-time steps (you run these), Pending external evidence, Scope

### Community 147 - "PRD — API Gatekeeper, rate limiting and overflow queueing"
Cohesion: 0.33
Nodes (5): 1. Description and theoretical background, 2. Requirements, expected input/output, performance metrics, 3. Constraints, limitations, alternatives considered, 4. Success criteria and test scenarios, PRD — API Gatekeeper, rate limiting and overflow queueing

### Community 148 - "Submission checklist & evidence index"
Cohesion: 0.33
Nodes (5): BLOCKED-EXTERNAL (require a human + external services; NOT done, NOT faked), Evidence index, Game / counted-match (DONE locally), Software quality (DONE — locally verified), Submission checklist & evidence index

### Community 149 - "score_outcome"
Cohesion: 0.40
Nodes (4): Fixed scoring table (Appendix F). Values are immutable constants., Return (police_score, thief_score) for a sub-game outcome., score_outcome(), test_fixed_scoring()

### Community 150 - "Official match G020 — replay evidence"
Cohesion: 0.40
Nodes (4): Official match G020 — replay evidence, Provenance, Reproducing the verdict, What is and is not here

### Community 151 - "PRD — `AntiSqueezeBrain` (topology-first Thief)"
Cohesion: 0.40
Nodes (5): 1. Description and theoretical background, 2. Requirements, expected input/output, performance metrics, 3. Constraints, limitations, alternatives considered, 4. Success criteria and test scenarios, PRD — `AntiSqueezeBrain` (topology-first Thief)

### Community 152 - "PRD — Belief representation (posterior over the opponent's cell)"
Cohesion: 0.40
Nodes (5): 1. Description and theoretical background, 2. Requirements, expected input/output, performance metrics, 3. Constraints, limitations, alternatives considered, 4. Success criteria and test scenarios, PRD — Belief representation (posterior over the opponent's cell)

### Community 153 - "PRD — `RingBreakerBrain` (opponent-adaptive Cop)"
Cohesion: 0.40
Nodes (5): 1. Description and theoretical background, 2. Requirements, expected input/output, performance metrics, 3. Constraints, limitations, alternatives considered, 4. Success criteria and test scenarios, PRD — `RingBreakerBrain` (opponent-adaptive Cop)

### Community 154 - "PRD — Stigmergic scent field (the observation model)"
Cohesion: 0.40
Nodes (5): 1. Description and theoretical background, 2. Requirements, expected input/output, performance metrics, 3. Constraints, limitations, alternatives considered, 4. Success criteria and test scenarios, PRD — Stigmergic scent field (the observation model)

### Community 155 - "Tournament methodology & results"
Cohesion: 0.40
Nodes (4): Methodology (bounded, reproducible, held-out), Reproduce, Results (held-out, tuning seeds 1–5, held-out seeds 100–105; 484 bounded games), Tournament methodology & results

### Community 157 - "test_quality_gates.py"
Cohesion: 0.60
Nodes (4): _load(), Positive + negative tests for the CI quality-gate scripts (line-count, secret-…, test_line_count_flags_oversize_only(), test_secret_scan_positive_and_negative()

### Community 158 - "test_sdk.py"
Cohesion: 0.60
Nodes (4): Direct coverage of the AgentSDK facade: the single entry point through which…, _sdk(), test_emit_verify_and_match_audit(), test_local_series_and_simulate()

### Community 159 - "SDK / API reference"
Cohesion: 0.50
Nodes (3): AgentSDK methods, Key building blocks (stable within the package), SDK / API reference

### Community 160 - "Strategy baseline (frozen)"
Cohesion: 0.50
Nodes (3): Baseline results — scenario-diverse (600 distinct scenarios), Faithfulness, Strategy baseline (frozen)

### Community 161 - "Experiment log"
Cohesion: 0.50
Nodes (3): Accepted (earlier), Experiment log, Trap-fix experiments (this task)

### Community 162 - "Thief strategy improvements (corrected + anti-herding trap fix)"
Cohesion: 0.50
Nodes (3): Base change (accepted earlier), Thief strategy improvements (corrected + anti-herding trap fix), Trap fix (this task) — resolves the corner_trap regression

### Community 164 - "offenders"
Cohesion: 0.67
Nodes (3): main(), offenders(), Path

### Community 165 - "scan"
Cohesion: 0.67
Nodes (3): main(), Path, scan()

### Community 166 - "test_e2e_network.py"
Cohesion: 0.67
Nodes (3): P7+P18+P19 end-to-end gate: a real responder process + a real driver process…, test_e2e_networked_series(), _wait()

## Knowledge Gaps
- **437 isolated node(s):** `thief-agent`, `$schema`, `title`, `type`, `schema_version` (+432 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Board` connect `Board` to `Action`, `reachable_area`, `Observation`, `evaluation.py`, `test_interop_scent_compat.py`, `test_orcai_counter.py`, `board.py`, `production.py`, `firewall.py`, `thief_antisqueeze.py`, `test_gui.py`, `test_hints.py`, `make_rng`, `defaults.py`, `evidence.py`, `turn_engine.py`, `TurnMessage`, `run_audit`, `BaselineMeta`, `test_contain_bayes.py`, `test_orcai_brains.py`, `test_advisor.py`, `test_advisor_client.py`, `smell.py`, `net_engine.py`, `capture.py`, `PeerHalf`, `CopLocator`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `Observation` connect `Observation` to `Action`, `reachable_area`, `evaluation.py`, `test_orcai_counter.py`, `board.py`, `production.py`, `Board`, `test_gui_tk_layer.py`, `firewall.py`, `thief_antisqueeze.py`, `test_gui.py`, `make_rng`, `defaults.py`, `evidence.py`, `turn_engine.py`, `commands_gui.py`, `BaselineMeta`, `test_orcai_brains.py`, `test_advisor.py`, `net_engine.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `canonical_json()` connect `canonical_json` to `derive_game_ids`, `IdemCache`, `exceptions.py`, `verify_series`, `emit_series`, `DevTestSigner`, `confirm.py`, `signer.py`, `config_sha256`, `friendly.py`, `interop/series.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Board` (e.g. with `thief_trapped()` and `is_move_legal()`) actually correct?**
  _`Board` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Observation` (e.g. with `AIPrimaryBrain` and `safe_fallback()`) actually correct?**
  _`Observation` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Action` (e.g. with `AIPrimaryBrain` and `_same()`) actually correct?**
  _`Action` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `BeliefMap` (e.g. with `AIPrimaryBrain` and `biased_target()`) actually correct?**
  _`BeliefMap` has 23 INFERRED edges - model-reasoned connections that need verification._