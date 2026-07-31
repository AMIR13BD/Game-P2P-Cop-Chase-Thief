# Gmail OAuth setup (BLOCKED-EXTERNAL)

The Gmail reporting code is fully implemented and locally validated with mocks; the
real send requires a one-time external setup that needs Google Cloud access, a browser
consent, and a network send. None of these can be done autonomously. Perform these
steps when you (a human) are available.

## Scope
Only `https://www.googleapis.com/auth/gmail.send`. Never request read scopes.

## One-time steps (you run these)
1. In Google Cloud Console, create/pick a project; enable the **Gmail API**.
2. Create an **OAuth client ID** of type *Desktop app*. Download the JSON as
   `credentials.json` into the repo root (it is git-ignored; never commit it).
3. Install the Gmail extra and mint a send-only token:
   ```bash
   uv sync --extra gmail
   uv run python -m thief_agent gmail --action bootstrap
   ```
   This opens a browser for consent and writes `token.json` (git-ignored).
4. Validate + dry-run against a completed game (no send):
   ```bash
   uv run python -m thief_agent gmail --action validate --dir artifacts_net --game-id <gid>
   uv run python -m thief_agent gmail --action dryrun   --dir artifacts_net --game-id <gid>
   ```
5. Real send (only after six sub-games + confirmed final audit; set mode away from
   draft, e.g. `--email-mode send`):
   ```bash
   uv run python -m thief_agent gmail --action send --dir artifacts_net --game-id <gid> --email-mode send
   ```

## Behaviour guarantees (already implemented + tested)
- Never sends on technical failure, disagreement, or a failed/tampered audit.
- Idempotent: a `gmail_sent_<gid>.json` marker prevents duplicate sends after retry/restart.
- Draft/dry-run modes never send and produce the exact attachment for inspection.
- Absent/expired/revoked credentials -> a clear `BLOCKED-EXTERNAL` error; nothing sent.
- Credentials/token loaded only from ignored paths (`PT_GMAIL_CREDENTIALS`,
  `PT_GMAIL_TOKEN`), never logged or committed.

## Pending external evidence
- Google Cloud project + OAuth consent screenshots.
- Real Gmail sent-message id.
Do not fabricate any of these; capture them during the real run.
