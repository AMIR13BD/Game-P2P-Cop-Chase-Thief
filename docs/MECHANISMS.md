# Per-mechanism PRDs

Concise product/requirement notes for each core mechanism: the user problem, the
requirement, the design, and the acceptance evidence (tests). This satisfies the
per-mechanism documentation requirement.

## Commit-reveal integrity (`domain/crypto`, `peer/audit`, `peer/sealing`)
- Requirement: a peer cannot forge or retro-edit a move; both peers can audit afterwards.
- Design: per turn, publish `commit = SHA256(canonical_json(payload)|nonce)`; reveal the
  nonce at the final audit; recompute and compare.
- Acceptance: `test_crypto`, `test_step0_audit`, `test_mutual_audit` (tamper -> fail closed).

## Two-peer final confirmation (`report/confirm`)
- Requirement: each peer independently confirms the agreed result; neither can fabricate
  the other's confirmation.
- Design: role-symmetric canonical `final`; each peer signs `{group, final_sha256}` with
  its OWN key; exchange over the `confirm` tool; verify under the peer's key; require one
  matching hash + two distinct peers.
- Acceptance: `test_confirm`, `test_rehearsal`, `test_e2e_network` (live exchange).

## Reliability & DoS resistance (`infra/reliability`, `peer/watchdog`, `shared/gatekeeper`, `infra/idempotency`)
- Requirement: survive drops/latency/floods without illegal moves or false success.
- Design: timeout + bounded retry + backoff + correlation; per-sub-game watchdog;
  concurrency/queue token-bucket; server idempotency keyed by (token, request_id).
- Acceptance: `test_reliability`, `test_e2e_fault`, `test_idempotency*`, `test_gatekeeper_deadline`.

## Scent, belief & strategy portfolio (`domain/smell`, `strategy/*`)
- Requirement: strong, legal, deadline-bounded play for both roles using only legal data.
- Design: stigmergic scent -> normalized belief; Police (intercept/barrier/herd/hybrid)
  and Thief (escape/evade/entropy/endgame/hybrid) over shared graph/search algorithms;
  every action through the firewall + guaranteed fallback.
- Acceptance: `test_police_portfolio`, `test_thief_portfolio`, `test_stress` (0 illegal/diagonal).

## Adaptive meta-controller (`strategy/meta`, `strategy/registry`)
- Requirement: pick the right strategy per game state; deterministic; bounded; logged.
- Design: rule-based selection over role/belief/remaining-turns/score/profile/barrier
  state with seeded controlled exploration; firewall-enforced; per-turn reason log.
- Acceptance: `test_meta`, `test_production_integration`.

## Audit-gated profiling (`strategy/profiling`)
- Requirement: learn opponent tendencies without touching hidden/unaudited data; reset
  per opponent.
- Design: `observe_subgame` runs `run_audit` and rejects on failure; per-opponent
  `ProfileStore`; features from revealed records only.
- Acceptance: `test_profiling`, `test_rehearsal` (forged evidence rejected).

## Free-language hints & deception (`strategy/hints`, `strategy/hint_filter`)
- Requirement: legal NL hints (≤15 words), no leakage, credibility only from audit.
- Design: truthful/vague/deceptive generation; digit/coordinate/secret filter;
  `biased_target` acts on a hint only above audited credibility 0.5.
- Acceptance: `test_hints`, `test_redteam`.

## Gmail reporting & connectivity (`infra/gmail_*`, `infra/tunnel`)
- Requirement: send the signed JSON report via Gmail API after a valid counted match;
  provider-neutral public connectivity with TLS.
- Design: gated + idempotent send, dry-run/draft never sends, `gmail.send` scope only;
  tunnel adapter with endpoint/TLS validation and health check.
- Acceptance: `test_gmail`, `test_tunnel` (+ BLOCKED-EXTERNAL for real OAuth/URL).
