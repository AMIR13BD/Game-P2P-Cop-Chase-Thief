# Submission checklist & evidence index

## Software quality (DONE — locally verified)
- [x] Independent, installable repo (`uv sync`); package `thief_agent` / `thief_agent`.
- [x] Full test suite passes; branch coverage ≥85% (≈89–90%).
- [x] Ruff check + format clean; every tracked `.py` ≤150 physical lines.
- [x] Secret scan clean; `.env`/`credentials.json`/`token.json`/keys git-ignored.
- [x] No parent `.git`; no cross-repo imports/symlinks; `_spec/`/`_reference/` unchanged.
- [x] README user manual + architecture, threat model, testing, tournament, operations,
      per-mechanism PRDs, API/SDK, prompt log docs present.
- [x] Ordered Git history; clean working tree.

## Game / counted-match (DONE locally)
- [x] Six-sub-game role alternation; commit-reveal; mutual audit; technical-loss 0/0.
- [x] Two-peer final confirmation with distinct per-peer keys (forgery fails closed).
- [x] Replay viewer VERIFIED OK / TAMPERED; local-truth GUI (no hidden-position leak).
- [x] Gmail reporting path (gated, idempotent, dry-run) — mocked + dry-run validated.
- [x] Provider-neutral tunnel adapter with TLS enforcement + health check.
- [x] Local two-process counted rehearsal produces a validated evidence bundle.

## BLOCKED-EXTERNAL (require a human + external services; NOT done, NOT faked)
Run these when available; capture the listed evidence.
| Item | Command / action | Evidence to capture |
|---|---|---|
| Gmail OAuth token | `uv sync --extra gmail` then `... gmail --action bootstrap` (needs `credentials.json`) | consent screenshots, `token.json` created (not committed) |
| Real Gmail send | `... gmail --action send --dir <dir> --game-id <gid> --email-mode send` | real sent-message id |
| Public HTTPS tunnel | start provider (ngrok/Localtonet) -> `export PT_TUNNEL_URL=https://.../mcp` | public URL + health-check output |
| Real opponent match | `... netplay --opponent-url https://<opp>/mcp --token <t> --counted` | opponent identity, result artifacts |
| Two-computer run | `serve` on each machine behind tunnels; `netplay` across | both peers' evidence dirs |
| GUI screenshots | render `view` / replay in a terminal and screenshot | `docs/images/*.png` |
| GitHub push/tag | push both repos; tag the submission | repo URLs + tag |
| Moodle submission | submit per course instructions | submission proof |
| Official Step-0 signer | integrate lecturer's key (OfficialSigner) | signed declarations verify under official key |

## Evidence index
- Tournament record: `docs/tournament/champions.json` (real, generated locally).
- Counted rehearsal: run `scripts/counted_rehearsal.py` -> `rehearsal_evidence/rehearsal_summary.json`
  (per-run; git-ignored).
- External evidence above: **placeholders only** until the real runs occur. Nothing is
  fabricated.
