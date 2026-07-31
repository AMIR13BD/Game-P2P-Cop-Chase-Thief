# Security & Threat Model

Adversary: an untrusted opponent peer (and a hostile network) that may send malformed,
duplicated, reordered, stale, or forged messages, lie in hints, attempt to read hidden
state, forge audit/agreement evidence, or exhaust our resources. Trust boundary: our
own process. Everything crossing it is validated; all defined failures fail closed to a
deterministic technical loss (0/0), never an illegal move or a false-successful audit.

| Threat | Control | Where |
|---|---|---|
| Forged/replayed moves | commit-reveal (SHA-256 commit, nonce revealed at audit) | `domain/crypto`, `peer/audit` |
| Hidden-position leak (live) | Observation carries only legal fields; GUI draws one marker | `strategy/base`, `gui/window` |
| Malformed protocol messages | strict field checks -> ValueError | `infra/mcp_server` tools |
| Duplicate / retried requests | server-side idempotency keyed (token, request_id) | `infra/idempotency` |
| Lost responses / transient drops | timeout + bounded retry + backoff + correlation | `infra/reliability` |
| Stalled/slow opponent | per-sub-game watchdog -> technical | `peer/watchdog` |
| DoS (flooding) | concurrency + queue gatekeeper (token bucket) | `shared/gatekeeper` |
| Unauthorized / revoked peer | bearer allow-list + revocation set | `security/auth` |
| Inconsistent / illegal barriers | peer validates declared barrier (bounds/dup/shape) | `peer/net_engine` |
| Malicious hint text | word cap + coordinate/secret filter; fail-closed sanitize | `strategy/hint_filter` |
| Unverified hint influence | hint biases pursuit only above audited credibility 0.5 | `strategy/hints`, `strategy/meta` |
| Profiling from hidden/unaudited data | profile ingests only audit-verified records | `strategy/profiling` |
| Forged final agreement | per-peer keys; each signs own hash; forgery fails under peer key | `report/confirm` |
| Oversized/empty report attachment | size/empty guard before send | `infra/gmail_report` |
| Duplicate Gmail send after restart | idempotency marker with message id | `infra/gmail_report` |
| Secret exposure | keys/tokens only from ignored env/paths; secret-scan; never logged | `.gitignore`, `scripts/secret_scan.py` |
| Deadline exhaustion | anytime search returns best legal move; guaranteed fallback | `strategy/search`, `strategy/fallback` |

## Cryptographic notes and the external boundary
The DEV path uses keyed HMAC-SHA256 signers, one distinct secret key per peer
(`PT_SIGNER_KEY`, ignored env). This proves the core property in tests and the local
rehearsal: **a process holding only its own key cannot fabricate the other peer's
confirmation** (a signature made with the wrong key fails verification under the peer's
key). Because HMAC is symmetric, a single peer cannot verify the *other* peer's
signature without that peer's key; full cross-peer verification therefore uses either
both keys (the local rehearsal / lecturer's audit) or the official asymmetric Step-0
key. The official signer integration is **BLOCKED-EXTERNAL**.

## Secrets policy
Never committed: `.env`, `credentials.json`, `token.json`, `*.key`, `*.pem`, signer
keys, tunnel tokens, OAuth tokens. Loaded only from ignored local paths or environment.
No secret is written to logs or artifacts (`no_key_leak` is checked by the rehearsal).
