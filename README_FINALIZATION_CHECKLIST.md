# Finalization checklist

Everything else in the submission is done. These are the only actions genuinely
outstanding, and all of them depend on the remaining league match(es) being played.

| # | Action | Where |
|---|---|---|
| 1 | ~~Play the remaining counted series~~ **DONE** — G020 vs `Orcai-MJ`, 90 : 30, 6–0, all audits verified | league |
| 2 | ~~Insert the final match evidence~~ **DONE** — G020 vs `Orcai-MJ`, 90 : 30, 6–0, all audits verified, consensus confirmed | `README.md` §7.1 |
| 3 | ~~Capture the **Live GUI belief-map** screenshot~~ **DONE** → `docs/images/thief-gui-belief-map.png`, embedded in §5.1 | `uv run python scripts/capture_gui.py live --dir <evidence> --game-id <id> --role thief --out docs/images/thief-gui-belief-map.png` |
| 4 | ~~Capture the **Replay `VERIFIED OK`** screenshot~~ **DONE** → `docs/images/thief-replay-verified-ok.png` (real G020), embedded in §5.2 | `uv run python scripts/capture_gui.py replay --dir docs/evidence/G020 --game-id G020 --expect "VERIFIED OK" --out docs/images/thief-replay-verified-ok.png` |
| 5 | Confirm the end-of-game report email was sent for the final match (both groups send separately) | `uv run python -m thief_agent gmail --action send --dir <dir> --game-id <GAME_ID>` |
| 6 | Update the test count in §7.3 only if code changed | `uv run pytest` |
| 7 | Final secret scan | `uv run python scripts/secret_scan.py` |
| 8 | ~~Create and push the annotated submission tag~~ **DONE** | `git tag -a v1.0-submission -m "Final submission: Police-Thief P2P, group amireman"` then `git push origin v1.0-submission` |
| 9 | Final push of both repositories | `git push origin <branch>` |

Companion repository: https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police
