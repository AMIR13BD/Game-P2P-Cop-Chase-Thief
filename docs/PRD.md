# Thief Agent — Product Requirements Document (PRD)

> Repository: `thief/` · Natural role: **THIEF** · Team: `amireman`
> Baseline authority: the approved Phase-1 Requirements Audit + Errata v1 present in the project record.
> Spec source of truth: `_spec/police_thief_p2p.pdf` (book v3.0.0). Appendix ו (F) parameter table and explicit mandatory rules override all examples and the reference repository.
> This PRD is **independently complete**: a developer can implement this repository without opening `police/docs/PRD.md`.

---

## 1. Product identity

- **Repository identity.** `thief/` is the **Thief submission repository**. It is one of the team's two independent GitHub repositories. Its natural role is THIEF.
- **Default natural role.** THIEF (the "robber"/evader side). It plays its natural role on sub-games 1, 3, 5 and the swapped role (POLICE) on sub-games 2, 4, 6.
- **Team identity.** Team code `amireman` (8 chars, no spaces). Members: Amir Fadila (206663338), Eman Sarhan (323047407). Members submit separately in Moodle; self-grade covers code quality only, never league result.
- **Project purpose.** A fully decentralized peer-to-peer autonomous agent that plays the "Police–Thief" pursuit race on a discrete grid with no central referee. Integrity is guaranteed cryptographically, not by trust. The product's ambition is to be the **strongest legal Thief agent we can engineer** for the live league.
- **Independent-process requirement.** This agent runs as its own OS process, with its own FastMCP server on its own port, its own private config, and its own GUI. It communicates with the opponent only over MCP.
- **Independent-runtime requirement.** This repository is independently installable and runnable (`uv sync`; `uv run …`). It must not import from, symlink to, or depend on any runtime file outside itself, and must never share memory, variables, secrets, or private state with any other process.
- **Six-sub-game role-switching requirement.** One counted meeting against an opponent is a **six-sub-game series**. Roles alternate: natural (THIEF) on sub-games 1/3/5, swapped (POLICE) on 2/4/6. Therefore this repository must be a **complete dual-role agent**, strong as both Thief and Police, even though its submission identity is Thief.

---

## 2. Competitive mission

The product must:

- **Fully comply** with the specification (every mandatory rule and Appendix F parameter).
- **Avoid technical losses** (no crash, timeout, illegal move, protocol violation, or crypto forgery — each is scored 0/0).
- **Maintain cryptographic integrity** end-to-end (commit-reveal, mutual audit, tamper detection).
- **Operate reliably over real networks** (public HTTPS tunnel, retries, backoff, watchdog, deadline tracking).
- **Provide reproducible behavior** (deterministic seeds; identical config+seed ⇒ identical replay).
- **Maximize legal competitive performance** — this is not a compliance demo; after foundations are reliable, the majority of engineering effort targets winning.
- **Adapt across a six-sub-game series** using only legally audited opponent data.
- **Be selected and improved using measurable tournament evidence** — the shipped champion is chosen by data, not by author preference.

This document deliberately does **not** describe the agent as baseline, minimal, or merely sufficient, and it does **not** claim guaranteed victory. It targets the strongest legal agent we can build.

---

## 3. Non-goals

- No central referee or authoritative server.
- No shared runtime state between the two processes/repositories.
- No hidden or side-band communication channel that leaks game state.
- No access to opponent private state during live play.
- No bird's-eye live GUI (no simultaneous view of both true positions).
- No LLM-controlled movement, barrier, legality, or protocol decision.
- No secret leakage; no committing credentials, tokens, or keys.
- No weakening of mandatory minimums.
- No diagonal movement, ever.
- No fabricated audit data.
- No falsified reports or falsified game-count declarations.
- No strategy that relies on information not legally available live.

---

## 4. Personas

- **Team developer** — Amir/Eman; implements and reviews modules under the maximum-150-physical-lines-per-file quality gate.
- **Local game operator** — the person launching the peer via CLI before a match; needs clear status and safe defaults.
- **Opponent peer** — an untrusted remote process; zero-trust boundary; only protocol-visible fields are exchanged.
- **Lecturer/grader** — Dr. Segal; receives JSON reports, reads the academic README, reproduces the tagged commit.
- **Replay auditor** — anyone (grader or us) re-verifying a log step-by-step for `Verified OK`/`TAMPERED`.
- **League coordinator** — tracks counted games, diversity incentive, min/max game bounds.
- **Strategy researcher** — Amir/Eman in the self-play lab; runs tournaments, ablations, adversarial search.

---

## 5. Functional requirements

Stable IDs; every major Phase-1 mandatory rule and Appendix F parameter is traceable here. Rule references `#N` map to the Phase-1 Appendix ה rule numbers. The shared foundation FRs (ARCH..SUBMISSION, except the role-specific strategy detail in §17–§18) are identical to the Police PRD to guarantee protocol consistency across the two repositories.

