"""Typed errors for fail-closed behavior across the agent."""


class ConfigError(ValueError):
    """Raised on missing, malformed, or spec-violating configuration."""


class CryptoError(ValueError):
    """Raised on commit/verify mismatch (tamper) or malformed crypto input."""


class IllegalTransitionError(RuntimeError):
    """Raised when the state machine is asked for a disallowed transition."""


class TechnicalLossError(RuntimeError):
    """Raised to route a sub-game to the 0/0 technical-loss outcome."""


class ArtifactError(ValueError):
    """Raised on missing/malformed/schema-invalid or mismatched artifact evidence."""


class NetworkError(RuntimeError):
    """Base for transport/reliability failures."""


class RateLimitError(NetworkError):
    """Outgoing request rate exceeded the configured limit."""


class QueueFullError(NetworkError):
    """Bounded request queue is full (DoS guard)."""


class ProtocolError(NetworkError):
    """Response correlation/session/ordering violation."""


class ExhaustedRetriesError(NetworkError):
    """All retries exhausted; caller maps this to a technical loss."""
