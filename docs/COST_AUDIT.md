# Cost audit — total AI / API cost of this project

A forensic accounting of every LLM and paid-service cost this project incurred, from the first
commit to submission. Nothing here is estimated from conversation length or invented: every token
figure is read out of a machine-written usage record, and every `$0` is justified rather than
assumed.

Snapshot: **2026-08-16**. Figures were produced by aggregating provider-written usage records; the
method is reproducible from the description in each section.

---

## 1. Summary

| Category | Usage | Cost basis | Actual cost | API-equivalent |
|---|---:|---|---:|---:|
| Claude Code (development) | 1,621,114,159 tokens | Subscription — no per-project charge | **$0.00** | **$1,308.57** |
| OpenAI advisor (gameplay) | 0 tokens | Never invoked; no key configured | **$0.00** | $0.00 |
| Gameplay LLM (all 27 games) | 0 tokens | Offline hint templates only | **$0.00** | $0.00 |
| Cloudflare Quick Tunnels | ~30 ephemeral tunnels | Free tier, no account required | **$0.00** | — |
| Gmail API | 12 sends | Free; no per-message charge | **$0.00** | — |
| GitHub (repos + Actions) | 71 CI runs, ~107 min | Within included Actions allowance | **$0.00** | — |
| **Total known actual cost** | | | **$0.00** | |
| **Total API-equivalent estimate** | | | | **$1,308.57** |

**Read the two right-hand columns as different things.** *Actual cost* is money that changed hands
because of this project. *API-equivalent* is what the same work would have cost billed at public
per-token list prices. They are reported separately and never added together.

**Unknown is not zero.** Section 7 lists what this audit could not measure. Those costs are real;
they are simply not attributable to this project from the evidence available.

---

## 2. Claude Code — development usage

Claude Code was the primary development tool. Its session transcripts record a per-request `usage`
object (input, output, cache-write, cache-read tokens, and the model that served the request), which
makes this the one development cost that is precisely measurable.

**Source.** 19 JSONL session transcripts under two local project directories, both belonging to this
workspace (14 top-level sessions plus 5 sub-agent transcripts). Attribution is by working directory:
every record's `cwd` resolves under `…/Desktop/finalproject`, so no unrelated project's usage is
included. Session files themselves are **not** committed — only these aggregates.

| Model | API calls | Input | Output | Cache write (1h) | Cache write (5m) | Cache read | Total tokens | API-equivalent |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `claude-opus-4-8` | 3,318 | 380,162 | 5,647,737 | 33,159,390 | 321,717 | 1,338,772,720 | 1,378,281,726 | $1,146.09 |
| `claude-opus-5` | 812 | 1,624 | 709,859 | 2,491,605 | 0 | 239,629,345 | 242,832,433 | $162.49 |
| **Total** | **4,155** | **381,786** | **6,357,596** | **35,650,995** | **321,717** | **1,578,402,065** | **1,621,114,159** | **$1,308.57** |

A further 25 assistant records carry a `<synthetic>` model and zero tokens — locally generated
messages that never reached the API. They are counted as calls nowhere in the table above.

**Pricing basis (API-EQUIVALENT ESTIMATE).** Both models are Opus-tier at **$5.00 / 1M input** and
**$25.00 / 1M output**. Cache writes bill at 1.25× base input for the 5-minute TTL and 2× for the
1-hour TTL; cache reads bill at 0.1× base input. Applied per model:

```
cost = (input × $5 + output × $25 + cache_write_1h × $10 + cache_write_5m × $6.25
        + cache_read × $0.50) / 1e6
```

**Actual billed cost: $0.00 attributable.** Claude Code was used through a subscription. No cost
field is recorded anywhere in the local session data, and a monthly subscription price is *not* this
project's cost — the seat is shared across everything the account did that month, and dividing it
would be an invention. The subscription fee is listed as unmeasured in §7 rather than silently
counted as zero.

**Why cache-read dominates.** 97.4% of all tokens are cache reads, billed at one-tenth of input
rate. At full input price the same volume would have been roughly $7,900 — prompt caching is the
single largest cost factor in this figure, not model choice.

---

## 3. OpenAI advisor — never used

The agent ships an optional LLM tactical advisor
([`advisor/client.py`](../src/thief_agent/advisor/client.py), default model `gpt-5.4-mini`). It
activates only when `OPENAI_API_KEY` is present and otherwise falls back to the deterministic
strategy layer.

