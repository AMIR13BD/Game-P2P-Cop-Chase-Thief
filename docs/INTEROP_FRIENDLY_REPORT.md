# Cross-team FRIENDLY interoperability — implementation & proof

**Scope:** protocol/interoperability only. No strategy, benchmark, or security change.
**Authority:** official reference `rmisegal/Game-P2P-Cop-Chase @ 960499f` (book v3.0.0).
**Independent peer:** community kit `Imreec/copthief-league-protocol @ 596aaf4` (`sparring` peer,
`wire_shape: reference-v3`).
**Branches:** Thief `interop/official-protocol` (base `4406c85`), Thief `interop/official-protocol`
(base `3783bc3`). Master untouched. Nothing merged or pushed.

This supersedes the *NOT PROVEN* verdict in [`INTEROP_GAP_REPORT.md`](INTEROP_GAP_REPORT.md): the
four mandatory blockers are closed and a full six-sub-game FRIENDLY series has been played, live,
against an independently-implemented compliant peer with clean mutual audits — **no email**.

---

## 1. Mandatory incompatibilities fixed
| # | Blocker (was) | Now |
|---|---|---|
| 1 | `game_id` = manual CLI value | `"-vs-".join(sorted([a,b]))` — `interop/ids.derive_game_ids` |
| 2 | `game_uid` = `SHA256(game_id)[:32]` | `UUID(SHA256(canonical(terms)\|"\|".join(sorted(pair)))[:16])` |
| 3 | agreement = `config_sha256` equality | signed terms: `SHA256(canonical(terms)\|nonce)` mutually verified |
| 4 | MCP tools `hello/start_subgame/exchange/finalize/confirm`, single dialer | official `negotiate/receive_turn/submit_audit/receive_control`, **dual-server + dual-dial, pushed turns** |
| 5 | cannot play an unknown compliant student | **plays the kit's independent peer, live, cleanly** (§12) |

## 2. Official-reference behaviour implemented
A neutral adapter package `src/<pkg>/interop/` wraps the existing engine and speaks reference-v3:
`ids`, `terms`, `wire`, `delivery`, `negotiate`, `server`, `client`, `engine`, `runtime`, `series`,
`scoring`, `artifacts`, `friendly`, `cli`. It re-uses our **already-conformant** `domain/crypto`
(canonical JSON + commit-reveal) and calls the **unchanged** strategy brain through the same seam
`peer.net_engine.PeerHalf` already uses (`make_gameplay_brain` → `Observation` → `firewall.enforce`
→ `hint_filter.sanitize`). No file under `strategy/` was touched.

## 3. `game_id` proof
`derive_game_ids(terms,"amireman","sparring-local")[0] == "amireman-vs-sparring-local"`, equal for
both group orders, and byte-equal to the kit's `ref_game_id`. Locked by
`test_interop_core.test_game_id_is_sorted_pair_order_independent`.

## 4. `game_uid` proof
`= 724547d5-edfd-769d-31e9-8aed44e4354f`, reproduced independently by (a) our adapter, (b) the kit's
`ref_game_uid`, (c) the black-box peer, and (d) the kit's `check_artifacts.py --terms` derivation.
All four agree. Locked by `test_game_uid_matches_independent_reference_and_is_uuid`.

## 5. Signed-terms proof
`interop/negotiate.Negotiator` signs `commit_of(terms,nonce)` (= reference `terms_signature`
byte-for-byte) and refuses on terms mismatch, bad signature, missing group, or a wrong-input
`game_uid` declaration. The kit verified our greeting and we verified the kit's, live. Tests:
`test_interop_negotiate.py` (happy path + 5 refusals).

## 6. Official MCP tools implemented
`interop/server.build_peer_server` exposes exactly `negotiate(message)`, `receive_turn(message)`,
`submit_audit(payload)`, `receive_control(message)` — official names, official argument-name
asymmetry (`submit_audit` takes `payload`; the rest take `message`). Each validates, enqueues to a
thread-safe inbox, and returns `{"ok": true}` without blocking.

## 7. Dual-server / dial model
Each peer hosts its **own** FastMCP server (`start_peer_server`, background daemon thread) and dials
the opponent's URL (`interop/client.McpTransport`). Turns are **pushed** fire-and-forget; the turn
token travels with the message. Symmetric: both peers serve and both dial. Proven live over
localhost sockets in §12 and by `test_interop_network.py`.

## 8. Reconnect / idempotency behaviour
`interop/delivery` re-implements the reference at-least-once truth table (locked against the kit's
`vectors/delivery_contract.json`): `absorb` a duplicate (keyed on the **commit**), `equivocation`
on a second *different* commit for a played step, `buffer` inside the reorder window, `apply`+drain,
`discard` a stale sub-`next` index, `violation` past the window. A violation/equivocation is
**classified** as a technical loss, never a crash. Tests: `test_delivery_decision_truth_table`,
`test_inbox_dedup_reorder_and_equivocation`, `test_series_survives_duplicate_turn_delivery`,
and a per-sub-game turn-drain so a straggler never leaks into the next sub-game's fresh inbox.

