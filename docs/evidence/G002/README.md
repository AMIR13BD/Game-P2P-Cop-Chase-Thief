# Official match G002 — replay evidence

The committed artifact set of the **counted league match G002, `amireman` vs `uoh-ay26`**
(final score 40 : 60, sub-games 2 : 4 — loss).

## What is committed

| File | Role |
|---|---|
| `config_G002_g01.json` ... `g06.json` | the cryptographically locked agreed configuration of each sub-game -- the mandatory per-game config attachment (Appendix F, *Mandatory Rules* rules 3-4) |
| `log_G002_g01.json` ... `g06.json` | the per-sub-game commit-reveal log that the replay viewer verifies |
| `result_G002.json` | the final result report -- the same JSON structure that was mailed to the lecturer |

`declaration_G002.json` is deliberately **excluded**: it embeds the ephemeral tunnel
endpoints used on match day, which have no business in a published repository. Nothing
committed here contains credentials, tokens, absolute paths or e-mail addresses.

## Provenance

Every committed file carries `game_uid` `605f754b-7c28-3691-a5cf-f655e485e8ca` -- including all six logs -- so the
configuration published here is provably the one those logs were played under, not a
reconstruction after the fact. The agreed 14 terms hash to `config_sha256`
`ad9e1bfd724e9debcde523833381cb7982a5d619d693d3738b59e0da61f4d81a`, identical across all six sub-games.

## Per sub-game

`Outcome` is the sub-game's own verdict (capture or survival); `Ours` translates it through
our role in that sub-game, since a survival is a win for the Thief and a loss for the Cop.

| Sub-game | Our role | Outcome | Steps | Ours | Log verified | Gameplay tokens |
|---|---|---|---|---|---|---|
| `g01` | thief | survival | 35 | **win** | OK | 0 |
| `g02` | police | survival | 35 | **loss** | OK | 0 |
| `g03` | thief | capture | 15 | **loss** | OK | 0 |
| `g04` | police | survival | 35 | **loss** | OK | 0 |
| `g05` | thief | survival | 35 | **win** | OK | 0 |
| `g06` | police | survival | 35 | **loss** | OK | 0 |

The six `Ours` cells sum to 2 -- exactly the `sub_games_won` figure that the mutually
agreed `result_G002.json` records for `amireman`.

## Settlement

| | |
|---|---|
| Sub-games won | `amireman` 2 · `uoh-ay26` 4 |
| Final score | `amireman` 40 : 60 `uoh-ay26` |
| `results_agreed` | `true` |
| `sha_match` | `true` |
| `mutual_agreement.confirmed` | `true` |
| Series LLM tokens | 0 for both groups |

## Reproducing the verdict

```bash
uv run python -m thief_agent replay --dir docs/evidence/G002 --game-id G002        # text
uv run python -m thief_agent replay --dir docs/evidence/G002 --game-id G002 --gui  # window
```