**Evidence that it never ran:** `OPENAI_API_KEY` is unset in the development environment, no `.env`
file exists in either repository, and — decisively — every game's recorded `tokens_total` is `0`
(§4). Had the advisor ever been consulted, that counter would be non-zero.

`OPENAI_TOTAL_TOKENS = 0`, `OPENAI_ACTUAL_COST = $0.00`.

---

## 4. Gameplay runtime LLM usage — zero, across every game

Every sub-game writes a `tokens_total` into its summary, and every series result writes a per-group
`tokens` object. Both were aggregated across the whole workspace.

| Measure | Value |
|---|---:|
| JSON artifacts scanned | 965 |
| Unique usage records after deduplication | 162 |
| Duplicate records skipped | 240 |
| Distinct games covered | 27 |
| Records with non-zero gameplay tokens | **0** |
| **Total recorded gameplay LLM tokens** | **0** |

The 27 games include every counted league match — `G002`, `G005`, `G008`, `G012`, and the final
`G020` — plus friendlies, benchmarks, and local runs.

This is a design outcome, not an accident: verbal hints come from offline templates
(`BrainBase.hint`) and all move selection is deterministic, so a full six-sub-game series costs
nothing in inference. G020 is one instance of that property, not the whole story.

---

## 5. Deduplication method

The same run appears in several places, so raw sums would over-count badly. Two independent
deduplication passes were applied, and both changed the answer materially.

| Surface | Duplicate source | Key used | Duplicates removed |
|---|---|---|---:|
| Claude Code sessions | Resumed / forked sessions replay earlier assistant messages into new transcripts | `message.id` (one API response) | 5,527 records |
| Gameplay artifacts | Logs, summaries, result rows and archived copies restate the same sub-game | `(game_id, sub_game_number, role)` | 240 records |
| Gmail markers | Markers copied across run directories | `game_id` | 24 files → 12 sends |

Without the first pass the Claude Code figure would have been inflated by roughly 57% in record
count. Deduplication is the difference between an audit and a guess.

---

## 6. External services

| Service | How we used it | Why the cost is what it is |
|---|---|---|
| **Cloudflare Quick Tunnels** | ~30 ephemeral `trycloudflare.com` endpoints for peer-to-peer matches | Quick tunnels are anonymous and free — no account, no subscription, no metered egress. $0 is supported by the product's terms, not assumed. |
| **Gmail API** | 12 end-of-game report sends (24 markers → 12 after dedup) | The Gmail API is not metered in money; it is rate-limited in quota units. A send costs 100 units against a 1,000,000,000-unit daily quota — about 0.0001% of one day's allowance. |
| **GitHub — repositories** | 2 private repositories | Private repositories are included at no charge on current GitHub plans. |
| **GitHub — Actions** | 71 CI runs, ≈107 minutes of wall-clock across both repos | Private-repository Actions consume included minutes (2,000/month on the Free plan). 107 minutes is ~5% of that. **Caveat:** the API token available to this audit cannot read account billing, so this is measured usage against a published allowance, not a confirmed invoice. |

---

## 7. What this audit could NOT measure

Listed rather than folded into `$0`, because unknown and zero are different claims.

- **Claude subscription fee.** A real recurring cost, but not divisible into a defensible
  per-project figure. The API-equivalent estimate in §2 is the honest substitute.
- **Development work predating local session logging.** Only sessions still present on disk are
  counted. Any earlier work — or sessions since deleted — is invisible here, so the §2 figure is a
  **lower bound**.
- **Live-session growth.** The audit is a snapshot; the session that produced this document
  continues to accrue tokens after the numbers were read.
- **Electricity and local compute.** Never metered, so no figure is offered. Assigning one would be
  fabrication.
- **Human time.** Out of scope for an API-cost audit.
- **GitHub account plan.** Not readable with the available token scopes (see §6).

---

## 8. Reproducing these numbers

Claude Code totals: iterate `~/.claude/projects/<workspace-dir>/**/*.jsonl`, keep records with
`type == "assistant"` that carry `message.usage`, deduplicate on `message.id`, and sum
`input_tokens`, `output_tokens`, `cache_read_input_tokens`, and the
`cache_creation.ephemeral_{5m,1h}_input_tokens` split, grouped by `message.model`.

Gameplay totals: walk every `*.json` under the repositories and the match archive, collect
`summary.tokens_total` and `games[].tokens`, deduplicate on `(game_id, sub_game_number, role)`, and
sum.

No credentials, prompt text, conversation content, or personal billing information is reproduced in
this ledger — only aggregate counters and their provenance.
