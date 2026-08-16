"""Thief agent for the distributed P2P Police-Thief league (team `amireman`).

The public entry point is the SDK facade: every business operation is reached through
`AgentSDK` rather than by importing engine internals.
"""

from .shared.version import CODE_VERSION

__version__ = CODE_VERSION
__all__ = ["AgentSDK", "CODE_VERSION", "__version__"]


def __getattr__(name: str):
    """Lazily expose the SDK facade so importing the package stays cheap."""
    if name == "AgentSDK":
        from .sdk.sdk import AgentSDK

        return AgentSDK
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
