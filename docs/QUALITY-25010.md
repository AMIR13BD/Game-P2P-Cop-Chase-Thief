# Product quality — ISO/IEC 25010 mapping

The software guidelines (§13) ask for the project to be assessed against the eight product
quality characteristics of **ISO/IEC 25010:2011**. This document maps each characteristic
to concrete, checkable evidence in this repository. Where a sub-characteristic is weak or
out of scope, it says so — a self-assessment that scores itself full marks everywhere is
not an assessment.

Legend: **Strong** = enforced automatically or demonstrated by a counted match ·
**Adequate** = implemented and tested, not exhaustively · **Limited** = known gap.

---

## 1. Functional suitability

*Completeness, correctness, appropriateness.*

| Evidence | Where |
|---|---|
| All 14 signed contract terms implemented and validated on load | [`interop/terms.py`](../src/thief_agent/interop/terms.py), [`shared/config_validate.py`](../src/thief_agent/shared/config_validate.py) |
| Both roles implemented for six-sub-game alternation | [`strategy/`](../src/thief_agent/strategy/), README §3 |
| Correctness demonstrated in real league play — G020, 6–0, all audits verified | [`evidence/G020/`](evidence/G020/), README §7.1 |
| Rule compliance (R46 pounce, R47 enclosure, orthogonal-only movement) | `tests/unit/test_board_rules.py` |
| 750 automated tests, 87%+ statement coverage | CI, README §7.3 |

**Assessment: Strong.** The decisive evidence is external: a counted match against another
team, audited by both sides.

## 2. Performance efficiency

*Time behaviour, resource utilisation, capacity.*

| Evidence | Where |
|---|---|
| Decision latency p95 ≈ 3 ms against a 30 s protocol deadline (~4 orders of margin) | [`research/oat_sensitivity.csv`](research/oat_sensitivity.csv) `decision_ms_p95` |
| Zero timeouts across 3,600 benchmark scenario-plays | [`evidence/scenario_matchups.csv`](../evidence/scenario_matchups.csv) |
| Bounded admission capacity; overload refused rather than queued without limit | [`shared/gatekeeper.py`](../src/thief_agent/shared/gatekeeper.py), [`PRD_api_gatekeeper.md`](PRD_api_gatekeeper.md) |
| Sparse scent grid — negligible traces dropped below 1e-9 | [`domain/smell.py`](../src/thief_agent/domain/smell.py) |
| Zero gameplay LLM tokens — inference cost is not on the critical path | [`COST_AUDIT.md`](COST_AUDIT.md) |

**Assessment: Strong** for time behaviour. **Limited** on capacity headroom: measured only
up to 13×13 boards; behaviour beyond that is untested.

## 3. Compatibility

*Co-existence, interoperability.*

| Evidence | Where |
|---|---|
| Byte-identical canonical JSON so both peers hash the same bytes | [`domain/crypto.py`](../src/thief_agent/domain/crypto.py) |
| Wire format interoperable with the reference implementation | [`interop/wire.py`](../src/thief_agent/interop/wire.py), [`REUSE-REGISTER.md`](REUSE-REGISTER.md) |
| Negotiation refuses on protocol/schema mismatch instead of guessing | [`peer/handshake.py`](../src/thief_agent/peer/handshake.py) |
| Proven against four independent teams' implementations | README §7.1 (5 counted matches) |
| Version change does not break peers — `code_version` is reported, never compared | [`shared/version.py`](../src/thief_agent/shared/version.py) |
| Scent emission has an interop-compatible mode alongside our own | `compat_update`, [`PRD_scent_stigmergy.md`](PRD_scent_stigmergy.md) |

**Assessment: Strong.** Interoperability is the hardest thing in this project to fake and
the easiest to verify: five counted matches with four different opponent codebases.

## 4. Usability

*Learnability, operability, error protection, accessibility.*

| Evidence | Where |
|---|---|
| Live GUI with belief heatmap and green/grey turn indicator | [`gui/tk_live.py`](../src/thief_agent/gui/tk_live.py), README §5.1 |
| Replay Viewer with Previous/Next and an integrity badge | [`gui/tk_replay.py`](../src/thief_agent/gui/tk_replay.py), README §5.2 |
| Error protection: input locked outside move-accepting states | `status_banner.input_locked` |
| Workflow, interaction and accessibility notes | [`GUI-GUIDE.md`](GUI-GUIDE.md) |
| Operational runbook | [`OPERATIONS.md`](OPERATIONS.md) |
| README as user manual — install, usage, configuration, troubleshooting | README §10, §12 |

**Assessment: Adequate.** Colour is never the sole channel (badges carry text, cells carry
numerals), but no screen-reader or keyboard-navigation testing has been performed — see
[`GUI-GUIDE.md`](GUI-GUIDE.md) §4 for the honest list.

