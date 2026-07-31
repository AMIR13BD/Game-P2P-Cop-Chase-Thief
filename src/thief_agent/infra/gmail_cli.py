"""CLI dispatch for the Gmail reporting path (P23): bootstrap | validate | dryrun |
send. Draft/dry-run never sends. Send is gated on six sub-games + a confirmed final
audit, is idempotent, and fails clearly (BLOCKED-EXTERNAL) when OAuth files are absent."""

import json
import os

from . import gmail_auth as ga
from . import gmail_report as gr


def _subject(gid: str) -> str:
    return f"[uoh26finalgame] result report {gid}"


def _body(gid: str) -> str:
    return f"Automated final result report for game {gid}. Signed JSON report attached."


def _dryrun(args, st, name, msg) -> int:
    out = os.path.join(args.dir, f"gmail_dryrun_{args.game_id}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "recipient": st["recipient"],
                "subject": _subject(args.game_id),
                "attachment": name,
                "raw_len": len(msg["raw"]),
                "sent": False,
            },
            fh,
            indent=2,
        )
    print(f"DRY-RUN prepared report for {st['recipient']} attachment={name}; sent nothing -> {out}")
    return 0


def run(args) -> int:
    if args.action == "bootstrap":
        try:
            print("gmail bootstrap ->", ga.bootstrap())
            return 0
        except RuntimeError as exc:
            print(exc)
            return 2
    result = gr.load_result(args.dir, args.game_id)
    ok, reason = gr.should_send(result)
    if args.action == "validate":
        print(f"would_send={ok} reason={reason}")
        return 0 if ok else 1
    if not ok:
        print(f"NOT SENDING (fail-closed): {reason}")
        return 1
    name, blob = gr.report_attachment(args.dir, args.game_id)
    try:
        gr.validate_attachment(blob)
    except ValueError as exc:
        print(f"NOT SENDING (fail-closed): {exc}")
        return 1
    st = ga.email_settings(args.recipient, args.email_mode)
    msg = gr.build_message(
        "me", st["recipient"], _subject(args.game_id), _body(args.game_id), name, blob
    )
    if args.action == "dryrun" or st["mode"] == "draft":
        return _dryrun(args, st, name, msg)
    try:
        service = ga.build_service()
    except RuntimeError as exc:
        print(exc)
        return 2
    marker = os.path.join(args.dir, f"gmail_sent_{args.game_id}.json")
    res = gr.send_report(service, msg, marker)
    print(f"gmail {res['status']} message_id={res.get('message_id')}")
    return 0
