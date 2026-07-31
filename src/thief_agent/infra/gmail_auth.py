"""Gmail OAuth wiring (P23): send-only credentials/token loaded ONLY from ignored
local paths or environment; build the Gmail API service. No secret is ever logged or
committed. OAuth bootstrap and the live service require the google libraries plus a
real credentials.json and are BLOCKED-EXTERNAL until those are provided."""

import os

DEFAULT_RECIPIENT = "rmisegal+uoh26finalgame@gmail.com"  # from the project PDF [email]
SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


def credentials_path() -> str:
    return os.environ.get("PT_GMAIL_CREDENTIALS", "credentials.json")


def token_path() -> str:
    return os.environ.get("PT_GMAIL_TOKEN", "token.json")


def email_settings(recipient: str | None = None, mode: str | None = None) -> dict:
    """Resolve [email] settings: recipient + mode (draft = never sends)."""
    return {
        "recipient": recipient or os.environ.get("PT_GMAIL_RECIPIENT", DEFAULT_RECIPIENT),
        "mode": mode or os.environ.get("PT_GMAIL_MODE", "draft"),
    }


def build_service():
    """Build the Gmail service from an existing send-only token. Clear BLOCKED-EXTERNAL
    error if the token or google libraries are absent."""
    tp = token_path()
    if not os.path.exists(tp):
        raise RuntimeError(f"BLOCKED-EXTERNAL: Gmail token missing at {tp}; run 'gmail bootstrap'")
    try:
        from google.oauth2.credentials import Credentials  # pragma: no cover - needs lib
        from googleapiclient.discovery import build  # pragma: no cover - needs lib
    except ImportError as exc:
        raise RuntimeError(
            "BLOCKED-EXTERNAL: install google-api-python-client google-auth-oauthlib"
        ) from exc
    creds = Credentials.from_authorized_user_file(tp, [SEND_SCOPE])  # pragma: no cover
    return build("gmail", "v1", credentials=creds)  # pragma: no cover


def bootstrap():
    """Run the OAuth installed-app flow to mint a send-only token. BLOCKED-EXTERNAL:
    requires credentials.json (Google Cloud OAuth client) + browser consent."""
    cp = credentials_path()
    if not os.path.exists(cp):
        raise RuntimeError(f"BLOCKED-EXTERNAL: {cp} (Google OAuth client) not present")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow  # pragma: no cover - needs lib
    except ImportError as exc:
        raise RuntimeError("BLOCKED-EXTERNAL: install google-auth-oauthlib") from exc
    flow = InstalledAppFlow.from_client_secrets_file(cp, [SEND_SCOPE])  # pragma: no cover
    creds = flow.run_local_server(port=0)  # pragma: no cover
    with open(token_path(), "w", encoding="utf-8") as fh:  # pragma: no cover
        fh.write(creds.to_json())  # pragma: no cover
    return token_path()  # pragma: no cover
