# Final requirements audit — every requirement in both authoritative documents

*Generated for the `thief` repository (package `thief_agent`), team `amireman`. Both repositories
are audited against the same matrix and carry an identical copy of this document, because the
rulebook grades them as one submission in two halves.*

Two documents govern this project, and they are not equal in authority:

| | Document | Authority |
|---|---|---|
| **Source A** | `police_thief_p2p.pdf` — rulebook v3.0.0, 160 pp | **Highest.** Where the two disagree, Source A wins |
| **Source B** | `software_submission_guidelines-V3.pdf` — 39 pp | Binding *by reference*: §11.5(א) states the assignment "will be checked according to the principles in this file", and Table 4 lists it as the submission criterion |

Source A is explicit (frontmatter, *"what binds and what merely illustrates"*) that **nothing
is mandatory unless it says so**, and that the only source of truth for quantitative values is
the Appendix-F table. This audit therefore takes the rulebook's own enumeration — the 55
numbered rules of Appendix E — as the canonical mandatory list, and adds the checklists that
Appendix C, §9.4.2, §11.5 and Appendix F state as thresholds in their own right.

Source B §19 states plainly that not every clause is obligatory. Its rows are classified
`MANDATORY_FOR_PROJECT`, `APPLICABLE_EXCELLENCE` or `NOT_APPLICABLE`, and every
`NOT_APPLICABLE` carries a reason.

**No status below is asserted from a README claim.** Every `PASS` points at a file, a test, a
committed artifact or a command that was actually run during this audit.

---

## Scoreboard

| Source | Requirements | PASS | PARTIAL | FAIL | N/A |
|---|---:|---:|---:|---:|---:|
| **A — assignment rulebook** | **90** | **79** | **4** | **2** | **5** |
| **B — software guidelines** | **43** *(+1 note row)* | **38** | **4** | 0 | **1** |

Source B classification: `MANDATORY_FOR_PROJECT` 29 · `APPLICABLE_EXCELLENCE` 13 ·
`NOT_APPLICABLE` 1 · `CONFLICTS_WITH_ASSIGNMENT` **0** — no clause of Source B was found
to contradict Source A.

> **Counting note.** Source A's 90 rows are A1 (55 Appendix-E rules) + A2 (6) + A3 (9) +
> A4 (5) + A5 checklist (8) + A5 Moodle (7); statuses sum 79 + 4 + 2 + 5 = 90. Source B's
> table has 44 rows, of which 43 carry a status; the §19 row is an explanatory note, not a
> requirement, so it is excluded from the totals.

```
MANDATORY_FAIL_COUNT=2
MANDATORY_PARTIAL_COUNT=4
EXCELLENCE_GAPS=4
```

**Neither mandatory FAIL is a code defect, and neither can be fixed by committing anything.**
Both are the same underlying fact recorded where the rulebook states it twice — Appendix C
Table 6 row 1, and §11.5 item ב: **both repositories are private with no collaborator but the
owner and no pending invitation**, so Appendix C §1 is satisfied in neither of its two accepted
forms. That is HUMAN ACTION A below, and it blocks the submission outright: every other row in
this matrix describes something a grader currently cannot open.

---

## Human actions — the only items this audit could not close

