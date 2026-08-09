"""Official-protocol (reference-v3) cross-team interoperability adapter.

A neutral wire layer that lets our production strategy engine play an
independently-implemented official/reference-compatible peer WITHOUT touching any
strategy code. It re-uses our already-conformant crypto (canonical JSON +
commit-reveal) and wraps our brains behind the official MCP tool set
(``negotiate`` / ``receive_turn`` / ``submit_audit`` / ``receive_control``) with the
symmetric dual-server, pushed-turn connection model the reference uses.

Nothing in this package imports Gmail/reporting: friendly play is *structurally*
unable to email a lecturer (see ``friendly``).
"""

CODE_VERSION = "interop-1.0.0"
DEFAULT_GROUP_ID = "amireman"
# Our real team roster, advertised in the negotiated identity (declaration ``members``).
# A peer's final audit checks that our ``members`` is non-empty, so this must never be [].
DEFAULT_MEMBERS = ["Amir Fadila", "Eman Sarhan"]
