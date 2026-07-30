"""Typed errors for fail-closed behavior across the agent."""


class ConfigError(ValueError):
    """Raised on missing, malformed, or spec-violating configuration."""


class CryptoError(ValueError):
    """Raised on commit/verify mismatch (tamper) or malformed crypto input."""


class IllegalTransitionError(RuntimeError):
    """Raised when the state machine is asked for a disallowed transition."""


class TechnicalLossError(RuntimeError):
    """Raised to route a sub-game to the 0/0 technical-loss outcome."""
