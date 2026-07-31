"""Single entry-point facade for every agent business operation.

External consumers construct one AgentSDK bound to this peer's identity and drive
all operations through it -- local series, networked series, batch simulation,
artifact emit+verify, and the counted-match audit -- without importing internal
domain/peer/report modules directly."""

from ..constants import Role
from ..report.emit import emit_series
from ..report.verify import verify_match, verify_series
from ..sdk.series import run_series
from ..sim.batch import run_batch


class AgentSDK:
    def __init__(self, natural_role: Role, group_name: str, signer, github_commit: str) -> None:
        self.natural_role = natural_role
        self.group_name = group_name
        self.signer = signer
        self.github_commit = github_commit

    def local_series(self, cfg: dict, seed: int = 1234) -> dict:
        """Run a local six-sub-game series with role alternation and mutual audit."""
        return run_series(
            cfg,
            self.natural_role,
            self.group_name,
            self.signer,
            seed=seed,
            github_commit=self.github_commit,
        )

    async def networked_series(self, url, token, cfg, seed: int = 1234, terms=None) -> dict:
        """Drive a distributed six-sub-game series over real FastMCP transport."""
        from ..peer.net_runtime import run_networked

        return await run_networked(
            url,
            token,
            cfg,
            self.natural_role,
            self.group_name,
            self.github_commit,
            self.signer,
            seed,
            terms,
        )

    def simulate(self, cfg: dict, turns: int = 10000) -> dict:
        """Run a deterministic headless batch and return aggregate counters."""
        return run_batch(cfg, min_turns=turns)

    def _repos(self, opponent: str) -> dict:
        local = {"cop": "local", "thief": "local"}
        return {self.group_name: local, opponent: local}

    def emit_and_verify(
        self, out, gid, opponent, series, cfg, peer_commit=None, peer_ident=None
    ) -> dict:
        """Write the four artifacts, then run the integrity audit over them."""
        emit_series(
            out,
            gid,
            {**cfg, "agreed_between": [self.group_name, opponent]},
            self.group_name,
            opponent,
            series,
            self.github_commit,
            self._repos(opponent),
            self.signer,
            peer_commit=peer_commit,
            peer_ident=peer_ident,
        )
        return verify_series(out, gid, self.signer)

    def verify_match(self, out, gid) -> dict:
        """Run the strict counted-match cross-repo audit over emitted artifacts."""
        return verify_match(out, gid, self.signer)