| # | Action | Blocking? | Why not automated |
|---|---|---|---|
| **A** | **Grant the lecturer access to both repositories** — add them as a collaborator, or make both repos public | **YES — blocks everything** | Changes GitHub account state and repository visibility; an owner decision, and the instruction for this audit was not to change visibility automatically |
| **B** | **Re-point `v1.0-submission` at the final commit** in both repos | High | Moving a published tag needs a force update of a remote ref, which this audit was instructed not to perform |
| **C** | **Moodle submission** — fill the Word template unaltered, save as PDF, submit **separately for each member** (Amir Fadila, Eman Sarhan), with code `amireman` and both repo links | **YES** | Off-platform |
| **D** | **Enter the code-quality self-grade** on the form — code quality only, never the league result (rule #55) | Medium | A judgement the team must make and sign. Basis: `docs/QUALITY-25010.md` |

Exact commands for A and B are in README §14.

---

## A1 — Appendix E: the 55 mandatory rules

*Source A, Appendix E, pp. 126–134 (printed), Tables 7–12. This is the rulebook's own
consolidated list of every binding rule, with its sanction.*

| # | Action | Requirement | Status | Evidence |
|---|---|---|---|---|
| **1** | MUST | Run Thief and Police code in two fully separate processes | PASS | `peer/net_runtime.py` drives a real FastMCP client against a separate `infra/mcp_server.py` process; all 42 counted sub-games were played host-to-host over public tunnels |
| **2** | MUST NOT | Never share memory or variables between the sides | PASS | Each peer owns its own `Observation`, which structurally cannot hold an opponent coordinate; `tests/unit/test_belief_firewall.py`, `tests/integration/test_interop_network.py` |
| **3** | MUST | The orchestrator is the single entry point to the subsystems | PASS | `sdk/sdk.py::AgentSDK` (ADR-1 in `PLAN.md`); `tests/unit/test_sdk.py` |
| **4** | MUST | Manage game states with a proper state machine | PASS | `peer/state_machine.py`, explicit `ALLOWED` transition map |
| **5** | MUST | Reject every illegal state transition | PASS | `peer/state_machine.py` guards each target against `ALLOWED`; `tests/unit/test_state_machine.py` |
| **6** | MUST | Deadline tracking so the agent never hangs waiting on the opponent | PASS | `infra/reliability.py::ReliableCaller` — timeout, retry, backoff, deterministic technical loss; `tests/unit/test_reliability.py` |
| **7** | MUST | Watchdog for process-crash monitoring and controlled data extraction | PASS | `peer/watchdog.py::Watchdog`, wired per sub-game from `watchdog_timeout_sec` in `peer/net_runtime.py` |
| **8** | MUST | Show local truth only in the live UI | PASS | `gui/window.py::local_view`; the README §5.1 screenshot states the guarantee on screen |
| **9** | MUST NOT | Never display the full objective board in the live UI | PASS | `tests/unit/test_gui.py` asserts exactly one player marker is ever drawn |
| **10** | MUST | Use a tunnel to expose the local server to the public internet | PASS | `infra/tunnel.py`; all seven counted matches ran over Cloudflare quick tunnels |
| **11** | MUST | Config file byte-identical on both sides | PASS | `shared/config_hash.py` canonical hash; `config_sha256` identical across all 42 committed configs |
| **12** | MUST | Raise Appendix-F minima only by agreement, never lower them | PASS | `interop/terms.py` defaults to the Appendix-F values; `tests/unit/test_config_required.py` |
| **13** | MUST | Move in orthogonal directions only | PASS | `domain/moveset.py`, `domain/rules.py::is_move_legal`; `tests/unit/test_board_rules.py` |
| **14** | MUST NOT | No diagonal moves | PASS | Move set is `N/S/E/W/STAY`; `strategy/firewall.py` rejects anything else |
| **15** | MUST | Declare every barrier placement openly | PASS | Barrier placement is a committed then revealed wire action; `docs/PRD_commit_reveal_audit.md` |
| **16** | MUST NOT | Never lie about a barrier position | PASS | The barrier cell is inside the committed payload; any mismatch fails the audit |
| **17** | MUST | SHA-256 commit-reveal protocol | PASS | `domain/crypto.py::commit_of`; `tests/unit/test_crypto.py`, `tests/unit/test_protocol_vectors.py` |
| **18** | MUST | Keep the nonce secret until the game ends | PASS | The nonce is disclosed only in the reveal phase; `tests/unit/test_crypto.py::test_fresh_nonce_unique` |
| **19** | MUST | Technical-loss the game on any audit hash mismatch | PASS | `gui/replay_verify.py`, `interop/runtime_audit.py`; `tests/integration/test_mutual_audit.py`, `tests/integration/test_technical_loss.py` |
| **20** | MUST | Build a viewer that replays and verifies the match log | PASS | `replay` CLI plus `gui/tk_replay.py`; README §5.2 screenshot; all 42 committed logs replay `VERIFIED OK` |
| **21** | MUST | Declare truthfully when capturing a thief | PASS | The capture claim is derived from `domain/capture.py`, committed and then revealed |
| **22** | MUST NOT | Never falsely claim a capture | PASS | The claim is bound to the committed payload; `tests/unit/test_capture.py` |
| **23** | MUST | Cryptographically lock the scent-emission model before the game | PASS | Pheromone terms sit inside the hashed 14-term contract (`config_sha256`) |
| **24** | MUST | Cryptographic hardware declaration before the game (Step-0) | PASS | The Step-0 `system_spec` record is the first committed payload of every sub-game — visible in every committed log |
| **25** | SHOULD | Do not hand the move decision to the LLM; use it for text and profiling | PASS | ADR-3 — every move is deterministic Python; the LLM is confined to hints. 0 gameplay tokens across all seven matches |
| **26** | MUST | Communicate in free natural language only | PASS | `strategy/hints.py`; hint payloads are visible in every committed log |
| **27** | MUST NOT | No direct numeric-position protocol | PASS | `strategy/hint_filter.py::leaks_information` rejects any digit at all; `tests/unit/test_hints.py` |
| **28** | MUST | Token-bucket rate limiter for the Gmail reporting path | PASS | `shared/rate_limiter.py::TokenBucket` through `shared/gatekeeper.py`, limits read from `config/game.json` |
| **29** | MUST | DoS detector protecting network resources | PASS | `shared/gatekeeper.py` bounded admission (`concurrent_requests + queue_depth`) raising `QueueFullError` |
| **30** | MUST | Send-only Gmail permission | PASS | `infra/gmail_auth.py` requests the single scope `gmail.send` |
| **31** | MUST | Play the minimum number of games against different groups | PASS | 7 counted series against 7 different groups; the minimum is 2 — README §7.1 |
| **32** | MUST | Report results automatically through the Gmail API | PASS | `infra/gmail_report.py`; sends recorded for all seven matches in `docs/COST_AUDIT.md` |
| **33** | MUST | Format the match report as standard JSON | PASS | `result_<game_id>.json`; committed for G002/G005/G008/G012 under `docs/evidence/` |
| **34** | MUST NOT | Never send a free-text final report — JSON attachment only | PASS | `infra/gmail_report.py` attaches the JSON artifact |
| **35** | MUST | Agree the result with the opponent; each group sends its own report | PASS | `interop/consensus.py`; `results_agreed: true` in all seven result records |
| **36** | MUST | Comprehensive mutual log audit at the end of every game | PASS | `interop/runtime_audit.py`; 42/42 logs verified untampered on both sides |
| **37** | MUST | Declare the true number of games played at the start of each game | PASS | Declared in the Step-0 declaration record of every match |
| **38** | MUST NOT | Never misdeclare the number of games | PASS | The counted record is 7 and is reported as 7 everywhere; no opponent replayed (rule #52) |
| **39** | MUST NOT | Never push secrets or credentials, even to a private repo | PASS | `scripts/secret_scan.py` gates on tracked and unignored files; 0 findings in both repos |
| **40** | MUST | Add credential and secret files to .gitignore | PASS | `.gitignore` excludes `.env`, `*.key`, `*.pem`, `credentials.json`, `token.json` |
| **41** | MUST | Tag the submission version with an annotated Git tag | PARTIAL | `v1.0-submission` exists and is pushed in both repos, but points at a pre-final commit — **HUMAN ACTION B** |
| **42** | MUST | Write a comprehensive academic report in the repository | PASS | `README.md` — 14 sections covering all six §9.4.2 components |
| **43** | MUST | Download the Moodle form, fill it, save as PDF, do not move or alter fields | N/A | Off-platform action that cannot be performed from the repository — **HUMAN ACTION C** |
| **44** | MUST | Each team member submits separately in Moodle | N/A | Off-platform action — **HUMAN ACTION C** |
| **45** | MUST | Enter a unique 8-character group code with no spaces | PASS | `amireman` — exactly 8 characters, no spaces; used as `group_id` in every artifact |
| **46** | MUST | A barrier placed on the thief's current cell counts as a capture | PASS | `domain/capture.py`; `tests/unit/test_board_rules.py` (R46) |
| **47** | MUST | A thief with no legal move is also captured | PASS | `domain/capture.py` enclosure check; `tests/unit/test_board_rules.py` (R47) |
| **48** | MUST | Score every ending per the scoring table (20/5, 10/5, 0/0) | PASS | `domain/scoring.py` with the `scoring` block of `config/game.json`; `tests/unit/test_scoring.py` |
| **49** | MUST | Two repos, README cross-link, two links in Moodle, four links in the JSON | PARTIAL | Two repos and the cross-link are in place (README §6); the result JSON carries all four links. The Moodle half is **HUMAN ACTION C** |
| **50** | MUST | Each repo holds at least README, config/, PRD, PLAN and TODO | PASS | `README.md`, `config/`, `docs/PRD.md` plus six mechanism PRDs, `docs/PLAN.md`, `docs/TODO.md` |
| **51** | MUST | Send the automatic final reports to the agent-report address | PASS | `infra/gmail_auth.py::DEFAULT_RECIPIENT` is the Appendix-F agent-report address |
| **52** | MUST | Exactly one counted game per opponent; uncounted warm-ups are allowed | PASS | 7 opponents, 7 counted series, no repeats; friendlies deliberately excluded from the counted record |
| **53** | MUST | Record the played commit hash in the Step-0 declaration | PASS | `github_commit` appears in every Step-0 payload — visible in every committed log |
| **54** | MUST | Report tokens consumed per sub-game and per series in the final JSON | PASS | `tokens_total` per sub-game and `tokens_total_series` in every result record (0 throughout) |
| **55** | MUST | Give a code-quality self-grade only — never for the league result | PASS | `docs/QUALITY-25010.md` — self-grade 92/100 against the guidelines' enforcement table, with match outcomes explicitly excluded. Entering it on the form is **HUMAN ACTION D** |

**Totals — Appendix E:** PASS 51 · PARTIAL 2 · N/A 2 (both N/A rows are off-platform
Moodle steps).

---

## A2 — §9.4.2: mandatory contents of the academic README

*Source A, §9.4.2, printed p. 81. The rulebook says the absence of any one of these "detracts
from the submission".*

| # | Required component | Status | Evidence |
|---|---|---|---|
| 1 | Dec-POMDP model: state space, observations, uncertainty | PASS | README §1, including the belief-representation subsection |
| 2 | FastMCP orchestration dilemmas: turn management, network-failure handling, Gatekeeper and Orchestrator roles | PASS | README §2 (§2.1–§2.4) |
| 3 | Strategies implemented: heuristics, belief map, LLM policy, optionally Q-learning | PASS | README §3 (§3.1–§3.4) |
| 4 | Learning curves — *if* reinforcement learning was used | N/A | No RL is used. The rule is explicitly conditional; README §4 states the absence and gives the reason (ADR-3) |
| 5 | Screenshots — Live GUI belief map **and** Replay showing `Verified OK` (stated as an absolute requirement) | PASS | README §5.1 → `docs/images/*-gui-belief-map.png`; README §5.2 → `docs/images/*-replay-verified-ok.png` |
| 6 | Link to the companion repository | PASS | README §6, plus the §6.1 interop contract |

Item 4 is the only conditional one in the list ("**if** you trained an RL agent"). No RL is
used, deliberately (ADR-3), and README §4 says so rather than leaving the section blank.

---

## A3 — Appendix C, Table 6: the submission checklist

*Source A, Appendix C §3, printed p. 120. These are the rulebook's threshold conditions,
to be verified before cutting the submission tag.*

| Item | Required status | Status | Evidence |
|---|---|---|---|
| Two GitHub repos accessible to the lecturer | public, or private and shared with the lecturer | FAIL | Both repositories are **private** with the owner as sole collaborator and no pending invitations, so neither accepted form holds and a grader cannot open them — **HUMAN ACTION A** |
| Cross-link between the repos, and two links in the submission | both present | PASS | README §6 links each repo to the other; the Moodle links are **HUMAN ACTION C** |
| Annotated Git tag for the submission version | `v1.0-submission` pushed | PARTIAL | The tag exists and is pushed in both repos but predates the final commits — **HUMAN ACTION B** |
| README report components (chapter 9) | complete in both repos | PASS | All six §9.4.2 components present in both READMEs |
| Belief-map (GUI) screenshot | attached | PASS | `docs/images/police-gui-belief-map.png` and `thief-gui-belief-map.png` |
| Replay screenshot showing `Verified OK` | attached | PASS | `docs/images/*-replay-verified-ok.png`; the tampered counterpart is committed too |
| At least two games against different groups | 2 or more | PASS | 7 counted series against 7 different groups |
| End-of-game e-mail, each group separately | both sides sent | PASS | Sent for all seven counted matches; ledger in `docs/COST_AUDIT.md` |
| No secrets pushed to the repository (.gitignore) | verified | PASS | `scripts/secret_scan.py` reports clean in both repos; nothing sensitive is tracked |

---

## A4 — Appendix F: the mandatory configuration rules

*Source A, Appendix F §2, printed p. 140.*

| # | Rule | Status | Evidence |
|---|---|---|---|
| 1 | Define all Appendix-F values in the config file, identical on both sides and cryptographically locked | PASS | `config/game.json` carries every Appendix-F parameter; `config_sha256` locks the agreed 14 terms |
| 2 | Settings may change per game if the opponent agrees | PASS | `interop/negotiate.py` and `interop/agree.py` |
| 3 | Give every config file a distinct per-game name | PASS | `config_<GID>_g<NN>.json` — 42 such files are now committed |
| 4 | **Attach every game's config file to the GitHub repository** | PASS | **Fixed during this audit.** All 42 per-game configs are committed under `docs/evidence/<GID>/`; before this pass none were |
| 5 | E-mail the lecturer the commit used for each game | PASS | `github_commit` appears in Step-0 and in the mailed result report |

### Appendix-F parameter conformance

Every value in `config/game.json` was compared field-by-field against Tables 13–19. All 30
parameters match the mandatory table exactly; no `קבוע` (fixed) parameter deviates and no
`מינימום` parameter is below its floor.

| Table | Parameters | Conformance |
|---|---|---|
| 13 — board, axes, start positions | grid 7, agents 2, thief (3,3), cop (0,0), origin top-left, index 0 | exact |
| 14 — arena and verbal hints | setting configurable, hint cap 15 words | exact |
| 15 — movement and barriers | N/S/E/W/STAY, 14 barriers, 35 moves, survival 35 | exact |
| 16 — pheromones | intensity 0.9, decay 0.10, field 5×5 | exact |
| 17 — scoring | 20/5 capture, 5/10 survival, tie 2, technical 0 | exact |
| 18 — network and league | 6 sub-games, diversity 10, min 2, max 10, 200k token budget | exact |
| 19 — rate limiter and gatekeeper | 30 rpm, 2 concurrent, 5 s backoff, 3 retries, queue 100, 30 s timeout, 60 s watchdog | exact |

---

## A5 — §11.5: the final pre-submission checklist and the Moodle list

*Source A, §11.5, printed pp. 97–98.*

| Checklist item | Status | Evidence |
|---|---|---|
| Base logic works — full race without crashing, scoring enforced | PASS | `domain/`, `sim/`; 42 real sub-games completed without a crash |
| FastMCP over a public URL, not just localhost | PASS | All seven counted matches ran host-to-host over public tunnels |
| Commit-reveal active and the audit passes with no forgery detected | PASS | 42/42 logs verified untampered on both sides |
| Scent map and belief map computed and actually influencing decisions | PASS | `domain/smell.py`, `strategy/belief.py`; `docs/PRD_scent_stigmergy.md`, `docs/PRD_belief_map.md` |
| Live GUI and Replay App with `Verified OK` | PASS | README §5.1 and §5.2 with committed screenshots |
| Gmail API JSON reporting from both sides | PASS | Both groups reported separately for all seven counted matches |
| GitHub repo with a Git tag and an academic README | PARTIAL | README complete; the tag needs re-pointing — **HUMAN ACTION B** |
| At least the minimum number of races against different opponents | PASS | 7 against 7 different groups; minimum is 2 |

### Moodle submission list (§11.5, items א–ו)

| Item | Requirement | Status | Evidence |
|---|---|---|---|
| א | A folder of markdown PRD files is attached to GitHub and the repo root is readable | PASS | `docs/` holds `PRD.md` plus six mechanism PRDs; `README.md` at the root |
| א (2) | The whole project complies with the course-introduction software guidelines | PASS | Source B audited in full below; graded per §11.5(א) |
| ב | Submit through Moodle; the code is on GitHub and shared with the lecturer | FAIL | Sharing has not happened — **HUMAN ACTION A**; Moodle submission is **HUMAN ACTION C** |
| ג | Each team member submits separately in Moodle | N/A | Off-platform — **HUMAN ACTION C** |
| ד | A unique 8-character group code with no spaces | PASS | `amireman` |
| ה | Fill the Word template and save as PDF without moving or changing fields | N/A | Off-platform — **HUMAN ACTION C** |
| ו | Self-grade code quality only, never the league result | PASS | `docs/QUALITY-25010.md` self-grade section; entering it is **HUMAN ACTION D** |

---

## B — Software guidelines V3, clause by clause

*Source B, all 39 pages. Binding by reference through §11.5(א) of Source A.*

| § | Criterion | Classification | Status | Evidence |
|---|---|---|---|---|
| 2.1 | README.md at the root as a full user manual | MANDATORY_FOR_PROJECT | PASS | README §13 — system requirements, step-by-step install, env vars, troubleshooting, usage, CLI flags, examples, config guide, contribution guidelines, credits and licence |
| 2.2 | docs/PRD.md — goals, KPIs, acceptance criteria, functional and non-functional requirements, assumptions, milestones | MANDATORY_FOR_PROJECT | PASS | `docs/PRD.md` with numbered FR-* requirements |
| 2.2 | docs/PLAN.md — C4, UML, deployment diagrams, ADRs with rationale and trade-offs, API/contract docs | MANDATORY_FOR_PROJECT | PASS | **Improved in this audit.** `docs/PLAN.md` now opens with nine ADRs, each with the rejected alternative and the price paid; C4 L1–L4 and the deployment view are in `docs/ARCHITECTURE.md` (mermaid); contracts in `docs/API.md` |
| 2.2 | docs/TODO.md — tasks with priority and status, phases, ownership, definition of done | MANDATORY_FOR_PROJECT | PASS | **Fixed in this audit.** 1,110 atoms; checkboxes were all unticked and are now synchronised to the `Status:` field (332 `[x]`), with a preamble that explains what the 766 open atoms do and do not mean |
| 2.3 | Dedicated PRD per algorithm / central mechanism | MANDATORY_FOR_PROJECT | PASS | Six: `PRD_ringbreaker`, `PRD_antisqueeze`, `PRD_belief_map`, `PRD_scent_stigmergy`, `PRD_commit_reveal_audit`, `PRD_api_gatekeeper` — each with theory, I/O, constraints, rejected alternatives and success criteria |
| 2.4 | Recommended project layout (src/, tests/, docs/, config/, results/, assets/, notebooks/) | APPLICABLE_EXCELLENCE | PASS | `src/`, `tests/unit` + `tests/integration`, `docs/`, `config/`, `schemas/`, `scripts/`, `evidence/`; analysis notebook at `docs/research/results_analysis.ipynb` and figures under `docs/images/` rather than separate `notebooks/` and `assets/` trees |
| 2.5 | Mandatory workflow: PRD → PLAN → TODO → mechanism PRDs → approve → build | APPLICABLE_EXCELLENCE | PARTIAL | PRD/PLAN/TODO and the mechanism PRDs all precede the code and drove it, but the ADRs were written retrospectively in this audit. Recorded honestly in the self-grade (−3) |
| 3.1 | Modular project structure with clear separation of concerns | MANDATORY_FOR_PROJECT | PASS | `domain` / `strategy` / `peer` / `interop` / `infra` / `gui` / `sdk` / `shared`; ADR-2 keeps `domain` free of upward dependencies, independently confirmed by the Graphify extraction |
| 3.2 | Every code file at most 150 lines (blanks and comments excluded) | MANDATORY_FOR_PROJECT | PASS | `scripts/check_line_count.py` enforces the **stricter** physical-line reading in CI — 0 violations across every tracked `.py` (ADR-9) |
| 3.3 | Docstrings on every function, class and module; comments explaining *why* | MANDATORY_FOR_PROJECT | PASS | Module and public-API docstrings throughout; the Ruff `D`-adjacent selection plus review keeps them current |
| 4.1 | SDK architecture — all business logic reachable through an SDK layer; no logic in GUI/CLI | MANDATORY_FOR_PROJECT | PASS | `sdk/sdk.py::AgentSDK` is the single facade (ADR-1); `commands*.py` and `gui/` delegate to it; `tests/unit/test_sdk.py` |
| 4.2 | OOP, no duplicated code; extract at two or more copies; mixin rules | MANDATORY_FOR_PROJECT | PASS | `strategy/base.py::BrainBase` is the shared base for the whole portfolio; `interop/` shares wire helpers. `docs/REUSE-REGISTER.md` records what was consolidated |
| 5.1 | Central API Gatekeeper — no direct external calls bypass it | MANDATORY_FOR_PROJECT | PASS | `shared/gatekeeper.py` in front of the outgoing report path and the peer endpoint; `docs/PRD_api_gatekeeper.md` |
| 5.2 | Rate limits read from configuration, never hardcoded | MANDATORY_FOR_PROJECT | PASS | `config/game.json` → `rate_limiter_gatekeeper` (rpm, concurrency, backoff, retries, queue depth) |
| 5.3 | Overflow queued, not rejected; bounded depth; backpressure | MANDATORY_FOR_PROJECT | PASS | Admission up to `concurrent_requests + queue_depth`, then an explicit `QueueFullError` rather than a crash (ADR-8) |
| 6.1 | TDD — red, green, refactor; every module has a test file; happy and error paths; mocks for externals | APPLICABLE_EXCELLENCE | PARTIAL | Coverage of happy and error paths is comprehensive and external services are mocked, but tests were largely written alongside rather than strictly test-first. Declared in the self-grade (−3) |
| 6.2 | Global test coverage at least 85%, and the suite must fail below it | MANDATORY_FOR_PROJECT | PASS | **Improved in this audit.** Police 87.48%, Thief 87.99% (statement + branch). `fail_under = 85` was configured but CI ran plain `pytest`; the CI step now runs `pytest --cov`, so the gate actually fires |
| 6.3 | Edge cases identified and documented; defensive programming; graceful degradation | MANDATORY_FOR_PROJECT | PASS | `docs/THREAT-MODEL.md`; the legality firewall degrades instead of raising (ADR-4); malformed input, oversized messages, non-finite scent, replay and equivocation all have tests |
| 6.4 | Documented expected results, automated test reports, pass/fail logs | APPLICABLE_EXCELLENCE | PASS | `docs/TESTING.md`; CI publishes the run; `tests/unit/protocol_vectors.py` holds reference vectors |
| 7.1 | Zero Ruff violations | MANDATORY_FOR_PROJECT | PASS | `uv run ruff check .` clean in both repos, plus `ruff format --check`; selection `E,F,W,I,N,UP,B,SIM,C4` |
| 7.2 | No hardcoded configurable values | MANDATORY_FOR_PROJECT | PASS | Game and limit values come from `config/game.json`; only protocol/mathematical constants and enum values live in `constants.py` |
| 7.3 | Versioned configuration hierarchy; .env for secrets; .env-example committed | MANDATORY_FOR_PROJECT | PASS | **Fixed in this audit.** `config/game.json` is versioned and schema-validated; `.env-example` documented only `ANTHROPIC_API_KEY`, which the code never reads — it now lists all 13 real variables with placeholders and defaults |
| 7.4 | No secrets in the project; .gitignore covers .env/*.key/*.pem/credentials.json | MANDATORY_FOR_PROJECT | PASS | Verified by scan; `.gitignore` complete; least-privilege documented in `docs/GMAIL-OAUTH.md` (send-only scope) |
| 8.1 | Explicit version tracking starting at 1.00, validated at startup | MANDATORY_FOR_PROJECT | PASS | `shared/version.py` — `CODE_VERSION = "1.00"`, `CONFIG_VERSION`, and `check_config_version` fails closed at load |
| 8.2 | Clear commit history, feature branches, tagging of major versions | APPLICABLE_EXCELLENCE | PASS | Descriptive commit subjects; feature branches (`improve/*`, `championship/*`) merged into `master`; `v1.0-submission` tag (see HUMAN ACTION B) |
| 8.3 | Prompt book — the prompt-engineering log | APPLICABLE_EXCELLENCE | PASS | `docs/PROMPTS.md` — representative prompts, three iterations where the first answer was wrong, and the lessons drawn |
| 8.4 | uv is mandatory; no pip, venv or `python -m`; pyproject.toml is the single source; uv.lock committed | MANDATORY_FOR_PROJECT | PASS | `pyproject.toml` + `uv.lock`, no `requirements.txt`; every documented command is `uv run …`; CI uses `astral-sh/setup-uv` |
| 9.1 | Parameter exploration and sensitivity analysis (OAT, variance-based, partial derivatives) | MANDATORY_FOR_PROJECT | PASS | OAT sweep — 4 parameters × 4 opponents × 200 seeds, 68 points (`docs/research/oat_sensitivity.csv`); answered as **RQ2** in README §12.1 |
| 9.2 | Results-analysis notebook with methodical analysis, algorithm comparison, LaTeX equations, citations | APPLICABLE_EXCELLENCE | PASS | `docs/research/results_analysis.ipynb` — estimator choice, strategy comparison, OAT, horizon interaction and the official result, with references |
| 9.3 | Quality visualisation: clear labels, consistent accessible colours, legends, high resolution | MANDATORY_FOR_PROJECT | PASS | Three committed figures with titles, axis labels, units, legends and Wilson intervals (1091×754 to 3178×727), regenerable via `scripts/make_charts.py` |
| 10.1 | Usability criteria and Nielsen's ten heuristics | APPLICABLE_EXCELLENCE | PASS | `docs/GUI-GUIDE.md` walks the heuristics; system status, error prevention and recognition-over-recall are visible in the §5 screenshots |
| 10.2 | Interface documentation: screenshot of every screen and state, workflows, accessibility | APPLICABLE_EXCELLENCE | PARTIAL | `docs/GUI-GUIDE.md` covers every screen and state with committed captures, and states plainly that no assistive-technology testing was done |
| 11.1 | Cost breakdown: input/output tokens, cost per million, total by model | MANDATORY_FOR_PROJECT | PASS | README §11 and `docs/COST_AUDIT.md` — measured figures, actual and API-equivalent kept in separate rows and never summed, with the deduplication method stated |
| 11.2 | Budget management: forecast, real-time monitoring, overrun alerts | APPLICABLE_EXCELLENCE | PARTIAL | The token budget per series is a config parameter and gameplay consumption is 0, so there is nothing to alert on; forecasting and unknowns are covered in `COST_AUDIT.md` §7. No live monitoring dashboard exists |
| 12.1 | Extension points: plugin architecture, lifecycle hooks, middleware | APPLICABLE_EXCELLENCE | PASS | `strategy/registry.py` is a plugin registry; a new brain is a `BrainBase` subclass selected by config key — exactly the Appendix-F Table 22 extension mechanism |
| 12.2 | Maintainability: modularity, reuse, analysability, testability | MANDATORY_FOR_PROJECT | PASS | `docs/QUALITY-25010.md` §7 maps this to evidence |
| 13.1 | ISO/IEC 25010 — all eight product-quality characteristics | APPLICABLE_EXCELLENCE | PASS | `docs/QUALITY-25010.md` maps all eight to checkable evidence and names two honest weak points |
| 14.1 | pyproject.toml with name, version, description, author, licence, dependencies | MANDATORY_FOR_PROJECT | PASS | All present; **licence file added in this audit** (`LICENSE`) and linked from README §13.6 |
| 14.2 | __init__.py in the root package and every sub-package; __all__ and __version__ | MANDATORY_FOR_PROJECT | PASS | Present throughout; `__init__.py` exports `AgentSDK`, `CODE_VERSION`, `__version__` |
| 14.3 | Relative or package-qualified imports only; never absolute machine paths | MANDATORY_FOR_PROJECT | PASS | All intra-package imports are relative; no machine-specific path appears in any tracked file |
| 15 | Parallel processing and thread safety | NOT_APPLICABLE | N/A | The rulebook mandates a strictly turn-based protocol with one decision per turn per agent, so CPU parallelism would change protocol semantics. Concurrency is genuinely present but as bounded async I/O — `anyio` in `infra/reliability.py`, with concurrency capped by the gatekeeper — which is the I/O-bound case §15.1 describes |
| 16 | Building-block design: declared inputs, outputs, setup, validation, single responsibility, testability | APPLICABLE_EXCELLENCE | PASS | `BrainBase` declares Input `Observation`, Output `Action`, Setup role/seed/config, with validation delegated to the firewall; `Gatekeeper` and `ReliableCaller` follow the same shape and are dependency-injected in tests |
| 17 | Final checklist across all six areas | MANDATORY_FOR_PROJECT | PASS | This document, plus `docs/COMPLIANCE-CHECKLIST.md` and `docs/SUBMISSION-CHECKLIST.md` |
| 19 | Not every clause is obligatory; depth is what is graded | — | — | Recorded verbatim so that the four `PARTIAL` rows above are read as declared shortfalls rather than hidden ones |

### The one NOT_APPLICABLE row, with its reason

**§15 — parallel processing and thread safety.** Source B asks for multiprocessing or
multithreading with explicit thread-safety measures. Source A mandates a strictly turn-based
protocol: each agent makes exactly one decision per turn, commits it, and waits for the peer.
Adding CPU parallelism to the decision path would change protocol semantics and risk a
technical loss, so it is not implemented — and this audit was instructed not to build
architecture that merely satisfies a generic guideline. The concurrency that *is* present is
the I/O-bound kind §15.1 itself describes: `anyio`-based async transport in
`infra/reliability.py`, with bounded concurrency enforced by the gatekeeper and per-request
deadlines. Classified `NOT_APPLICABLE` rather than `FAIL` because Source A wins on conflict.

---

## Verification method

Every row above was checked in one of four ways, and no row rests on a README assertion:

| Method | Applied to |
|---|---|
| **Command executed during this audit** | Test suites (750 tests, 87.99% coverage), `ruff check`, `ruff format --check`, the 150-line gate, the secret scan, and a full replay of all 42 committed sub-game logs |
| **File and code inspection** | Every rule mapped to a named module, class or function; the file was opened and the mechanism confirmed |
| **Data re-derivation** | Every research figure recomputed from the committed CSVs; every counted score re-derived from the signed `result_*.json` and cross-checked against the per-sub-game logs |
| **External state query** | Repository visibility, collaborator list and pending invitations queried through the GitHub API — which is how the mandatory FAIL was found |

Reproduce the mechanical half:

```bash
uv run pytest --cov=src --cov-report=term-missing   # 750 tests, 87.99%, gate at 85%
uv run ruff check . && uv run ruff format --check .
uv run python scripts/check_line_count.py
uv run python scripts/secret_scan.py
for g in G002 G005 G008 G012 G020 G040 G077; do
  uv run python -m thief_agent replay --dir docs/evidence/$g --game-id $g
done
```

---

## What this audit changed

| Area | Finding | Fix |
|---|---|---|
| Appendix F rule 4 | **No per-game config file was committed for any match** — a mandatory rule, previously unmet in both repos | All 42 authentic `config_<GID>_g<NN>.json` committed under `docs/evidence/` |
| Match evidence | Only 3 of 7 counted matches had committed logs | `G002`, `G005`, `G008`, `G012` logs and signed results added — all 24 replay `VERIFIED OK` |
| README §14 | Claimed "5 counted, 5 different groups" while §7.1 said seven | Corrected to 7, and the checklist's access and tag rows made truthful |
| README §11 | Claimed "2 public repos" and free unmetered Actions | Corrected — the repos are private |
| README §12.4 | Claimed no `src/` file had changed since the Graphify snapshot; 26 had | Corrected, with the two structural findings re-verified by hand against the current tree |
| README §7.2 | Reported a 100/100 benchmark with no committed source and a reproduction command that does not produce it | Provenance stated: not reproducible from this repo, with the counted G020 result given as the checkable evidence instead |
| README §7.3 | Stated a stale test count | Corrected to the measured 750 |
| `.env-example` | Documented one variable the code never reads, and none of the 13 it does | Rewritten with every real variable, its default and its purpose |
| CI | README claimed the coverage gate was enforced; CI ran plain `pytest`, so `fail_under` never fired | CI now runs `pytest --cov`, making the claim true and satisfying Source B §6.2 |
| `scripts/secret_scan.py` | Failed on git-ignored local credentials, so the gate was red on any machine able to send mail — while not checking whether a secret was actually *tracked* | Rewritten to gate on what git would publish; four new regression tests |
| `docs/TODO.md` | All 1,110 atoms rendered unchecked, including 332 recorded `DONE`; the closing note still listed finished work as deferred | Checkboxes synchronised to `Status:`; preamble explains the 766 open atoms; closing note updated |
| `docs/PLAN.md` | No ADRs, which Source B §2.2 requires | Nine ADRs added, each with the rejected alternative and the trade-off accepted |
| `LICENSE` | Absent, though Source B §17.6 requires a licence | Added, matching the "all rights reserved, staff may evaluate" position README already stated |
| Self-grade | Rule #55 requires a code-quality self-grade; none existed | Added to `docs/QUALITY-25010.md` — 92/100, with the eight lost points itemised |
| Repository access | **Both repos private, lecturer has no access** | Cannot be fixed here — **HUMAN ACTION A** |
