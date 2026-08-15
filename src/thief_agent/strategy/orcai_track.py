"""Roll the modelled Orcai-MJ Thief forward and score how far to trust the model.

The tracker is fed ONLY things we are entitled to know: the signed ``thief_start``
term, the barriers on the public board, the scent WE emit (recomputed from our own
position history with the agreed kernel), and the scent the opponent sends us. It
never sees a true opponent coordinate.

Sequencing matters and follows the wire exactly (thief-first rounds):

  round k:  their Thief turn k   ->   our Police turn k

so when our brain is asked to decide at step k, their k-th move is ALREADY fixed.
``advance`` therefore applies our outbound message k-1 to the mirrored belief and
then steps the model once, yielding the cell they are standing on right now.

``confidence`` is the safety valve: the modelled cell is checked against the scent
they actually broadcast, and a model that stops matching reality drives the brain
back to its general-purpose fallback rather than chasing a fiction.
"""

from ..domain import smell
from ..domain.board import Board, Cell
from .orcai_model import OrcaiBelief, ring_of, ringrunner_next

WINDOW = 8  # rolling window for the agreement score
PEAK_TOLERANCE = 0.92  # modelled cell must carry >= this share of the peak intensity


class OrcaiThiefTracker:
    """Deterministic forward model of their Thief plus a live agreement score."""

    def __init__(self, size: int, thief_start: Cell, rho: float = 0.1) -> None:
        self.size = size
        self.rho = rho
        self.pred: Cell = tuple(thief_start)
        self.belief = OrcaiBelief(size)  # THEIR belief about OUR cop
        self.our_scent: dict = {}  # mirror of the field we have emitted so far
        self.last_step = 0
        self.hits: list[bool] = []
        self.ring_hits: list[bool] = []

    # ------------------------------------------------------------------ model
    def advance(self, obs, board: Board) -> Cell:
        """Advance to their move for THIS round and return the cell they now occupy."""
        if obs.step <= self.last_step:  # idempotent if a brain asks twice in one turn
            return self.pred
        if obs.step > 1:
            # Our message k-1 carried the scent emitted from the cell we are standing
            # on now, and any barrier we declared is already in obs.barriers. Their
            # runtime applies the barrier, then diffuses, then fuses the scent.
            self.our_scent = smell.step_update(self.our_scent, obs.self_pos, board, self.rho)
            self.belief.diffuse(board.barriers)
            self.belief.fuse(self.our_scent)
        self.pred = ringrunner_next(self.pred, self.belief.most_likely(), board)
        self.last_step = obs.step
        return self.pred

    def peek(self, cop_cell: Cell, board: Board) -> Cell:
        """Their NEXT move if we end this turn on `cop_cell`, without mutating state.

        A one-ply lookahead through their real decision function: we know the scent
        that cell would emit, so we know the belief they would hold and therefore the
        move they would make. Used to intercept where they are going, not where they
        were.
        """
        scent = smell.step_update(self.our_scent, cop_cell, board, self.rho)
        shadow = OrcaiBelief(self.size, self.belief.trust)
        shadow.grid = [row[:] for row in self.belief.grid]
        shadow.diffuse(board.barriers)
        shadow.fuse(scent)
        return ringrunner_next(self.pred, shadow.most_likely(), board)

    # ------------------------------------------------------------- confidence
    def resync(self, cell: Cell) -> Cell:
        """Overrule the model with a cell the received scent actually supports.

        Evidence always wins over the model. This keeps the counter correct when the
        seeded start is not the one in play, and lets it recover mid-game if they
        deviate; the agreement score still falls, so a model that needs constant
        correction hands the turn to the general-purpose fallback.
        """
        self.pred = tuple(cell)
        return self.pred

    def score(self, scent: dict, evidence: Cell | None = None) -> None:
        """Grade the model against the scent they broadcast (and any ML fix-up)."""
        if evidence is not None:
            self.hits.append(tuple(evidence) == tuple(self.pred))
        elif scent:
            peak = max(scent.values())
            here = scent.get(self.pred, 0.0)
            self.hits.append(peak <= 0.0 or here >= PEAK_TOLERANCE * peak)
        self.ring_hits.append(ring_of(self.pred, self.size) == 1)
        del self.hits[:-WINDOW]
        del self.ring_hits[:-WINDOW]

    @property
    def confidence(self) -> float:
        """Share of the recent window in which the model matched the broadcast scent."""
        if not self.hits:
            return 1.0  # nothing contradicts the model yet; the signed start is known
        return sum(self.hits) / len(self.hits)

    @property
    def on_ring(self) -> bool:
        """True once the modelled Thief has settled onto the ring-1 attractor."""
        return bool(self.ring_hits) and all(self.ring_hits[-3:]) and len(self.ring_hits) >= 3
