# Finalization checklist

Everything else in the submission is done. These are the only actions genuinely
outstanding, and all of them depend on the remaining league match(es) being played.

| # | Action | Where |
|---|---|---|
| 1 | Play the remaining counted series and record the verified result | league |
| 2 | Insert the final match evidence — game id, score, per-sub-game results, audit status | `README.md` §7.1, replacing the `FINAL-SUBMISSION TODO` marker |
| 3 | Capture the **Live GUI belief-map** screenshot → `docs/images/gui-belief-map.png`, then replace the marker in §5 with an image link | `uv run python -m thief_agent view` (for a peaked posterior, capture mid-game from a live `netplay` session) |
| 4 | Capture the **Replay `VERIFIED OK`** screenshot → `docs/images/replay-verified-ok.png`, then replace the marker in §5 with an image link | `uv run python -m thief_agent replay --dir <artifacts-dir> --game-id <GAME_ID>` |
| 5 | Confirm the end-of-game report email was sent for the final match (both groups send separately) | `uv run python -m thief_agent gmail --action send --dir <dir> --game-id <GAME_ID>` |
| 6 | Update the test count in §7.3 only if code changed | `uv run pytest` |
| 7 | Final secret scan | `uv run python scripts/secret_scan.py` |
| 8 | Create and push the annotated submission tag (**not before** the match is finished) | `git tag -a v1.0-submission -m "Final submission: Police-Thief P2P, group amireman"` then `git push origin v1.0-submission` |
| 9 | Final push of both repositories | `git push origin <branch>` |

Companion repository: https://github.com/AMIR13BD/Game-P2P-Cop-Chase-Police
