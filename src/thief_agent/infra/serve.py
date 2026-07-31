"""Launch a peer's real FastMCP HTTP server as an independent process."""

from ..security.auth import AuthRegistry
from ..security.signer import DevTestSigner
from ..shared.config_validate import validate
from ..shared.defaults import DEFAULT_GAME_CONFIG
from ..shared.gitinfo import current_commit
from .mcp_server import PeerConfig, build_server


def make_terms(grid: int | None = None) -> dict:
    terms = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT_GAME_CONFIG.items()}
    if grid:
        terms["board_and_agents"] = {**terms["board_and_agents"], "grid_size": grid}
    return terms


def run(
    host: str,
    port: int,
    group: str,
    valid: list[str],
    revoked: list[str],
    seed: int = 1234,
    grid: int | None = None,
) -> None:
    pc = PeerConfig(
        group=group,
        terms=make_terms(grid),
        flat_cfg=validate(DEFAULT_GAME_CONFIG),
        auth=AuthRegistry(set(valid), set(revoked)),
        github_commit=current_commit(default="0" * 40),
        signer=DevTestSigner(),
        seed=seed,
    )
    build_server(pc).run(transport="http", host=host, port=port, show_banner=False)
