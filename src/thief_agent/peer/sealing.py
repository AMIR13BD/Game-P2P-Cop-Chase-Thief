"""Step-0 declaration: hardware + code version + group + Git commit, sealed & signed.

`github_commit` is required (no silent 'unknown'); the caller resolves it once at
the application boundary and passes it in, keeping domain code pure."""

from typing import Any

from ..domain.crypto import seal
from ..shared.sysinfo import system_spec
from ..shared.version import CODE_VERSION


def step0_payload(group_name: str, sub_game: int, github_commit: str) -> dict[str, Any]:
    return {
        "step": 0,
        "type": "system_spec",
        "spec": system_spec(),
        "code_version": CODE_VERSION,
        "group_name": group_name,
        "sub_game_number": sub_game,
        "github_commit": github_commit,
    }


def make_step0_record(group_name: str, sub_game: int, signer, github_commit: str) -> dict:
    payload = step0_payload(group_name, sub_game, github_commit)
    sealed = seal(payload)
    return {
        "payload": payload,
        "nonce": sealed["nonce"],
        "commit": sealed["commit"],
        "signature": signer.sign(payload),
        "signer": signer.name,
    }
