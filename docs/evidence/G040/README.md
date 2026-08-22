# Official match G040 — replay evidence

The six per-sub-game logs of the **counted league match G040, `amireman` vs `salareen`**
(final score 90 : 30, 6–0). They are committed so the commit-reveal verdict can be
reproduced by anyone, from real league data rather than a fixture.

## Provenance

The series was played by our peer runtime with **role-specific commits declared per
sub-game**: the Thief repository at `17b83bf1d0f4c9ce338fa04f6252b6a105c76da1`
defended sub-games `g01`/`g03`/`g05`, and the Police repository at
`6e8bc146b5e667286e6ceb80fc61edaeb9109dec` pursued `g02`/`g04`/`g06`. The
opponent declared `c0f4f23e73dcd67f456401b2e57fc5be764a7f55` (cop) and `6980a2243b2658cc83429b0f788203e10d2331b0` (thief).

| sub-game | our role | outcome | recorded steps |
|---|---|---|---|
| `g01`, `g03`, `g05` | thief | survival | 35 each |
| `g02`, `g04` | police | capture | 12 each |
| `g06` | police | capture | 12 |

## Settlement

| | |
|---|---|
| Sub-games | 6 : 0 to `amireman` |
| Final score | `amireman` 90 : 30 `salareen` |
| `results_agreed` | `true` — every sub-game's result claim matched on both sides |
| `sha_match` | `true` |
| `mutual_agreement.confirmed` | `true` |
| Consensus digest | `052219681e9eb0f7d079993428de7d25f909889b95c45c9b5e5a7563663f3e5d` |
| Consensus profile | `official_reference_v1` |

## What is and is not here

Only the `log_*.json` records are committed. `declaration_G040.json` and `result_G040.json`
are deliberately **excluded**: they embed the ephemeral tunnel endpoints used on match day,
which have no business in a published repository. The settlement facts those files carry are
transcribed into the table above instead. Nothing here contains credentials, tokens,
absolute paths or e-mail addresses.

A log holds, per turn, the revealed `(nonce, payload)` pair and its SHA-256 `commit` — which
is exactly what the replay viewer needs to recompute each commitment independently.

## Reproducing the verdict

```bash
uv run python -m thief_agent replay --dir docs/evidence/G040 --game-id G040        # text
uv run python -m thief_agent replay --dir docs/evidence/G040 --game-id G040 --gui  # window
```
