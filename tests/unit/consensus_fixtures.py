"""Frozen settlement rows from our two FILED counted series, as inert test data.

Copied out of the filed artifacts once and pinned here so the historical digests can be
re-proved without a test ever opening — let alone writing — a historical run directory.
Only the five consensus keys per sub-game plus the signed aggregate are kept; that is
exactly what the digest is computed over.

G002 = amireman vs uoh-ay26. G020 = amireman vs Orcai-MJ.
"""

G020_GAME_ID = "G020"
G020_GAME_UID = "e78cb3a7-a5a9-8321-a6ef-0f0cddfc8796"
G020_LEGACY_SHA = "ceceb3dd6fccdff03fb862c9532e14fc24ac87002595365835cf42c1171835ca"
G020_REFERENCE_SHA = "d41bdf24ece10d2eb21b2a7c64c6a509ee73c8244340bd5d6675ce92b6bd75a7"

_G020_SURVIVAL = {
    "result": "survival",
    "roles": {"Orcai-MJ": "police", "amireman": "thief"},
    "score": {"Orcai-MJ": 5, "amireman": 10},
    "winner_group": "amireman",
}
_G020_CAPTURE = {
    "result": "capture",
    "roles": {"Orcai-MJ": "thief", "amireman": "police"},
    "score": {"Orcai-MJ": 5, "amireman": 20},
    "winner_group": "amireman",
}
G020_ROWS: list[dict] = [
    {"sub_game_number": n, **(_G020_SURVIVAL if n % 2 else _G020_CAPTURE)} for n in range(1, 7)
]
G020_AGGREGATE: dict = {
    "total_score": {"Orcai-MJ": 30, "amireman": 90},
    "sub_games_won": {"Orcai-MJ": 0, "amireman": 6},
    "ties": 0,
    "winner_group": "amireman",
    "series_tie": False,
}

G002_GAME_ID = "G002"
G002_GAME_UID = "605f754b-7c28-3691-a5cf-f655e485e8ca"
G002_LEGACY_SHA = "c8ddf64616d87d78ac70ebe7989de4b0e689fcec970abebb6ab01a7dab0a6e28"

_G002_WE_SURVIVE = {
    "result": "survival",
    "roles": {"amireman": "thief", "uoh-ay26": "police"},
    "score": {"amireman": 10, "uoh-ay26": 5},
    "winner_group": "amireman",
}
_G002_THEY_SURVIVE = {
    "result": "survival",
    "roles": {"amireman": "police", "uoh-ay26": "thief"},
    "score": {"amireman": 5, "uoh-ay26": 10},
    "winner_group": "uoh-ay26",
}
_G002_THEY_CAPTURE = {
    "result": "capture",
    "roles": {"amireman": "thief", "uoh-ay26": "police"},
    "score": {"amireman": 5, "uoh-ay26": 20},
    "winner_group": "uoh-ay26",
}
G002_ROWS: list[dict] = [
    {"sub_game_number": 1, **_G002_WE_SURVIVE},
    {"sub_game_number": 2, **_G002_THEY_SURVIVE},
    {"sub_game_number": 3, **_G002_THEY_CAPTURE},
    {"sub_game_number": 4, **_G002_THEY_SURVIVE},
    {"sub_game_number": 5, **_G002_WE_SURVIVE},
    {"sub_game_number": 6, **_G002_THEY_SURVIVE},
]
