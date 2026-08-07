"""Official deterministic shared identifiers (reference-v3 / book App. F).

Both peers derive IDENTICAL values from data they both hold after the handshake —
the agreed terms plus the two group ids — so no extra round-trip is needed. The
construction is byte-for-byte the official one and is locked by the kit's
``vectors/game_uid.json``:

    game_id  = "-vs-".join(sorted([group_a, group_b]))
    game_uid = str(UUID(bytes=SHA256(canonical(terms)|"|".join(sorted(pair)))[:16]))
"""

import hashlib
import uuid

from ..domain.crypto import canonical_json


def derive_game_ids(terms: dict, group_a: str, group_b: str) -> tuple[str, str]:
    """Return (game_id, game_uid) — identical for both peers, order-independent."""
    pair = sorted([group_a, group_b])
    game_id = f"{pair[0]}-vs-{pair[1]}"
    seed = f"{canonical_json(terms)}|{'|'.join(pair)}"
    game_uid = str(uuid.UUID(bytes=hashlib.sha256(seed.encode()).digest()[:16]))
    return game_id, game_uid


def declaration_name(gid: str) -> str:
    return f"declaration_{gid}.json"


def config_name(gid: str, nn: int) -> str:
    return f"config_{gid}_g{nn:02d}.json"


def log_name(gid: str, nn: int) -> str:
    return f"log_{gid}_g{nn:02d}.json"


def result_name(gid: str) -> str:
    return f"result_{gid}.json"


def links(gid: str) -> dict:
    """Logical role -> filename; per-sub-game files keep the literal g<NN> placeholder."""
    return {
        "declaration": declaration_name(gid),
        "config": f"config_{gid}_g<NN>.json",
        "log": f"log_{gid}_g<NN>.json",
        "result": result_name(gid),
    }
