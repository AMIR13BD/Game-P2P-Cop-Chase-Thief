# Cross-team interoperability gap report

**Authoritative source:** official reference `rmisegal/Game-P2P-Cop-Chase` @ `960499f`
(2026-07-12), book v3.0.0. **Interop kit** (compatibility aid only): `Imreec/copthief-league-protocol`
@ `596aaf4` (2026-08-06). Our repos: Police `33d0b82`, Thief `0ae284f` (branch `interop/official-protocol`).

Tiers below: **OFFICIAL REQUIREMENT** (book, must match) · **KIT CORE** (kit pins bytes the book
leaves to agreement) · **OPTIONAL KIT** (Appendix-A opt-in) · **NON-BINDING** (recommendation).

## Summary
| Interop surface | Tier | Our status |
|---|---|---|
| Canonical JSON (§2) | KIT CORE / OFFICIAL | ✅ **byte-identical** (7/7 vectors) |
| Commit-reveal (§3) | KIT CORE / OFFICIAL | ✅ **byte-identical** (3/3 + reference form) |
| Terms/agreement signature (§4) | KIT CORE | ⚠️ primitive matches; not wired into negotiate |
| `game_id` derivation (§4) | OFFICIAL REQUIREMENT | ❌ manual CLI arg, not `-vs-`.join(sorted(pair)) |
| `game_uid` derivation (§4) | OFFICIAL REQUIREMENT | ❌ different construction |
| **MCP wire interface** | OFFICIAL REQUIREMENT | ❌ **incompatible tool set + connection model** |
| Pheromone model (§5) | KIT CORE | ⚠️ different kernel (own-emission only) |
| Report consensus (§6) | KIT CORE | not assessed (blocked by wire gap) |
| Live six-game sparring | proof gate | ❌ **not runnable in this sandbox** |

## A. Canonical JSON — ✅ MATCH (OFFICIAL/KIT CORE)
Our `domain/crypto.canonical_json` = `json.dumps(obj, sort_keys=True, ensure_ascii=False,
separators=(",",":"))`. Reproduces all 7 CORE vectors byte-for-byte incl. Hebrew, astral emoji,
shortest-float repr, Unicode **code-point** key sort, and the `1e-07`/`1e+16` exponent cliff
(Python-native). Booleans/null/nested/lists all match. Locked by `tests/unit/test_interop_vectors.py`.

## B. Commit-reveal — ✅ MATCH (OFFICIAL/KIT CORE)
Our `commit_of(payload,nonce)` = `SHA256(canonical(payload)+"|"+nonce)` = the kit's **reference
form** (3/3 vectors + `divergent_forms.reference_form`). The nonce is pipe-appended to the canonical
string (not inside the object). Consequence: **our revealed log passes an independent opponent's
cross-team audit** — the single most important interop fact, and we already satisfy it.

## C. Game identifiers — ❌ GAP (OFFICIAL REQUIREMENT)
- **game_id.** Official: `"-vs-".join(sorted([group_a, group_b]))`. Ours: a **manual `--game-id`
  CLI argument** (`report/ids.py` consumes, never derives). Two peers would produce non-matching
  artifact filenames that cannot be joined.
- **game_uid.** Official: `str(UUID(bytes=SHA256(canonical(terms)+"|"+"|".join(sorted(pair)))[:16]))`
  → `1e73c318-5b29-4a7b-1c60-ecb8286265f0`. Ours: `SHA256(game_id)[:32]` (32 hex, no dashes, from the
  game_id string only) → `29ca1883…`. Different input, length and format; peers would not share a uid.
- Bridgeable in a neutral adapter using our existing `canonical_json`/`commit_of` primitives (no
  strategy change), but currently non-conformant.

## D. Terms/agreement signature — ⚠️ PARTIAL (KIT CORE §4)
Official pre-game gate: `signature = SHA256(canonical(terms)+"|"+nonce)`. Our `commit_of(terms,nonce)`
**reproduces the official signature bytes exactly** (verified against the vector). But our `negotiate`
exchanges a nonce-less `config_sha256(cfg)=SHA256(canonical(cfg))` equality check instead of a
signed-terms gate. The primitive is compatible; the wire step is not yet.

## E. MCP wire interface — ❌ MAJOR GAP (OFFICIAL REQUIREMENT)
| | Official reference / kit | Ours |
|---|---|---|
| Tools | `negotiate(message)`, `receive_turn(message)`, `submit_audit(payload)`, `receive_control(message)` | `version`, `hello`, `negotiate(payload)`, `start_subgame`, `exchange`, `finalize`, `confirm` |
| Connection model | **symmetric**: BOTH peers host a FastMCP server AND both dial each other; turns are **pushed** fire-and-forget (`receive_turn` → `{"ok":true}`) | **asymmetric**: one peer serves, a single dialer drives via **request/response** (`exchange` returns the move) |
| Turn message | keys `[step, commit, hint, smell_grid, barrier_placed]` pushed to `receive_turn` | `exchange(payload)` args/returns move synchronously |
| Audit | `submit_audit(payload)` end-of-game reveal | `finalize`/`confirm` |

An independently-written official peer calling us hits **unknown tools** and never finds a
`receive_turn`/`submit_audit` to push to; our driver finds no `exchange` to pull from theirs. **A
compliant peer cannot play our production server as-is**, and vice-versa. Closing this needs a
**substantial neutral protocol adapter** (dual-server, the 4 receive-tools, an inbox + push turn
loop, `submit_audit`) wrapping our strategy engine — i.e. re-implementing the official peer runtime
around our brains. Preserves strategy, but it is large and unbuilt.

## F. Pheromone (§5) — ⚠️ DIFFERENT MODEL (KIT CORE, own-emission)
Official `subtractive_chebyshev_v1`: `value = round(max(0, intensity - (intensity/(half+1))·chebyshev),3)`.
Ours (`domain/smell.py`): a fixed radial kernel with `tau=min(0.9, max(0,(1-rho)·tau+delta))`. Scent
is each peer's **own** emission consumed by the opponent's belief map (not re-hashed at audit), so it
is a strategy-input difference, not an audit/settlement break — but the transmitted grid semantics
differ from the official model.

## G. Tunnel independence — ✅ (already neutral)
Transport is provider-agnostic: bearer auth + optional `PT_TUNNEL_HEADERS` (e.g. Localtonet
`localtonet-skip-warning: true`), no hardcoded host/provider. This layer is interop-ready; it is the
**application** wire (§E) that is not.

## H. Email/report safety — ✅
Reporting is gated on emitted+verified counted evidence; friendly/failed/audit-failed runs do not
email. No email is sent by tests or by this task.

## Verdict
Our **byte-level cryptographic core is already cross-team conformant** (canonical JSON + commit-reveal
— the parts that void a match on mismatch). However the **application-level MCP wire protocol and the
shared identifiers differ from the official reference**, and no live cross-implementation six-game
series has been (or can be, in this sandbox) demonstrated. We therefore **cannot** play an unknown
compliant group without source-code modifications (a neutral wire adapter + id/signature alignment).

**CROSS-TEAM INTEROPERABILITY: NOT PROVEN — DO NOT PLAY OFFICIAL MATCHES.**
