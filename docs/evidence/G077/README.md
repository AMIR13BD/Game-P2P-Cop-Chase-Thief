# Official match G077 — replay evidence

The six per-sub-game logs of the **counted league match G077, `amireman` vs `ali-ahm1`**
(final score 90 : 30, 6–0). They are committed so the commit-reveal verdict can be
reproduced by anyone, from real league data rather than a fixture.

## Provenance

The series was played by our peer runtime with **role-specific commits declared per
sub-game**: the Thief repository at `17b83bf1d0f4c9ce338fa04f6252b6a105c76da1`
defended sub-games `g01`/`g03`/`g05`, and the Police repository at
`6e8bc146b5e667286e6ceb80fc61edaeb9109dec` pursued `g02`/`g04`/`g06`. The
opponent declared `a885ccc2229ffa677688d24af61bdad2e4c0da64` (cop).

| sub-game | our role | outcome | recorded steps |
|---|---|---|---|
| `g01`, `g03`, `g05` | thief | survival | 35 each |
| `g02`, `g04` | police | capture | 12 each |
| `g06` | police | capture | 19 |

## Settlement

| | |
|---|---|
| Sub-games | 6 : 0 to `amireman` |
| Final score | `amireman` 90 : 30 `ali-ahm1` |
| `results_agreed` | `true` — every sub-game's result claim matched on both sides |
| `sha_match` | `true` |
| `mutual_agreement.confirmed` | `true` |
| Consensus digest | `d93188454b5b24c01d4c3390904446626c4b6439d22887a9ef543dbf1f6f4b32` |
| Consensus profile | `official_reference_v1` |

## What is and is not here

Only the `log_*.json` records are committed. `declaration_G077.json` and `result_G077.json`
are deliberately **excluded**: they embed the ephemeral tunnel endpoints used on match day,
which have no business in a published repository. The settlement facts those files carry are
transcribed into the table above instead. Nothing here contains credentials, tokens,
absolute paths or e-mail addresses.

A log holds, per turn, the revealed `(nonce, payload)` pair and its SHA-256 `commit` — which
is exactly what the replay viewer needs to recompute each commitment independently.

## Reproducing the verdict

```bash
uv run python -m thief_agent replay --dir docs/evidence/G077 --game-id G077        # text
uv run python -m thief_agent replay --dir docs/evidence/G077 --game-id G077 --gui  # window
```
