# Finalization checklist

*Last reconciled during the final pre-submission audit, against the actual repository state —
not against intent.*

The league programme is **finished**: seven counted series against seven different groups,
444 raw points, every one of the 42 sub-game logs verified untampered on both sides, and the
complete evidence committed under `docs/evidence/`. Nothing below is waiting on a match.

## Closed

| # | Item | Evidence |
|---|---|---|
| 1 | All counted league matches played | `G002` · `G005` · `G008` · `G012` · `G020` · `G040` · `G077` — README §7.1 |
| 2 | Match evidence committed and replayable | [`docs/evidence/`](docs/evidence/) — logs + per-game configs for all seven series |
| 3 | Per-game config files attached to the repo | `docs/evidence/<GID>/config_<GID>_g<NN>.json` (Appendix F, *Mandatory Rules* 3–4) |
| 4 | **Live GUI belief-map** screenshot | [`docs/images/thief-gui-belief-map.png`](docs/images/thief-gui-belief-map.png) — README §5.1 |
| 5 | **Replay `VERIFIED OK`** screenshot | [`docs/images/thief-replay-verified-ok.png`](docs/images/thief-replay-verified-ok.png) — README §5.2 |
| 6 | End-of-game report e-mail sent, each group separately | all seven counted matches; ledger in [`docs/COST_AUDIT.md`](docs/COST_AUDIT.md) |
| 7 | Quality gates green | pytest + 85% coverage floor, zero Ruff, 150-line limit, secret scan — [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| 8 | Secret scan clean | `uv run python scripts/secret_scan.py` — gates on what git would publish |
| 9 | Annotated submission tag created and pushed | `v1.0-submission`, pointing at the submitted commit |
| 10 | **Both repositories public** — Appendix C §1 satisfied without an invitation | GitHub repository settings |
| 11 | Companion repository cross-linked | README §6 → [Police repo](https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police) |

## Open — off-platform actions only

| # | Action | Why it is not automated |
|---|---|---|
| B | **Re-point `v1.0-submission` at the final commit.** The tag is pushed but was cut before the final documentation and evidence commits, so it does not freeze the submitted version. | Moving a published tag requires a force update of a remote ref |
| A | **Moodle submission.** Download the Word template, fill it in without moving or altering any field, save as PDF, and submit — **separately for each team member** (Amir Fadila, Eman Sarhan), with group code `amireman` and both repository links. | Off-platform, per-student action |
| B | **Enter the code-quality self-grade** on the Moodle form. Rule #55 and §11.5(ו) require it to score *code quality only*, never the league result. A defensible basis is in [`docs/QUALITY-25010.md`](docs/QUALITY-25010.md). | A judgement the team must make and sign |

Companion repository: https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police