## 9. Six-game behaviour
`interop/series.run_series` plays exactly 6 sub-games, re-handshaking per sub-game (as the
reference/kit do), alternating roles (`scoring.role_for`: natural on odd, opposite on even), with
one shared match identity and a fresh runtime/brain/commit-chain each sub-game. Live result:
6/6 complete, roles `police,thief,police,thief,police,thief`.

## 10. Audit behaviour
`interop/runtime` reveals `AuditPayload{sender,records,result_claim}` and verifies the opponent's
records with **integrity** (re-hash via our serializer) **and binding** (each revealed commit ==
the commit received on the wire). Both peers commit canonical payloads; nonces stay secret until
reveal; a mismatch → `tamper_forfeit` (0-0). Live: all 6 sub-games audited clean, both directions
(e.g. g01 log: 14 verified steps, `tampered:false`). Our records also pass the kit's **armed** audit
(integrity + binding + physics).

## 11. Artifact comparison
`interop/artifacts` emits the four official artifacts (`declaration`/`config`×6/`log`×6/`result`)
as canonical bytes, named from `game_id`, joined by `game_uid`. Our result and the kit's result
agree field-for-field:

```
game_uid   724547d5-edfd-769d-31e9-8aed44e4354f  (both)
total_score {amireman:90, sparring-local:30}     (both)
sub_games_won {amireman:6, sparring-local:0}      (both)
winner_group amireman                             (both)
per-row scores  g1/3/5 capture 20-5, g2/4/6 survival 10-5  (both)
```

## 12. Independent sparring result (LIVE, two real servers)
Our production adapter (`uv run python -m <pkg>.interop friendly`) vs the kit's `uv run python -m sparring.cli
serve` over **real localhost FastMCP** (ours :8904 ↔ kit :8934):

```
game_id  amireman-vs-sparring-local
game_uid 724547d5-edfd-769d-31e9-8aed44e4354f
 sub  role     outcome   steps  audit
  1  police   capture     12    OK
  2  thief    survival    35    OK
  3  police   capture     12    OK
  4  thief    survival    35    OK
  5  police   capture     12    OK
  6  thief    survival    35    OK
 totals {amireman:90, sparring-local:30}  winner amireman
 lecturer_report_sent=False
```
Negotiation succeeded, ids matched, 6/6 completed, roles alternated, zero malformed MCP calls, zero
illegal actions, zero technical failures, every audit clean, no `tamper_forfeit`, artifacts
generated on both sides, result totals agree — **email NOT sent.**

Cross-artifact verification with the kit's own `tools/check_artifacts.py`:
- `check_artifacts.py /tmp/ours --terms terms.json` → **ALL ARTIFACT CHECKS PASS** (incl. uid DERIVES from flat terms).
- `check_artifacts.py <kitdir> --terms terms.json` → **ALL ARTIFACT CHECKS PASS**.
- `check_artifacts.py /tmp/ours <kitdir> --terms terms.json` → **ALL SETS AGREE** (uid, total_score, sub_games_won, winner_group, ties, series_tie, tokens, per-row scores, mutual_agreement).

## 13. Black-box peer result
`tests/integration/blackbox_peer.py` is a from-scratch reference-v3 peer using **stdlib only**
(hashlib/json/uuid/secrets) that imports **none** of our adapter. It negotiates, plays six
role-alternating sub-games, answers capture claims, claims survival, and audits our revealed records
with its own serializer. `test_our_runtime_plays_an_independent_blackbox_peer` proves: ids
recomputed identically, 6/6, complementary roles, both sides' audits clean. This is in addition to
the live kit run (a second, fully independent implementation).

## 14. Mixed-tunnel result
Transport is provider-neutral: an optional bearer token plus optional `PT_TUNNEL_HEADERS`, never a
hardcoded host/provider/opponent. `test_interop_transport.py` proves: no header by default; the
Localtonet bypass header applies only when configured; `Authorization` is preserved simultaneously;
a tunnel header can never override `Authorization`. So **Localtonet↔ngrok** and
**Localtonet↔Localtonet** use the identical protocol — only the dialing header differs (see §16
playbook). Not runnable end-to-end here (no external tunnels), but the header contract is enforced.

## 15. FRIENDLY email hard-block result
`interop/friendly` imports **nothing** from `infra.gmail_*`, `report.emit`, or `commands_report`:
there is no code path from a friendly run to a sender. It never marks a result
`counted-two-peer` — the only mode `gmail_report.should_send` would ever accept — so even a later
stage handed the result could not send it. Tests prove a **successful**, a **failed/timeout**, and
a **tamper-failed** friendly all leave the Gmail sender uninvoked (`test_friendly_never_calls_gmail_sender`
[clean & tampered], `test_friendly_module_imports_no_gmail`). The CLI prints
`match_mode=friendly` / `lecturer_report_sent=False`. Existing Gmail/reporting code is untouched and
remains available for a future explicit counted mode.

## 16–20. Gates (this repo)
- **Interop tests:** 42 passing (unit: ids/terms/wire/delivery/scoring/negotiate/transport/cli;
  integration: loopback six-game series, duplicate-delivery, artifact-join, black-box peer, real
  localhost two-server, friendly no-email).
- **Coverage (interop package):** **92%** (≥85). Full-suite coverage report below.
- **Ruff / format:** clean on all new files.
- **Line-count:** every source and test file ≤150 physical lines.
- **Secret scan:** no *tracked* secrets added; the working-tree scanner flags pre-existing,
  git-ignored local Gmail OAuth artifacts (`credentials.json`,`token.json`) unrelated to this work.
- **No strategy modification / no benchmark regression:** nothing under `strategy/`, `sim/`, or
  `evidence/` changed; the adapter only *calls* the existing brain seam.

## 21. Files changed
Added `src/<pkg>/interop/` (16 modules) + `tests/**/test_interop_*` and two integration helpers
(`interop_loopback.py`, `blackbox_peer.py`) + this report. No existing source file modified.

---

## FRIENDLY MATCH PLAYBOOK (two arbitrary students)

Us: `amireman`. Opponent: `THEIR_GROUP`. **Both sides need only these commands — no source edits.**
Exchange first: **group name, public MCP URL, bearer token (optional/shared), cop+thief repo URLs,
commit hash, and the hardware/model line** the declaration records. Agree the standard terms (Book
App. F defaults) so the signed `terms` are byte-identical.

### Our side
```
# TERMINAL 1 — our public server + driver (one process serves AND dials)
uv run python -m thief_agent.interop friendly \
    --peer <THEIR_PUBLIC_MCP_URL> \
    --group amireman --role police \
    --host 127.0.0.1 --port 8901 \
    --out runs/friendly --games 6
    # add --token <SHARED_TOKEN> ONLY if both sides agreed a bearer

