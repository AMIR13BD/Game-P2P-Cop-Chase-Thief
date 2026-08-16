# Official match G020 — replay evidence

The six per-sub-game logs of the **counted league match G020, `amireman` vs `Orcai-MJ`**
(final score 90 : 30, 6–0). They are committed so that the mandatory `VERIFIED OK` replay
screenshot can be reproduced by anyone, from real league data rather than a fixture.

## Provenance

These logs were written by **this repository's own runtime**, at commit
`71ce1d4442dcb7303d1a0f19f0af00e93b453c91`, which is the peer that played G020 for group
`amireman`. Our peer alternates roles across the six sub-games, so the set covers both
sides of the contract:

| sub-game | our role | recorded steps |
|---|---|---|
| `g01`, `g03`, `g05` | thief | 35 each |
| `g02`, `g04`, `g06` | police | 9 each |

The same six files are published in the companion Police repository as our group's shared
series evidence; that repository's runtime did not itself record them.

## What is and is not here

Only the `log_*.json` records are committed. `declaration_G020.json` and
`result_G020.json` are deliberately **excluded**: they embed the ephemeral Cloudflare
tunnel endpoints used on match day, which have no business in a published repository.
Nothing here contains credentials, tokens, absolute paths or e-mail addresses.

A log holds, per turn, the revealed `(nonce, payload)` pair and its SHA-256 `commit`. That
is exactly what the replay viewer needs in order to recompute each commitment
independently — which is why the green badge in the screenshot means something.

## Reproducing the verdict

```bash
uv run python -m thief_agent replay --dir docs/evidence/G020 --game-id G020        # text
uv run python -m thief_agent replay --dir docs/evidence/G020 --game-id G020 --gui  # window
```