## 5. Reliability

*Maturity, availability, fault tolerance, recoverability.*

| Evidence | Where |
|---|---|
| Watchdog and per-turn deadline enforcement | [`peer/watchdog.py`](../src/thief_agent/peer/watchdog.py), [`peer/deadline.py`](../src/thief_agent/peer/deadline.py) |
| Reconnect without aborting the series | [`peer/net_reconnect.py`](../src/thief_agent/peer/net_reconnect.py), `tests/unit/test_reconnect_series.py` |
| A sub-game transport failure degrades to a technical result, not a crash | [`peer/technical.py`](../src/thief_agent/peer/technical.py) |
| Malformed or missing logs handled fail-closed in the replay viewer | `gui/replay_data.load_log` |
| Determinism under a fixed seed — reproducible failures | `tests/integration/test_determinism.py` |
| Zero technical losses across 3,600 benchmark plays | `evidence/scenario_matchups.csv` |

**Assessment: Strong.** Fault tolerance was exercised in real conditions, including a
tunnel drop mid-series during league play.

## 6. Security

*Confidentiality, integrity, authenticity, accountability.*

| Evidence | Where |
|---|---|
| Commit-reveal over SHA-256 with a fresh 128-bit nonce per move | [`PRD_commit_reveal_audit.md`](PRD_commit_reveal_audit.md) |
| Constant-time digest comparison (`secrets.compare_digest`) | [`domain/crypto.py`](../src/thief_agent/domain/crypto.py) |
| Mutual post-match audit and result consensus | [`peer/audit.py`](../src/thief_agent/peer/audit.py), [`interop/consensus.py`](../src/thief_agent/interop/consensus.py) |
| Bearer-token auth on the MCP endpoint with revocation | [`security/auth.py`](../src/thief_agent/security/auth.py) |
| OAuth 2.0 with `gmail.send` scope only — no password, least privilege | [`GMAIL-OAUTH.md`](GMAIL-OAUTH.md) |
| Zero secrets ever committed, `.gitignore` + automated scan in CI | [`scripts/secret_scan.py`](../scripts/secret_scan.py), README §9 |
| Belief firewall — an `Observation` structurally cannot carry an opponent coordinate | [`strategy/firewall.py`](../src/thief_agent/strategy/firewall.py) |
| Threat model documented | [`THREAT-MODEL.md`](THREAT-MODEL.md) |

**Assessment: Strong.** Stated limitation: the Step-0 declaration binds a claimed Git
commit, which is socially verifiable rather than cryptographically bound to the running
binary ([`PRD_commit_reveal_audit.md`](PRD_commit_reveal_audit.md) §3).

## 7. Maintainability

*Modularity, reusability, analysability, modifiability, testability.*

| Evidence | Where |
|---|---|
| Every tracked Python file ≤ 150 physical lines, enforced in CI | [`scripts/check_line_count.py`](../scripts/check_line_count.py) |
| Layered packages: `domain` / `strategy` / `peer` / `interop` / `infra` / `gui` / `sdk` | README §8 |
| All business operations reached through the `AgentSDK` facade | [`sdk/sdk.py`](../src/thief_agent/sdk/sdk.py) |
| Strategy registry — new brains added without touching the engine | [`strategy/registry.py`](../src/thief_agent/strategy/registry.py) |
| Ruff lint + format, zero violations, enforced in CI | `pyproject.toml`, CI |
| Presentation strictly separated from model (GUI is a painter over pure view-models) | [`gui/live_model.py`](../src/thief_agent/gui/live_model.py), [`gui/replay_model.py`](../src/thief_agent/gui/replay_model.py) |
| Per-mechanism PRDs recording rationale and rejected alternatives | `docs/PRD_*.md` |
| Explicit code/config versioning with startup validation | [`shared/version.py`](../src/thief_agent/shared/version.py) |

**Assessment: Strong.** The 150-line ceiling is the load-bearing constraint: it forces a
module to do one thing, and it is machine-enforced rather than aspirational.

## 8. Portability

*Adaptability, installability, replaceability.*

| Evidence | Where |
|---|---|
| Pure Python 3.13, two runtime dependencies (`fastmcp`, `openai`) | `pyproject.toml` |
| Reproducible install from a committed lockfile — `uv sync` | `uv.lock` |
| No absolute paths; all package-relative imports and file access | guidelines §14.3 checklist |
| Behaviour configured by data, never hardcoded | `config/game.json`, `shared/config_spec.py` |
| Optional integrations isolated behind extras (`--extra gmail`) and lazy imports | `pyproject.toml`, `advisor/client.py` |
| Headless text renderer alongside the Tk GUI for environments with no display | `gui/window.py` vs `gui/tk_live.py` |

