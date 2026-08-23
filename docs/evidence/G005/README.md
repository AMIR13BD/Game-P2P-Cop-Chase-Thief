# Official match G005 — replay evidence

The committed artifact set of the **counted league match G005, `amireman` vs `saedshki`**
(final score 47 : 47, sub-games 3 : 3 — series tie).

## What is committed

| File | Role |
|---|---|
| `config_G005_g01.json` ... `g06.json` | the cryptographically locked agreed configuration of each sub-game -- the mandatory per-game config attachment (Appendix F, *Mandatory Rules* rules 3-4) |
| `log_G005_g01.json` ... `g06.json` | the per-sub-game commit-reveal log that the replay viewer verifies |
| `result_G005.json` | the final result report -- the same JSON structure that was mailed to the lecturer |

`declaration_G005.json` is deliberately **excluded**: it embeds the ephemeral tunnel
endpoints used on match day, which have no business in a published repository. Nothing
committed here contains credentials, tokens, absolute paths or e-mail addresses.

## Provenance

Every committed file carries `game_uid` `6edafd13-6aa1-1fc7-3ad0-6317aea6bcd1` -- including all six logs -- so the
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
| `g03` | thief | survival | 35 | **win** | OK | 0 |
| `g04` | police | survival | 35 | **loss** | OK | 0 |
| `g05` | thief | survival | 35 | **win** | OK | 0 |
| `g06` | police | survival | 35 | **loss** | OK | 0 |

The six `Ours` cells sum to 3 -- exactly the `sub_games_won` figure that the mutually
agreed `result_G005.json` records for `amireman`.

## Settlement

| | |
|---|---|
| Sub-games won | `amireman` 3 · `saedshki` 3 |
| Final score | `amireman` 47 : 47 `saedshki` |
| `results_agreed` | `true` |
| `sha_match` | `false` |
| `mutual_agreement.confirmed` | `false` |
| Series LLM tokens | 0 for both groups |

> **Settlement note — read this.** `results_agreed` is `true`: both sides claimed the same
> outcome for every sub-game, so the score above is the mutually agreed one. `sha_match` is
> `false`, and `confirmed` therefore `false`, because the two peers' *settlement digests* differ —
> the opponent serialised the result envelope to a different field shape than we did. That is a
> wire-schema divergence in the report record, not a disagreement about the result. It is
> recorded here rather than smoothed over.

## Reproducing the verdict

```bash
uv run python -m thief_agent replay --dir docs/evidence/G005 --game-id G005        # text
uv run python -m thief_agent replay --dir docs/evidence/G005 --game-id G005 --gui  # window
```
