"""Byte-level conformance of OUR production crypto against the official interop CORE
vectors (copthief-league-protocol @ 596aaf4, aligned to book v3.0.0, SPEC §2/§3/§4).

Proves our own `canonical_json` / `commit_of` reproduce the pinned bytes, so our revealed
log survives an independent opponent's cross-team audit. Vector *data* is factual (pinned
digests); no external implementation code is imported. See docs/INTEROP_GAP_REPORT.md for
the identifier/wire gaps that remain OUT of scope for these primitives."""

import hashlib

from thief_agent.domain.crypto import canonical_json, commit_of

# --- SPEC §2: canonical JSON (object -> canonical string, sha256) ---
CANONICAL = [
    (
        {"b": 1, "a": {"d": 4, "c": 3}},
        '{"a":{"c":3,"d":4},"b":1}',
        "943d56ce0b02b80a8afcd12d849426226b68f2d8cd2840af8f6f93067f14c360",
    ),
    (
        {"hint": "אני ליד הכיכר", "move": "MOVE:N"},
        '{"hint":"אני ליד הכיכר","move":"MOVE:N"}',
        "7461690c1167e6a4b44927a507e81aa38f290d9be8f662a1c0ea689d76b8bcc7",
    ),
    (
        {"emoji": "🙂", "x": 1},
        '{"emoji":"🙂","x":1}',
        "a16621d5cba0b8a1ce5909e74c0d2679295ae11eec4ccbf5f7e8550ecea3690d",
    ),
    (
        {
            "decay_per_step": 0.1,
            "emit_intensity": 0.9,
            "min_center_intensity": 0.5,
            "ram_gb": 31.8,
            "vram_gb": 6.0,
        },
        '{"decay_per_step":0.1,"emit_intensity":0.9,"min_center_intensity":0.5,"ram_gb":31.8,"vram_gb":6.0}',
        "62469a4afd756d527d881563440dbd82e2bc694cfd97516adacecb40a178483e",
    ),
    (
        {"a": True, "b": None, "c": [1, 2, 3]},
        '{"a":true,"b":null,"c":[1,2,3]}',
        "6e96c2da7b746f9e47d1bd8ee49e5e385de926c51e3a7f3fe9886ca02a29d351",
    ),
    (
        {"🙂": "astral key", "～": "high-BMP key"},
        '{"～":"high-BMP key","🙂":"astral key"}',
        "46193c64b2be01fac9662e4f211b64ff39a95d0c5f803b6971e4415186f3f146",
    ),
    (
        {"tiny": 1e-07, "huge": 1e16},
        '{"huge":1e+16,"tiny":1e-07}',
        "e4d847a30f5a6af84ea0b57471959195ad037f50a30f34534c1ee101e1b1cfc6",
    ),
]

# --- SPEC §3: commit = SHA256(canonical(payload)+"|"+nonce) ---
COMMITS = [
    (
        {
            "step": 0,
            "type": "system_spec",
            "spec": {"os": "Linux", "cpu_cores": 4, "ram_gb": 16.0, "vram_gb": 0.0},
            "model": "cli-default",
            "code_version": "1.0",
            "group_name": "Example-Team",
            "sub_game_number": 1,
        },
        "0f1e2d3c4b5a69788796a5b4c3d2e1f0",
        "69c9a786d18829990291cd0ffb768eacfa009011b0c89a6f4f32330551e2003e",
    ),
    (
        {
            "step": 1,
            "state": "grid=7x7;self=[4, 3];barriers=[]",
            "position": [4, 3],
            "move": "MOVE:S",
            "intent": "truth",
            "hint": "I keep to the main avenues.",
        },
        "112233445566778899aabbccddeeff00",
        "aa6420e2d3a907d6c140856caecbb351b4d5ad98e381549c28268669af378dcc",
    ),
    (
        {
            "step": 2,
            "state": "grid=7x7;self=[2, 4];barriers=[[1, 1]]",
            "position": [2, 4],
            "move": "MOVE:N",
            "intent": "lie",
            "hint": "אני ליד הכיכר 🙂",
        },
        "deadbeefcafef00dfeedface00c0ffee",
        "2caaeb0a7e656868b85166a9ebe34226bae4fdcb79cb7a0a23759121769d9338",
    ),
]

# --- SPEC §4: terms_signature = commit form over the agreed terms ---
_TERMS = {
    "board_size": 7,
    "smell_grid_size": 5,
    "decay_per_step": 0.1,
    "emit_intensity": 0.9,
    "min_center_intensity": 0.5,
    "max_steps": 35,
    "barriers_max": 14,
    "setting": "Haifa",
    "hint_max_words": 15,
    "axis_origin_corner": "top-left",
    "axis_start_index": 0,
    "thief_start": [3, 3],
    "cop_start": [0, 0],
    "num_games": 1,
}
_TERMS_NONCE = "a1a2a3a4b1b2b3b4c1c2c3c4d1d2d3d4"
_TERMS_SIG = "80793141f22b6193b02a74d5955767ad1e24abbac172894358ec13622b85a04c"


def test_canonical_json_bytes_match_core_vectors():
    for obj, expected, digest in CANONICAL:
        got = canonical_json(obj)
        assert got == expected, f"{obj!r}: {got!r} != {expected!r}"
        assert hashlib.sha256(got.encode("utf-8")).hexdigest() == digest


def test_commit_reveal_matches_reference_form():
    for payload, nonce, commit in COMMITS:
        assert commit_of(payload, nonce) == commit


def test_our_commit_primitive_reproduces_official_terms_signature():
    # our commit_of primitive produces the exact official §4 agreement-signature bytes
    assert commit_of(_TERMS, _TERMS_NONCE) == _TERMS_SIG