**Assessment: Adequate.** Developed and verified on Linux/WSL2 with Python 3.13; not
tested on macOS or native Windows, and the Tk GUI needs a display server (the headless
path exists precisely for that reason).

---

## Summary

| Characteristic | Assessment |
|---|---|
| Functional suitability | Strong |
| Performance efficiency | Strong (capacity untested beyond 13×13) |
| Compatibility | Strong |
| Usability | Adequate (no assistive-technology testing) |
| Reliability | Strong |
| Security | Strong (commit-binding is social, not cryptographic) |
| Maintainability | Strong |
| Portability | Adequate (single platform verified) |

The two honest weak points are **accessibility testing** and **cross-platform
verification**. Both are stated rather than hidden, and neither affects league play.

---

## Code-quality self-grade (rulebook rule #55 / §11.5 item ו)

The rulebook requires a self-grade that scores **code quality only** — explicitly *not* the
league result. That separation is the whole point of the rule: a team that went 6–0 and a team
that lost every match can have identically good code, and scoring the scoreboard would measure
the wrong thing. **Nothing in this section refers to match outcomes.** The league record lives
in README §7.1 and is deliberately excluded here.

Scored against the software guidelines' own enforcement table (§19.1), which is the checklist
this project is graded on:

| Guideline requirement | Threshold | Measured | Self-score |
|---|---|---|---|
| Test coverage | ≥ 85% | **87.99%** statement + branch, gate enforced in CI | 5 / 5 |
| Ruff violations | 0 | **0** on every tracked file | 5 / 5 |
| File size | ≤ 150 lines | **0 violations**, enforced on *physical* lines (stricter than §3.2) | 5 / 5 |
| Secrets in source | 0, plus `.env-example` | **0**; scanner gates on what git would publish | 5 / 5 |
| Package manager | everything through `uv` | `pyproject.toml` + `uv.lock`, no `pip`/`requirements.txt` | 5 / 5 |
| SDK architecture | all business logic behind the SDK | `AgentSDK` is the single facade (ADR-1) | 5 / 5 |
| API gatekeeper | every external call through it | token bucket + bounded queue, limits from config | 5 / 5 |
| Rate limits from config | not hardcoded | `config/game.json` → `rate_limiter_gatekeeper` | 5 / 5 |
| Version tracking | starts at 1.00 | `shared/version.py`, config version validated at load | 5 / 5 |
| OOP / no duplication | extract at 2+ copies | shared bases and mixins; no duplicated protocol logic | 4 / 5 |
| TDD | tests with or before code | 750 tests, happy and error paths, mocks for externals — but written alongside rather than strictly red-green-refactor | 4 / 5 |
| Documentation | PRD, PLAN, TODO, per-mechanism PRDs, prompt book | all present; ADRs added late, in this audit | 4 / 5 |
| Research and visualisation | experiments, sensitivity, notebook, charts | 4 research questions answered from committed CSVs; labelled charts; notebook | 5 / 5 |
| Cost analysis | token ledger and optimisation | full ledger, actual vs API-equivalent kept separate | 5 / 5 |

Per-criterion the table above scores **67 / 70** — eleven rows at 5, three at 4 — which is
95.7%. That number reflects the *enforceable* criteria only, and every one of those is
machine-checked, so it flatters the areas no gate can measure. The three process weaknesses
below are not visible to any gate, and they are real, so the figure entered on the form marks
them down deliberately rather than reporting the mechanical score:

**Self-grade: 92 / 100** — 95.7% on the enforced criteria, less a further ~4 points for the
three process shortfalls named next.

**Where those points went, stated rather than rounded away.** The three sub-5 rows expand into
three areas that are honestly short of the standard:

1. **TDD discipline (−3).** Tests are comprehensive and cover error paths, but they were
   largely written alongside implementation rather than strictly red-first. The guidelines ask
   for red-green-refactor as a *process*, and the git history does not demonstrate it.
2. **Documentation process (−3).** Every mandatory document exists, but the ADRs
   ([`PLAN.md`](PLAN.md)) were written retrospectively during this audit rather than before the
   code, which inverts the §2.5 workflow. `docs/TODO.md` also carries 766 planned atoms whose
   named files were never created — reconciled and explained rather than deleted.
3. **Coverage distribution (−2).** The 87.99% global figure clears the bar, but it is not
   evenly spread: `strategy/predict.py` sits at 26% and `strategy/search.py` at 61%, and
   `sim/opponents/uoh.py` is at 0% — an unused sparring adapter that should be either exercised
   or removed.

Two further known weaknesses are recorded in the summary above and not double-counted here:
no assistive-technology testing, and verification on a single platform (Linux/WSL2, Python
3.13).
