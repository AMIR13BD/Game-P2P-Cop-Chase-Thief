"""Gmail API reporting (P23): build the mandatory signed-JSON report email and send it
idempotently, ONLY after six sub-games and a successful final mutual audit. Gmail API
only (never SMTP); scope gmail.send only. Message construction is pure stdlib and fully
testable; the live transport is injected (mocked in tests, real service in production).
No secret data is logged; credentials/token live only in ignored local paths."""

import base64
import json
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..report import ids

SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
MAX_REPORT_BYTES = 5_000_000  # reject an oversized/empty report attachment (fail closed)


def validate_attachment(blob: bytes) -> None:
    """Fail closed on an empty or oversized report attachment before sending."""
    if not blob:
        raise ValueError("empty report attachment")
    if len(blob) > MAX_REPORT_BYTES:
        raise ValueError(f"report attachment too large ({len(blob)} bytes)")


def should_send(result: dict) -> tuple[bool, str]:
    """Gate: exactly six sub-games, none technical/tampered, and a confirmed final
    mutual agreement. Never send on technical failure, disagreement, or failed audit."""
    if not isinstance(result, dict):
        return False, "no result"
    subs = result.get("sub_games", [])
    if len(subs) != 6:
        return False, f"need six sub-games, found {len(subs)}"
    for sg in subs:
        if sg.get("result") == "technical" or sg.get("audit", {}).get("tampered"):
            return False, "a technical or tampered sub-game is present"
    ma = result.get("mutual_agreement", {})
    if not ma.get("confirmed"):
        return False, "final mutual agreement not confirmed"
    if ma.get("mode") == "counted-two-peer":
        confs = ma.get("confirmations", {})
        groups = {c.get("group") for c in confs.values() if isinstance(c, dict)}
        hashes = {c.get("final_sha256") for c in confs.values() if isinstance(c, dict)}
        if len(confs) < 2 or len(groups) < 2 or len(hashes) != 1:
            return False, "two-peer confirmations missing or disagree"
    return True, "ok"


def build_message(sender: str, recipient: str, subject: str, body: str, name: str, blob: bytes):
    """A base64url-encoded Gmail message with the JSON report as an attachment."""
    msg = MIMEMultipart()
    msg["to"], msg["from"], msg["subject"] = recipient, sender, subject
    msg.attach(MIMEText(body, "plain"))
    part = MIMEApplication(blob, _subtype="json", Name=name)
    part["Content-Disposition"] = f'attachment; filename="{name}"'
    msg.attach(part)
    return {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")}


def load_result(dirpath: str, gid: str) -> dict:
    with open(os.path.join(dirpath, ids.result_name(gid)), encoding="utf-8") as fh:
        return json.load(fh)


def report_attachment(dirpath: str, gid: str) -> tuple[str, bytes]:
    """The mandatory JSON report artifact (name, bytes)."""
    name = ids.result_name(gid)
    with open(os.path.join(dirpath, name), "rb") as fh:
        return name, fh.read()


def send_report(service, message: dict, marker_path: str) -> dict:
    """Idempotent send: if the marker exists, skip (already sent after retry/restart);
    otherwise send via the Gmail service and record the returned message id."""
    if os.path.exists(marker_path):
        with open(marker_path, encoding="utf-8") as fh:
            prev = json.loads(fh.read() or "{}")
        return {"status": "skipped-already-sent", "message_id": prev.get("message_id")}
    resp = service.users().messages().send(userId="me", body=message).execute()
    mid = resp.get("id")
    with open(marker_path, "w", encoding="utf-8") as fh:
        json.dump({"message_id": mid}, fh)
    return {"status": "sent", "message_id": mid}
