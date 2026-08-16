"""Explicit version tracking for code and configuration (guidelines §8.1, Table 2).

``CODE_VERSION`` is the running software release. It is reported in the Step-0 declaration
and in the peer hello, and it is deliberately **not** part of the negotiated agreement:
``peer.handshake.check_compatibility`` compares only ``protocol_version`` and
``schema_version``, so two peers on different code versions still interoperate.

Historical note — the counted match **G020 was played by release ``0.1.0-day1``**, and every
artifact of that match truthfully records that string. Those files are immutable evidence
and are never rewritten; this constant describes the *current* submission release only.
"""

from ..exceptions import ConfigError

#: Current software release (guidelines require a 1.00-series submission version).
CODE_VERSION = "1.00"

#: Release that played the official counted match G020; kept for provenance only.
G020_CODE_VERSION = "0.1.0-day1"

#: Expected ``version`` key in ``config/game.json``.
CONFIG_VERSION = "1.00"

#: Config versions this release can load. Widen deliberately, never silently.
SUPPORTED_CONFIG_VERSIONS = frozenset({"1.00"})


def check_config_version(cfg: dict) -> str:
    """Validate the config's declared version at startup.

    A config with no ``version`` key is accepted as ``1.00`` so that an opponent's shared
    contract file - which is written to the rulebook's Appendix-F shape and carries no
    version key - still loads. An explicitly *incompatible* version fails closed.
    """
    declared = str(cfg.get("version", CONFIG_VERSION))
    if declared not in SUPPORTED_CONFIG_VERSIONS:
        raise ConfigError(
            f"config version {declared!r} is not supported by code {CODE_VERSION} "
            f"(supported: {sorted(SUPPORTED_CONFIG_VERSIONS)})"
        )
    return declared
