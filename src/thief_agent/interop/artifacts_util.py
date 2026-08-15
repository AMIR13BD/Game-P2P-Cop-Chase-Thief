"""Canonical hashing and hardware-spec shaping for the official submission artifacts.

Split out of ``artifacts.py`` purely to keep each module inside the repository's 150-line
ceiling. Both helpers are byte-for-byte identical to their previous definitions, so every
emitted artifact — and every canonical hash inside it — is unchanged.
"""

import hashlib

from ..domain.crypto import canonical_json


def canon_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def hardware_block(spec: dict) -> dict:
    return {
        "cpu_type": spec.get("cpu_type"),
        "cpu_freq_mhz": spec.get("cpu_freq_mhz"),
        "cpu_cores": spec.get("cpu_cores"),
        "ram_gb": spec.get("ram_gb"),
        "gpu_model": spec.get("gpu_type"),
        "vram_gb": spec.get("vram_gb"),
    }
