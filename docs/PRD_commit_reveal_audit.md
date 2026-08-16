# PRD — Commit-reveal integrity and mutual audit

*Per-mechanism PRD required by the software guidelines §2.3. Documents
[`domain/crypto.py`](../src/thief_agent/domain/crypto.py),
[`peer/sealing.py`](../src/thief_agent/peer/sealing.py),
[`peer/audit.py`](../src/thief_agent/peer/audit.py) and
[`gui/replay_verify.py`](../src/thief_agent/gui/replay_verify.py).*

---

## 1. Description and theoretical background

The match is played peer-to-peer with **no referee**. Each side could, in principle, choose
its move after seeing the opponent's, or rewrite its log afterwards to claim a better
result. Both attacks are prevented by a **commit-reveal** protocol backed by SHA-256.

A commitment scheme provides two properties:

* **Hiding** — the commitment reveals nothing about the value. Here a fresh 16-byte nonce
  is concatenated with the payload before hashing, so an opponent cannot brute-force the
  small move space (there are only five legal moves; without a nonce the hash *would* be
  trivially invertible by enumeration — the nonce is what makes hiding real).
* **Binding** — the committer cannot later open the commitment to a different value. This
  rests on the collision resistance of SHA-256: finding a second `(payload, nonce)` pair
  hashing to the same digest is computationally infeasible.

The construction is:

```
canonical_json(payload) = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"))
commit = SHA256( canonical_json(payload) + "|" + nonce )
```

Canonicalisation is essential: both peers must hash **identical bytes**, so key order,
whitespace and escaping are all pinned. Verification uses `secrets.compare_digest`, a
constant-time comparison, to avoid leaking information through timing.

Each turn therefore proceeds: commit → exchange → reveal → verify. Post-match, both peers
run a **mutual audit** over the whole log, recompute every commitment, and exchange a
digest of their result; the match is only agreed when both digests match.

## 2. Requirements, expected input/output, performance metrics

| # | Requirement |
|---|---|
| R1 | Commit before the opponent's move is known |
| R2 | Use a fresh cryptographically-random nonce per commitment (never reuse) |
| R3 | Serialize canonically so both peers hash identical bytes |
| R4 | Verify every revealed record; a single mismatch fails the sub-game |
| R5 | Compare digests in constant time |
| R6 | Seal a Step-0 declaration binding group name, sub-game number, code version and the exact played commit SHA |
| R7 | Reach mutual result consensus before a result is reported |
| R8 | Allow independent post-hoc verification by a third party from the log alone |

**Input** — a move payload dict.
**Output** — `{"nonce": …, "commit": …}` at seal time; a boolean/raise at verify time;
`{"verified": bool, "failed_steps": [...], "total": n}` at replay time.

**Constants** — `NONCE_BYTES = 16` (128 bits of entropy).

**Performance metrics** — verification time per record; whole-series audit time;
false-positive rate (must be exactly zero on untampered logs).

## 3. Constraints, limitations, alternatives considered

**Constraints.** The wire format must be byte-compatible with the official reference
implementation, so the canonical-JSON shape and the `payload|nonce` concatenation order are
fixed and not ours to optimise. Provenance for this format is recorded in
[`REUSE-REGISTER.md`](REUSE-REGISTER.md) — this is an independent re-implementation, not a
copy.

**Limitations — stated honestly.**
- Commit-reveal proves a move was *fixed in advance*; it does **not** prove the move was
  *good*, nor that the agent ran any particular strategy.
- The Step-0 declaration binds a claimed Git commit SHA; it does not by itself prove the
  binary that ran matches that SHA. Verification is social (the grader can read the repo at
  that SHA), not cryptographic.
- A peer that simply disconnects cannot be forced to reveal; that case is handled as a
  technical result by the watchdog, not by cryptography.

**Alternatives considered**

| Alternative | Why rejected |
|---|---|
| Hash the move with no nonce | Broken — only five legal moves, so the digest is invertible by enumeration. The nonce is what supplies hiding |
| Digital signatures per move instead of commitments | Signatures prove authorship, not *temporal ordering*; they do not stop choosing a move after seeing the opponent's |
| Trusted third-party referee | Contradicts the peer-to-peer requirement of the assignment |
| Non-canonical `json.dumps` | Key-order differences silently break cross-peer hashing — the exact class of bug canonicalisation exists to prevent |
| `==` for digest comparison | Leaks information through timing; `compare_digest` is constant-time |

## 4. Success criteria and test scenarios

**Success criteria**
- S1 An untampered series verifies 6/6 with zero failed steps.
- S2 Any single-byte modification of a payload, nonce or commitment is detected.
- S3 Both peers independently reach the same result digest.
- S4 A third party can verify from the committed logs alone, with no network access.

**Test scenarios**

| Scenario | Test |
|---|---|
| Commit/verify round trip, canonical JSON stability | `tests/unit/test_crypto.py` (domain suite) |
| Deliberate tamper is detected at the right step | `tests/unit/test_replay.py`, `sim/tamper_gen.py` |
| Tampered commitment vs tampered payload | `tests/unit/test_gui_replay_panel.py` |
| Mutual confirmation / consensus digest | `tests/unit/test_interop_mutual_confirmation.py`, `test_interop_consensus_schema.py` |
| Step-0 declaration sealing | `tests/unit/test_interop_peer_commit_sources.py` |
| Config-hash agreement and refusal on mismatch | `tests/unit/test_interop_official_result_compliance.py` |

**Empirical result.** The counted match **G020** verifies 6/6 with zero failed steps, and
mutual consensus is recorded as confirmed with matching peer digests. The committed logs
under [`evidence/G020/`](evidence/G020/) let anyone reproduce that verdict:

```bash
uv run python -m thief_agent replay --dir docs/evidence/G020 --game-id G020
```

The same verifier drives the green badge in the Replay Viewer screenshot, and the
[`thief-replay-tampered.png`](images/thief-replay-tampered.png) capture shows it
correctly rejecting a deliberately corrupted record — evidence that the green result is
earned rather than displayed unconditionally.