### FR-ARCH — Architecture
- **FR-ARCH-01** Run as a single independent OS process (rule #1). MUST.
- **FR-ARCH-02** Never share memory/variables/secrets/private state with any other process (rule #2). MUST.
- **FR-ARCH-03** Repository is independently installable/runnable; no import/symlink/runtime dependency on `police/` or any external runtime file. MUST.
- **FR-ARCH-04** A single Orchestrator is the only entry point to subsystems (rule #3). MUST.
- **FR-ARCH-05** Support both roles (dual-role agent) for six-sub-game alternation. MUST.

### FR-CONFIG — Configuration
- **FR-CONFIG-01** Load shared signed `config/game.json` (game contract) and private `config/game.toml` (per-peer). MUST.
- **FR-CONFIG-02** `game.json` values override any parallel key in `game.toml`; the private file can never weaken a signed term. MUST.
- **FR-CONFIG-03** Enforce byte-identical shared config across both peers (rule #11); refuse to play on any mismatch. MUST.
- **FR-CONFIG-04** Validate fixed values are unchanged; minimums only raised (harder direction); negotiables only by mutual agreement (rule #12). MUST.
- **FR-CONFIG-05** Default `map_area = "New York"` unless both peers explicitly agree otherwise (incl. empty/generic). MUST.
- **FR-CONFIG-06** Field names are fixed and mandatory (map 1:1 to Appendix F). MUST.
- **FR-CONFIG-07** Give each game's config a unique name derived from `game_id`/sub-game number; attach to the repo (rules #3-config, #4). MUST.

### FR-GAME — Game rules
- **FR-GAME-01** Discrete N×N grid, default 7×7 (minimum), two agents (fixed 2). MUST.
- **FR-GAME-02** Coordinate system `(row,col)`; origin corner + axis start index negotiable but identical both sides; default top-left, index 0. MUST.
- **FR-GAME-03** Start positions negotiable; default Thief center (3,3), Police corner (0,0). MUST.
- **FR-GAME-04** Enforce scoring table exactly (capture 20/5, survival 5/10, tie 2, technical loss 0/0) (rule #48). MUST.
- **FR-GAME-05** Capture when Police lands on Thief's cell and declares a Capture Claim (rule #46 landing/claim). MUST.
- **FR-GAME-06** Barrier placed on the Thief's current cell = capture, Police wins (rule #46). MUST.
- **FR-GAME-07** Thief with no legal move (all neighbors blocked by barriers/edges) = captured (rule #47). MUST.
- **FR-GAME-08** Survival: Thief surviving ≥ survival threshold valid steps without capture wins its survival score. MUST.

### FR-MOVE — Movement & barriers
- **FR-MOVE-01** Legal move set is exactly **N, S, E, W, STAY**; no diagonals (rule #13/#14, fixed). MUST.
- **FR-MOVE-02** Reject every diagonal move and every out-of-bounds/into-barrier move. MUST.
- **FR-MOVE-03** **Fail closed**: missing/empty/malformed/unsupported `move_set` is a hard error — never fall back to legacy king movement. MUST.
- **FR-MOVE-04** Movement and barrier decisions are pure Python; never produced by an LLM. MUST.
- **FR-MOVE-05** Barrier placement is a Police-only action used when this agent plays the **swapped POLICE role** (sub-games 2/4/6): forgo movement, place on own or 4-adjacent cell, impassable for both, irreversible (quota ≥ 14). MUST.
- **FR-MOVE-06** In swapped Police role: declare every barrier truthfully with exact location; no hidden barriers, no lying (rule #15/#16). MUST.

### FR-SCENT — Scent (stigmergy)
- **FR-SCENT-01** Emit a 5×5 scent field centered on the agent, center intensity 0.9, radial falloff (fixed). MUST.
- **FR-SCENT-02** Apply decay each full turn: `τ(t+1)=max(0,(1-ρ)·τ(t)+Δτ)` with ρ=0.10 (fixed). MUST.
- **FR-SCENT-03** Cryptographically lock the scent-emission model before play (rule #23). MUST.
- **FR-SCENT-04** Sample the opponent's received scent grid (no coordinates) as belief evidence; manage own emitted trail (Thief trail betrays position). MUST.

### FR-BELIEF — Belief map
- **FR-BELIEF-01** Maintain a probability distribution over every possible opponent cell. MUST.
- **FR-BELIEF-02** Update via likelihood from scent intensity/age, known barriers, legal-move constraints, and received hints. MUST.
- **FR-BELIEF-03** Belief and scent must measurably influence decisions (Phase-1 final-checklist gate). MUST.
- **FR-BELIEF-04** Belief uses only live-legal information (§8). MUST.

### FR-NET — Networking
- **FR-NET-01** Expose the local FastMCP server to the public internet via an HTTPS tunnel (rule #10). MUST.
- **FR-NET-02** Per-request response timeout (default 30 s, negotiable). MUST.
- **FR-NET-03** Retry with backoff: ≥3 retries, ≥5 s backoff (minimums). MUST.
- **FR-NET-04** Rate limiter (token bucket) ≥30 req/min, ≥2 concurrent, queue depth ≥100 (minimums) (rule #28). MUST.
- **FR-NET-05** Gatekeeper/DoS protection guarding network resources (rule #29). MUST.
- **FR-NET-06** Idempotency + duplicate/delayed/reordered-message protection; sequence validation; malformed-message rejection. MUST.
- **FR-NET-07** Reconnection behavior and clean technical-loss handling on unrecoverable failure. MUST.

### FR-MCP — FastMCP peer
- **FR-MCP-01** Each peer is simultaneously an MCP **server and client**. MUST.
- **FR-MCP-02** Endpoint exchange during handshake; opponent URL is the only thing known about the opponent. MUST.
- **FR-MCP-03** Peer authentication (bearer/token) with revocation support. SHOULD (MUST if the negotiated protocol requires it).

### FR-STATE — State machine
- **FR-STATE-01** Manage the game with a standard state machine; reject illegal transitions and fail safely (rule #4/#5). MUST.
- **FR-STATE-02** Cover all states in §9. MUST.

### FR-RELIABILITY — Reliability
- **FR-RELIABILITY-01** Deadline tracker prevents freeze waiting on the opponent; timeout ⇒ safe technical-loss handling (rule #6). MUST.
- **FR-RELIABILITY-02** Watchdog monitors process health and extracts data on crash (rule #7, threshold 60 s negotiable). MUST.
- **FR-RELIABILITY-03** Guaranteed legal emergency fallback move within a small fraction of the deadline. MUST.

### FR-CRYPTO — Cryptography
- **FR-CRYPTO-01** Commit-reveal over SHA-256 (rule #17). MUST.
- **FR-CRYPTO-02** Canonical JSON: `json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`. MUST.
- **FR-CRYPTO-03** Commitment: `SHA256(canonical_json(payload) + "|" + nonce).hexdigest()`. MUST.
- **FR-CRYPTO-04** Fresh nonce per commitment via `secrets.token_hex(16)` (rule #18). MUST.
- **FR-CRYPTO-05** Keep nonce, true position, true move, intent/verdict, and sealed payload hidden until final audit (rule #18, Errata A3). MUST.
- **FR-CRYPTO-06** Pre-game negotiation signs terms and refuses to play on any terms mismatch (config hash verification). MUST.
- **FR-CRYPTO-07** Step-0 declaration: hardware spec + code version + team + sub-game + Git commit hash, signed via a pluggable signer (rule #24/#53). MUST.
- **FR-CRYPTO-08** Pluggable signer interface with a clearly marked dev/test signer; official course-key integration is `BLOCKED-EXTERNAL`. MUST.

### FR-AUDIT — Audit
- **FR-AUDIT-01** Final reveal of all nonces at end of game; comprehensive mutual log audit (rule #36). MUST.
- **FR-AUDIT-02** Recompute each `{payload,nonce,commit}`; any mismatch ⇒ technical loss / tamper (rule #19). MUST.
- **FR-AUDIT-03** Produce `{passed, verified_steps, failed_steps}` and agree the shared result only after audit passes. MUST.
- **FR-AUDIT-04** Truthful capture claim; as Thief, answer capture claims truthfully; lies detected at audit ⇒ disqualification (rule #21/#22). MUST.

### FR-STRATEGY — Strategy (see §16–§19 for full detail)
- **FR-STRATEGY-01** Model the game as partially observable and adversarial (Dec-POMDP). MUST.
- **FR-STRATEGY-02** Provide a portfolio of interchangeable brains behind a stable interface (no single hardwired final policy). MUST.
- **FR-STRATEGY-03** Meta-controller selects/mixes strategies from role, opponent profile, topology, sub-game #, series score, remaining barriers/moves, uncertainty, and time budget. MUST.
- **FR-STRATEGY-04** Controlled, reproducible seeded randomization. MUST.
- **FR-STRATEGY-05** Strict separation of strategy evaluation, legality validation, protocol handling, and timeout-safe fallback (the "legality firewall"). MUST.
- **FR-STRATEGY-06** Online adaptation across the six sub-games using only post-audit data (§19). MUST.
- **FR-STRATEGY-07** Champion selection driven by measurable tournament evidence (§21). MUST.

### FR-HINT — Natural-language hints
- **FR-HINT-01** Communicate in free natural language only; no numeric-coordinate protocol (rule #26/#27). MUST.
- **FR-HINT-02** Enforce the hint word cap (default 15, negotiable) on template and LLM providers. MUST.
- **FR-HINT-03** Default provider `template` (deterministic, offline, zero tokens); LLM providers opt-in only. MUST.
- **FR-HINT-04** LLM may only interpret/generate hints, classify bluff, and profile language; it never controls movement/legality/protocol. MUST.
- **FR-HINT-05** As Thief, hints are a primary deception surface (legal, ≤ word cap, no numeric coords), may reference `map_area` landmarks. MUST.

### FR-GUI — Live GUI (see §14)
- **FR-GUI-01** Show local truth only; no bird's-eye view (rule #8/#9). MUST.

### FR-REPLAY — Replay Viewer (see §15)
- **FR-REPLAY-01** Mandatory replay viewer with per-step crypto verification; `Verified OK`/`TAMPERED` (rule #20). MUST.

### FR-REPORT — Reporting (see §13)
- **FR-REPORT-01** Both teams independently auto-send a JSON report on each counted match (rule #32/#35). MUST.

### FR-SECURITY — Security
- **FR-SECURITY-01** Never commit secrets; `.gitignore` covers `credentials.json`, `token.json`, `.env`, `*.key`, `*.pem`, tunnel creds, signing keys (rule #39/#40). MUST.
- **FR-SECURITY-02** Gmail scope limited to `gmail.send` (rule #30). MUST.
- **FR-SECURITY-03** Automated secret scanning in CI, including repo history. MUST.

### FR-LEAGUE — League
- **FR-LEAGUE-01** Declare true counted-game count at each match start; never falsify (rule #37/#38). MUST.
- **FR-LEAGUE-02** One counted game per opponent (6-sub-game series); warm-ups allowed and uncounted (rule #52). MUST.
- **FR-LEAGUE-03** Minimum 2 counted opponents to pass; maximum 10 counted matches. MUST.
- **FR-LEAGUE-04** Report total tokens per sub-game and series (rule #54). MUST.

### FR-SUBMISSION — Submission
- **FR-SUBMISSION-01** Two independent repos (police, thief), README cross-links, 4 links in result JSON (rule #49). MUST.
- **FR-SUBMISSION-02** Repos private, shared with `rmisegal@gmail.com`. MUST.
- **FR-SUBMISSION-03** Each repo has README (academic report, 6 sections), `config/`, PRD, PLAN, TODO (rule #50). MUST.
- **FR-SUBMISSION-04** Annotated Git submission tag `v1.0-submission` (rule #41). MUST.
- **FR-SUBMISSION-05** GUI belief-map + Replay `Verified OK` screenshots attached (rule #42, App.ג checklist). MUST.
- **FR-SUBMISSION-06** Moodle: unique 8-char code `amireman`; each member submits separately; PDF form unchanged; self-grade code only (rules #43/#44/#45/#55). MUST.

---

## 6. Non-functional requirements

Measurable targets; verified in tests/CI. (Identical to the Police PRD.)

- **Correctness** — 100% legal moves across automated suites; zero diagonals.
- **Reliability** — zero protocol-caused technical losses in stress tests; zero valid-run audit failures.
- **Availability** — survives transient network faults via retry/backoff/reconnect.
- **Latency** — p95 strategy decision < 25% of negotiated response deadline; emergency fallback < 5%.
- **Timeout safety** — zero timeout losses across ≥10,000 simulated turns.
- **Security** — no secret ever committed; scope `gmail.send` only; CI secret scan green.
- **Privacy** — live strategy reads no audit-only field; no opponent private state accessed.
- **Interoperability** — byte-compatible with the official reference crypto/serialization and artifact schemas.
- **Reproducibility** — identical config+seed ⇒ identical replay and identical artifacts (modulo timestamps).
- **Deterministic testing** — seeded, hermetic unit tests; no network in unit tier.
- **Maintainability/Modularity** — every Python file maximum 150 physical lines per Python file (strict, CI-enforced on every tracked `.py`, no generated-file bypass); no giant generated modules.
- **Testability** — each module unit-testable in isolation behind interfaces.
- **Observability** — structured local logs; live status; per-step audit trail.
- **Auditability** — every artifact reproducible and cryptographically verifiable.
- **Performance** — full 6-sub-game series completes within league time norms; template mode = zero tokens.
- **Network resilience** — tolerate duplicate/delayed/reordered/malformed messages without state corruption.
- **Graceful degradation** — always emit a legal fallback under time pressure; degrade strategy depth, never legality.
- **Protocol compatibility** — conform to the official protocol fields/semantics; PDF wins on any conflict.

---

## 7. Mandatory parameter baseline (Appendix ו / F)

Status: **FX** fixed (never change) · **MM** minimum (raise only, never lower) · **NG** negotiable (mutual agreement). All agreed shared values must match **exactly** (byte-identical) and be cryptographically locked.

| Parameter (JSON key) | Value / minimum | Status |
|---|---|---|
| `grid_size` | 7×7 | MM |
| `num_agents` | 2 | FX |
| `axis_origin_corner` | top-left | NG |
| `axis_start_index` | 0 | NG |
| `thief_start` | (3,3) | NG |
| `cop_start` | (0,0) | NG |
| `map_area` | **New York** (default) | NG |
| `hint_max_words` | 15 | NG |
| `move_set` | N,S,E,W,STAY (no diagonals) | FX |
| `max_barriers` | 14 | MM |
| `max_moves` | 35 | MM |
| `survival_threshold` | 35 | MM |
| `pheromone_center_intensity` | 0.9 | FX |
| `pheromone_decay` (ρ) | 0.10 | FX |
| `pheromone_grid_size` | 5×5 | FX |
| `scoring.capture_cop` | 20 | FX |
| `scoring.capture_thief` | 5 | FX |
| `scoring.survival_cop` | 5 | FX |
| `scoring.survival_thief` | 10 | FX |
| `scoring.tie_score` | 2 | FX |
| technical loss | 0/0 | FX |
| sub-games per series | 6 | FX |
| `diversity_reward` | 10 | FX |
| `min_games_to_pass` | 2 | FX |
| `token_budget_per_series` | ~200,000 | NG |
| `max_games_per_team` | 10 | FX |
| `requests_per_minute` | 30 | MM |
| `concurrent_requests` | 2 | MM |
| `retry_backoff_sec` | 5 | MM |
| `max_retries` | 3 | MM |
| `queue_depth` | 100 | MM |
| `response_timeout_sec` | 30 | NG |
| `watchdog_timeout_sec` | 60 | NG |

Rules: fixed values cannot change; minimum values may only increase in the harder direction; negotiable values require mutual agreement; agreed shared values must match exactly. No illustrative reference value (e.g. `num_games:1`) overrides Appendix F (series = 6).

---

## 8. Local-truth information model

### Live private information (never sent)
own position · own strategy state · own belief map · own private configuration · own nonce · own sealed payload · own opponent model.

### Live public/received information (protocol-visible)
commit hash (opaque) · natural-language hint (may be a lie) · scent grid `{"r,c":intensity}` (no coordinates of self) · timestamp · public barrier declaration · public capture claim · public claim response · public win claim · other explicitly public control messages.

### Audit-only information (revealed at final audit only)
opponent true position · opponent true movement · opponent intent/verdict · opponent nonce · full committed records.

- **FR-INFO-01** Live strategy MUST read only live public/received + own private information. Reading any audit-only field during live play is prohibited and is enforced by an interface boundary (audit data is unavailable to the live decision path). MUST.
- **FR-INFO-02** Post-audit opponent profiling MUST derive only from legally revealed audit records (§19). MUST.

---

## 9. State machine

Required states: `STARTUP → CONFIG_LOADING → NEGOTIATION → STEP0_DECLARATION → ENDPOINT_EXCHANGE → READY → COMMIT → ACKNOWLEDGE → PUBLIC_REVEAL_EXCHANGE → LOCAL_MOVE_EXECUTION → CLAIM_HANDLING → SUBGAME_COMPLETE → FINAL_AUDIT → ARTIFACT_GENERATION → REPORT_GENERATION → REPORT_SENDING → NEXT_SUBGAME → SERIES_COMPLETE → SHUTDOWN`, plus `FAILURE` and `TECHNICAL_LOSS` reachable from any state.

- **FR-STATE-03** Every transition is validated against an allow-list; invalid transitions raise and route to `FAILURE`/`TECHNICAL_LOSS` safely (no undefined behavior). MUST.
- **FR-STATE-04** `NEXT_SUBGAME` recomputes role by parity (odd=natural THIEF, even=swapped POLICE) and resets per-sub-game state (belief, scent, commit chain). MUST.
- **FR-STATE-05** `TECHNICAL_LOSS` records 0/0, still completes audit/report where possible. MUST.

---

## 10. FastMCP and networking

- Both server and client roles in every peer (FR-MCP-01).
- Authentication (bearer/token) with revocation.
- Endpoint exchange in handshake; public HTTPS tunnel for live play (FR-NET-01).
- Timeouts (response 30 s NG), retries (≥3), backoff (≥5 s), watchdog (60 s NG), deadline tracking.
- Idempotency keys; duplicate-message protection; sequence validation; reordered/delayed tolerance; malformed-message rejection.
- Rate limiting (≥30/min, ≥2 concurrent, queue ≥100); Gatekeeper/DoS protection.
- Reconnection behavior; unrecoverable failure ⇒ deterministic technical-loss handling.
- **Local enforcement is per-peer:** agreed numeric thresholds are identical across peers, but each peer runs its **own** rate-limiter/gatekeeper/watchdog instance against its own traffic and resources (no shared instance, no shared memory).

---

## 11. Cryptographic protocol

- Canonical JSON (FR-CRYPTO-02); SHA-256 commitment (FR-CRYPTO-03); fresh nonces (FR-CRYPTO-04).
- **Commit** — send commit hash only. **Acknowledge** — opponent confirms lock (no content). **Public message exchange** — NL hint + scent grid + public declarations travel; true move/position/verdict stay sealed. **Final nonce reveal** — all nonces at end of game. **Full mutual audit** — recompute and verify every record.
- Sealed payload handling: the full per-step record (`step,state,position,move,intent,verdict,hint,prompt_discussion,model,tokens_*`) is sealed; step-0 is the signed `system_spec` block.
- Exact record verification; mismatch ⇒ technical loss; tamper detection is deterministic.
- Config hash verification in negotiation (refuse to play on mismatch).
- Step-0 declaration with Git commit hash; pluggable signing interface (dev/test signer now, official key `BLOCKED-EXTERNAL`).

---

## 12. Required JSON artifacts

Names derive from `game_id` / sub-game number; four files per match lifecycle.

- **`declaration_<game_id>.json`** — pre-game static: `game_id`, `game_uid`, times, `num_sub_games` (6 for a counted series), `max_tokens_per_game`, per-group `{group_id, group_name, members, repos{cop,thief}, mcp_servers, llm_model, hardware_spec, signature}`. Schema-validated.
- **`config_<game_id>_g<NN>.json`** — agreed per-sub-game parameters + `config_sha256`, `config_name`, `sub_game_number`; byte-identical both sides.
- **`log_<game_id>_g<NN>.json`** — per-step `records[]` of `{payload, nonce, commit}`; step-0 `system_spec`; `summary.audit{passed,verified_steps,failed_steps}`; deterministic canonical serialization for hashed fields.
- **`result_<game_id>.json`** — per-sub-game `{roles, result, winner_group, github_commit, tokens, score, log_files, audit}` + `final_result{total_score, sub_games_won, ties, winner_group, series_tie, tokens_total_series}` + `mutual_agreement{sha256, confirmed}`; includes all four GitHub links.

- **FR-ARTIFACT-01** Validate every artifact against a schema before use/emit. MUST.
- **FR-ARTIFACT-02** Result JSON carries the six-sub-game series summary, per-sub-game Git commit hashes, token counts, scores, audit results, and mutual-agreement hash. MUST.

---

## 13. Gmail / OAuth reporting

- Send-only OAuth scope `gmail.send`; fresh team OAuth credentials (policy); JSON sent as a **MIME attachment**; fixed recipient `rmisegal+uoh26finalgame@gmail.com`.
- Both teams send independently (one-sided/contradictory ⇒ 0/0 for both).
- **Dev/test mode** may build/validate a draft without sending; **counted-match mode must actually send** (rule #32; Errata A5).
- Retry + rate-limit (honor 429, back off); duplicate-send prevention (idempotent per sub-game); persist sent-message evidence (message id).
- Secret handling: credentials/token never committed; `.gitignore` + CI scan.

---

## 14. Live GUI

Local truth only, no bird's-eye:
own position · known barriers · received scent visualization · belief heatmap · turn state banner · connection status · deadline state · locked/unlocked input state · local event log. Must never render opponent true position or a full objective board.

- **FR-GUI-02** A test asserts the GUI data model contains no opponent true position. MUST.

---

## 15. Replay Viewer

- Complete reconstruction from the log; per-step cryptographic verification; config-hash verification; audit verification.
- Visible `Verified OK`; visible `TAMPERED`; precise failed-step reporting; safe handling of malformed logs (no crash).
- A single tampered step ⇒ `TAMPERED` and disqualification (no appeal).

- **FR-REPLAY-02** 100% detection of deliberately tampered fixtures (payload/nonce/commit mutations). MUST.

---

## 16. Competitive strategy architecture

Model: partially observable, adversarial (Dec-POMDP). The strategy system MUST support:

1. **Belief state** over every possible opponent position.
2. **Bayesian/likelihood updates** from scent intensity, scent decay, known barriers, legal-movement constraints, received hints, and prior legally-audited opponent behavior.
3. **Separate opponent models** for position; movement policy; hint honesty; directional tendencies; board-region preferences; barrier behavior; risk tolerance; decision latency; response to score state.
4. **Online adaptation** across the six sub-games (post-audit only).
5. **A portfolio of strategies** (not one predictable policy).
6. **A meta-controller** selecting/mixing by role, opponent profile, board topology, sub-game #, series score, remaining barriers, remaining moves, uncertainty, and decision-time budget.
7. **Controlled randomization**.
8. **Reproducible seeded execution**.
9. **Strict separation** of strategy evaluation · legality validation · protocol handling · timeout-safe fallback.

Strategy interfaces (stable):
- `ThiefBrain._pick_move(observation) -> Action`, plus `prompt_builder` for hints.
- `PoliceBrain._decide_move(observation) -> Action` (move/barrier) for swapped sub-games.
- All brains subclass a `BrainBase`; the **legality firewall** validates every proposed action and substitutes a legal fallback if needed.

Thief brain portfolio (primary; final chosen by tournament): `ThiefDistanceBrain`, `ThiefMobilityBrain`, `ThiefEntropyBrain`, `ThiefDeceptionBrain`, `ThiefSearchBrain`, `ThiefHybridChampion`.
Police brain portfolio (swapped sub-games): `PoliceGreedyBrain`, `PoliceBeliefBrain`, `PoliceInterceptBrain`, `PoliceCutPlannerBrain`, `PoliceSearchBrain`, `PoliceHybridChampion`.

The first implemented strategy is **not** hardwired as final; the champion emerges from §21 evidence.

---

## 17. Thief championship strategy requirements (primary role)

The Thief design MUST evaluate several candidate approaches and MUST NOT merely maximize Manhattan distance.

Required mechanisms:
- probabilistic Police belief map; Police future reachability prediction;
- maximum-survival search; risk-sensitive path planning; entropy-preserving movement;
- multiple escape routes; vertex-disjoint path analysis;
- dynamic trap-risk detection; barrier-threat forecasting; articulation-point avoidance; corner avoidance; large-component preservation;
- scent-trail management; misleading trajectory creation; route switching; anti-interception planning; anti-pattern randomization; controlled stochastic policies;
- opponent-model exploitation; adaptive truth/lie scheduling; natural-language deception profiles;
- endgame policy optimized for reaching the survival threshold;
- iterative deepening; transposition caching; MCTS/POMCP-style planning where computationally practical;
- guaranteed legal emergency fallback.

The Thief MUST actively: preserve future mobility; maintain multiple escape options; avoid cheaply-sealable regions; force Police to waste barriers; create ambiguous movement histories; manipulate the Police belief distribution; vary behavior to resist profiling; exploit over-aggressive pursuit; switch to survival-maximizing play near the endgame.

> Note: adaptive truth/lie scheduling is legal deception in the NL layer; the intent flag is sealed and revealed only at audit, so it cannot be observed live by the opponent within the same sub-game.

- **FR-STRATEGY-THIEF-01** probabilistic Police belief map — acceptance: normalized; localization error < uniform baseline on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-01`.)
- **FR-STRATEGY-THIEF-02** Police future-reachability prediction — acceptance: predicted set contains true next police cells on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-02`.)
- **FR-STRATEGY-THIEF-03** maximum-survival search — acceptance: maximizes survived steps vs greedy baseline on seeded sims. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-03`.)
- **FR-STRATEGY-THIEF-04** risk-sensitive path planning — acceptance: avoids high-capture-risk cells on crafted maps (unit-verified). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-04`.)
- **FR-STRATEGY-THIEF-05** entropy-preserving movement — acceptance: belief entropy stays above threshold longer than distance-only baseline. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-05`.)
- **FR-STRATEGY-THIEF-06** multiple escape routes — acceptance: maintains >=2 vertex-disjoint routes when feasible (invariant). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-06`.)
- **FR-STRATEGY-THIEF-07** vertex-disjoint path analysis — acceptance: count matches Menger/max-flow on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-07`.)
- **FR-STRATEGY-THIEF-08** dynamic trap-risk detection — acceptance: flags cells sealable within k barriers; matches brute-force on small maps. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-08`.)
- **FR-STRATEGY-THIEF-09** barrier-threat forecasting — acceptance: predicts imminent seal on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-09`.)
- **FR-STRATEGY-THIEF-10** articulation-point avoidance — acceptance: avoids own articulation cell when alternative exists (invariant). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-10`.)
- **FR-STRATEGY-THIEF-11** corner avoidance — acceptance: corner-entry rate below baseline on seeded sims. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-11`.)
- **FR-STRATEGY-THIEF-12** large-component preservation — acceptance: keeps thief in largest reachable component on crafted cases. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-12`.)
- **FR-STRATEGY-THIEF-13** scent-trail management — acceptance: reduces own high-intensity trail exposure vs naive on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-13`.)
- **FR-STRATEGY-THIEF-14** misleading trajectory creation — acceptance: legal trajectories inconsistent with hint on demand (unit-verified). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-14`.)
- **FR-STRATEGY-THIEF-15** route switching — acceptance: switches route when predicted-intercept risk rises (unit-verified). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-15`.)
- **FR-STRATEGY-THIEF-16** anti-interception planning — acceptance: reduces interception rate vs InterceptBrain on seeded sims. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-16`.)
- **FR-STRATEGY-THIEF-17** anti-pattern randomization — acceptance: move-cycle autocorrelation below threshold (statistical test). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-17`.)
- **FR-STRATEGY-THIEF-18** controlled stochastic policies — acceptance: seeded reproducible; sampling within tolerance (unit-verified). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-18`.)
- **FR-STRATEGY-THIEF-19** opponent-model exploitation — acceptance: exploits profiled tendency for survival gain on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-19`.)
- **FR-STRATEGY-THIEF-20** adaptive truth/lie scheduling — acceptance: legal schedule; intent sealed until audit (invariant); resists profiling. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-20`.)
- **FR-STRATEGY-THIEF-21** natural-language deception profiles — acceptance: hints <= word cap, no numeric coords, varied register (unit-verified). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-21`.)
- **FR-STRATEGY-THIEF-22** endgame survival policy — acceptance: near threshold prioritizes survival; endgame survival rate rises. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-22`.)
- **FR-STRATEGY-THIEF-23** iterative deepening — acceptance: anytime legal move under budget (unit-verified). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-23`.)
- **FR-STRATEGY-THIEF-24** transposition caching — acceptance: cached evaluation equals uncached (equivalence test). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-24`.)
- **FR-STRATEGY-THIEF-25** MCTS/POMCP planning — acceptance: returns legal move; beats greedy on seeded sims. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-25`.)
- **FR-STRATEGY-THIEF-26** guaranteed legal emergency fallback — acceptance: legal move within <5% of deadline (invariant). (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-26`.)
- **FR-STRATEGY-THIEF-27** preserve future mobility — acceptance: average future-degree above baseline on seeded sims. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-27`.)
- **FR-STRATEGY-THIEF-28** force Police to waste barriers — acceptance: induces wasted barriers vs baseline on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-28`.)
- **FR-STRATEGY-THIEF-29** create ambiguous movement histories — acceptance: belief-map ambiguity metric above baseline. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-29`.)
- **FR-STRATEGY-THIEF-30** manipulate Police belief distribution — acceptance: shifts adversary belief mass away from true cell on fixtures. (PLAN P14; TODO: implementation + test task each tagged `FR-STRATEGY-THIEF-30`.)

---

## 18. Police championship strategy requirements (swapped role — sub-games 2/4/6)

Even though this is the Thief repository, it must field a championship Police for swapped sub-games. The Police MUST NOT merely move toward the highest-probability cell.

Required mechanisms:
- exact reachable-set tracking; probabilistic Thief belief map; scent-source inference; scent age estimation; multi-turn trajectory inference;
- hint likelihood scoring; opponent deception profiling after audit;
- shortest-path interception; future-position interception;
- graph articulation-point detection; bridge detection; bottleneck control; connected-component analysis and reduction; minimum-cut-inspired barrier placement;
- candidate trap enumeration; reachable-area minimization; escape-route destruction; information-gain actions;
- tempo cost of barrier placement; self-obstruction avoidance;
- capture-probability estimation; risk-sensitive planning near the move limit;
- iterative deepening; transposition caching; symmetry reduction;
- minimax / expectimax / MCTS / POMCP-style planning where practical;
- guaranteed legal emergency fallback.

The Police MUST plan how to: herd the Thief; shrink future safe regions; force predictable routes; control bottlenecks; construct traps; exploit corners; intercept likely future positions; balance information gathering against pursuit; decide when a barrier is worth losing movement tempo; adapt after audited opponent behavior becomes available.

- **FR-STRATEGY-POLICE-01** exact reachable-set tracking — acceptance: BFS reachable set matches brute-force on >=1000 seeded boards. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-01`.)
- **FR-STRATEGY-POLICE-02** probabilistic Thief belief map — acceptance: normalized; localization error < uniform baseline on seeded scenarios. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-02`.)
- **FR-STRATEGY-POLICE-03** scent-source inference — acceptance: inferred source within radius 1 of true emitter on >=80% of decay fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-03`.)
- **FR-STRATEGY-POLICE-04** scent age estimation — acceptance: estimated age within +/-1 turn on decay fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-04`.)
- **FR-STRATEGY-POLICE-05** multi-turn trajectory inference — acceptance: reconstructed path beats single-step baseline on trajectory fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-05`.)
- **FR-STRATEGY-POLICE-06** hint likelihood scoring — acceptance: separates truthful vs random hints on labeled fixtures (AUC>0.6). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-06`.)
- **FR-STRATEGY-POLICE-07** opponent deception profiling after audit — acceptance: honesty-rate estimate within +/-10% on fixtures; from audit records only. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-07`.)
- **FR-STRATEGY-POLICE-08** shortest-path interception — acceptance: path length equals BFS optimum; barriers respected. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-08`.)
- **FR-STRATEGY-POLICE-09** future-position interception — acceptance: reduces expected capture time vs shortest-path chase on seeded sims. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-09`.)
- **FR-STRATEGY-POLICE-10** graph articulation-point detection — acceptance: matches reference Tarjan on >=1000 random graphs. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-10`.)
- **FR-STRATEGY-POLICE-11** bridge detection — acceptance: matches reference bridge algorithm on >=1000 random graphs. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-11`.)
- **FR-STRATEGY-POLICE-12** bottleneck control — acceptance: identifies min-cut cells on crafted maps (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-12`.)
- **FR-STRATEGY-POLICE-13** connected-component analysis — acceptance: component labels match flood-fill on fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-13`.)
- **FR-STRATEGY-POLICE-14** connected-component reduction — acceptance: chosen barrier reduces thief component size on crafted cases. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-14`.)
- **FR-STRATEGY-POLICE-15** minimum-cut-inspired barrier placement — acceptance: placement lowers thief reachable-area >= threshold on fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-15`.)
- **FR-STRATEGY-POLICE-16** candidate trap enumeration — acceptance: enumerates all <=k-barrier traps on small boards; matches brute-force. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-16`.)
- **FR-STRATEGY-POLICE-17** reachable-area minimization — acceptance: chosen action minimizes thief reachable area among candidates (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-17`.)
- **FR-STRATEGY-POLICE-18** escape-route destruction — acceptance: removes >=1 vertex-disjoint escape route when safe (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-18`.)
- **FR-STRATEGY-POLICE-19** information-gain actions — acceptance: chooses higher entropy-reduction action on ambiguous fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-19`.)
- **FR-STRATEGY-POLICE-20** tempo cost of barrier placement — acceptance: barrier chosen only when modeled value >= tempo loss (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-20`.)
- **FR-STRATEGY-POLICE-21** self-obstruction avoidance — acceptance: never places a barrier increasing own shortest path to belief mass (invariant). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-21`.)
- **FR-STRATEGY-POLICE-22** capture-probability estimation — acceptance: estimate within +/-10% of simulated capture rate on fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-22`.)
- **FR-STRATEGY-POLICE-23** risk-sensitive planning near move limit — acceptance: switches to risk-averse policy within last K moves (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-23`.)
- **FR-STRATEGY-POLICE-24** iterative deepening — acceptance: anytime returns best-so-far legal move under budget (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-24`.)
- **FR-STRATEGY-POLICE-25** transposition caching — acceptance: cached evaluation identical to uncached (equivalence test). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-25`.)
- **FR-STRATEGY-POLICE-26** symmetry reduction — acceptance: symmetric states share evaluation; node count reduced (unit-verified). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-26`.)
- **FR-STRATEGY-POLICE-27** minimax/expectimax/MCTS/POMCP planning — acceptance: returns legal move; beats greedy on seeded sims. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-27`.)
- **FR-STRATEGY-POLICE-28** guaranteed legal emergency fallback — acceptance: always a legal move within <5% of deadline (invariant). (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-28`.)
- **FR-STRATEGY-POLICE-29** herding toward corners/bottlenecks — acceptance: herding metric increases over turns on fixtures. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-29`.)
- **FR-STRATEGY-POLICE-30** post-audit adaptation of pursuit — acceptance: later-sub-game policy shifts given profile; profile from audit only. (PLAN P13; TODO: implementation + test task each tagged `FR-STRATEGY-POLICE-30`.)

---

## 19. Six-sub-game opponent adaptation

After every completed audit, legally extract and store within the current series: movement frequencies; directional preferences; center/edge/corner preference; repeated-route tendencies; barrier locations; barrier aggressiveness; hint honesty rate; truth/lie sequence patterns; language patterns; reaction to uncertainty; risk tolerance; decision latency; score-dependent behavior; strategy-switching behavior.

Requirements:
- **FR-ADAPT-01** Profile persists across the six sub-games vs the same opponent. MUST.
- **FR-ADAPT-02** Profile resets between unrelated opponents. MUST.
- **FR-ADAPT-03** No hidden live information enters the profile; every feature is traceable to a legally-audited record. MUST.
- **FR-ADAPT-04** The meta-controller may adapt later sub-games using the profile. MUST.

---

## 20. Reference-code reuse register (candidates)

Reuse is permitted under the course EULA; preserve GTAI copyright/EULA headers; document every reuse; do not copy the repo blindly. Legacy diagonal/king movement is an explicit compatibility risk.

| Component (reference path) | Purpose | Benefit | Modifications | Line refactor | License/header | Tests | Incompatibilities | Decision |
|---|---|---|---|---|---|---|---|---|
| `domain/crypto.py` | canonical JSON, commit-reveal, audit | interop w/ official format | wrap behind our interface | split if >150 physical lines physical lines | keep GTAI header + cite | crypto unit tests | none known | **reuse** |
| `domain/protocol.py` | wire messages (`TurnMessage`/`AuditPayload`/`ControlMessage`) | field-compatible P2P | trim to our fields | ok | keep header | protocol tests | none | **reuse** |
| `domain/negotiation.py` | terms signing + byte-identity refusal | safe handshake | adapt to our config loader | ok | keep header | negotiation tests | none | **adapt** |
| `domain/board.py` + `constants.py` | geometry/neighbors | proven geometry | **force N/S/E/W+STAY; strip king fallback; fail closed** | split | keep header | movement legality tests | **legacy 8-dir king default** | **adapt** |
| `shared/gatekeeper.py`, `shared/rate_limiter.py` | DoS + token bucket | reliability | tune to minimums | ok | keep header | reliability tests | none | **reuse** |
| `shared/sysinfo.py`, `peer/sealing.py` | Step-0 sysinfo + sealing | signed declaration | wire pluggable signer | split | keep header | crypto/step0 tests | official key external | **adapt** |
| `gui/replay*.py` | replay verifier | `Verified OK`/`TAMPERED` | split `replay.py` (167 -> <=150 physical lines) | **required** | keep header | replay tamper tests | none | **adapt** |
| `report/artifacts.py`, `report/emit.py` | four JSON artifacts | schema compatibility | add real send + schema validation | ok | keep header | artifact tests | draft-only default | **adapt** |
| `infra/email_sender.py` | mail | reference only | **replace** with `gmail.send` OAuth + attachment | n/a | n/a | email tests | personal skill/hardcoded path | **replace** |
| strategy brains | move policy | none (our own work) | build fresh | n/a | our headers | strategy tests | reference is basic | **replace** |

---

## 21. Acceptance criteria

Every major FR/NFR has measurable criteria; competitive gates below are release-blocking.

- 100% legal moves across automated tests; **zero diagonal moves**.
- Zero protocol-caused technical losses in stress tests.
- Zero timeout losses across ≥10,000 simulated turns.
- Zero valid-run crypto audit failures.
- 100% detection of deliberately tampered replay fixtures.
- Correct six-sub-game role alternation (odd=THIEF, even=POLICE).
- Deterministic replay for identical config and seed.
- p95 strategy latency < 25% of negotiated response deadline; emergency fallback < 5%.
- **Thief survives the shipped reference Police baseline in ≥90%** of a large seeded test set (primary role).
- **Police defeats the shipped reference Thief baseline in ≥90%** of a large seeded test set (swapped-role capability).
- Positive win rate vs diverse held-out opponents.
- No single tested opponent causes catastrophic collapse of the final mixed strategy.
- Final champion beats earlier internal champions with statistically meaningful evidence (confidence intervals, adequate sample size).

If a numerical strategy target proves impossible due to game balance, we document: sample size; confidence interval; measured ceiling; attempted improvements; and retain the highest-performing strategy. We do not silently reduce ambition.

---

## Appendix — Traceability note
Each FR maps to ≥1 PLAN phase (see `PLAN.md`) and ≥1 TODO task (see `TODO.md`). Shared foundation FRs (ARCH/CONFIG/GAME/MOVE/SCENT/BELIEF/NET/MCP/STATE/RELIABILITY/CRYPTO/AUDIT/HINT/GUI/REPLAY/REPORT/SECURITY/LEAGUE/SUBMISSION) are identical in the Police PRD; only §17–§18 role emphasis differs (Thief is the primary role here).