# TERMINAL 2 — our tunnel (Localtonet example; any provider works)
localtonet http 8901          # publish http://127.0.0.1:8901/mcp -> https://<us>.localto.net/mcp
# If WE dial an opponent who is ALSO on Localtonet, set (Terminal 1 env):
export PT_TUNNEL_HEADERS='localtonet-skip-warning: true'
```

### Their side (any compliant/official peer — e.g. the reference or the kit)
```
# THEIR SERVER + DRIVER
uv run python -m THEIR_PACKAGE.interop friendly \
    --peer <OUR_PUBLIC_MCP_URL> --group THEIR_GROUP --role thief \
    --host 127.0.0.1 --port 8901 --out runs/friendly --games 6
#   (kit peer equivalent:  uv run python -m sparring.cli serve --peer <OUR_PUBLIC_MCP_URL> \
#                              --role thief --group-id sparring-THEIR --await-peer)

# THEIR TUNNEL
ngrok http --host-header=rewrite 8901      # ngrok: no special dial header needed
# or  localtonet http 8901                 # then WE dial with PT_TUNNEL_HEADERS set (above)
```

**Roles must be complementary in sub-game 1** (one `--role police`, the other `--role thief`); they
then alternate. **Tunnel matrix:**
- *Localtonet ↔ ngrok*: the ngrok side dials with no extra header; the side dialing the Localtonet
  URL sets `PT_TUNNEL_HEADERS='localtonet-skip-warning: true'`. ngrok server started with
  `--host-header=rewrite`.
- *Localtonet ↔ Localtonet*: **both** sides set `PT_TUNNEL_HEADERS='localtonet-skip-warning: true'`
  when dialing the other's `*.localto.net` URL.
The protocol bytes are identical regardless of provider.

**After the run** both sides hold `runs/friendly/{declaration,config×6,log×6,result}_amireman-vs-THEIR_GROUP.json`.
Cross-check before trusting anything:
```
python tools/check_artifacts.py runs/friendly --terms terms.json          # each side, alone
python tools/check_artifacts.py OUR_DIR THEIR_DIR --terms terms.json       # the join: ALL SETS AGREE
```
Friendly prints `lecturer_report_sent=False`. **No email is sent, ever, in friendly mode.**

## 26. Remaining incompatibilities
None for FRIENDLY cross-team play against a reference-v3 peer. Deliberately out of scope (not
required for friendly interop): the pheromone *kernel* differs from the reference (§F of the gap
report) — a strategy **input**, never audited, so it cannot void a match; and the counted/lecturer
reporting path is intentionally left disarmed.

---
**VERDICT: CROSS-TEAM FRIENDLY INTEROPERABILITY: PROVEN — SAFE TO TEST WITH A STUDENT, NO EMAIL**
