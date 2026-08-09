"""Post-run e-mail for the interop CLI, kept OUT of the friendly module so that module
stays structurally mail-free. Reuses the existing Gmail sender only. Demo mode targets an
explicit non-lecturer address (via the counted should_send bypass); official mode targets
the lecturer default. Any Gmail failure keeps all artifacts (nothing is deleted)."""

import os
from argparse import Namespace

from ..infra import gmail_auth as ga
from ..infra import gmail_cli as gc
from ..infra import gmail_report as gr


def demo_email(out: str, game_id: str, recipient: str) -> None:
    """DEMO ONLY: email the generated result JSON to an explicit non-lecturer recipient."""
    rc = gc.run(
        Namespace(
            action="send",
            dir=out,
            game_id=game_id,
            recipient=recipient,
            email_mode="send",
            demo_allow_uncounted=True,
        )
    )
    print(f"  demo_email_sent={rc == 0}  recipient={recipient}")


def official_email(out: str, game_id: str) -> None:
    """OFFICIAL: email the ONE generated result JSON to the lecturer default, once.

    Reuses the existing sender primitives; the gate is the CLEAN final audit checked by the
    caller. Recipient is the lecturer default — never the demo address."""
    name, blob = gr.report_attachment(out, game_id)  # the ONE result JSON (that exact file)
    gr.validate_attachment(blob)
    recipient = ga.email_settings(None, "send")["recipient"]  # lecturer default
    msg = gr.build_message("me", recipient, gc._subject(game_id), gc._body(game_id), name, blob)
    try:
        service = ga.build_service()
    except RuntimeError as exc:
        print(f"  EMAIL FAILED: {exc}; result saved, nothing sent.")
        return
    marker = os.path.join(out, f"gmail_sent_{game_id}.json")
    res = gr.send_report(service, msg, marker)  # idempotent: exactly one email
    print(f"  lecturer_report_sent={res['status']} id={res.get('message_id')} to={recipient}")
