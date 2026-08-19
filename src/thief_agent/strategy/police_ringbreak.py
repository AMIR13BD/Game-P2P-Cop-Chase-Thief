"""RingBreakerBrain: a Cop that plays the Orcai-MJ Thief's own decision function.

Their Thief is a deterministic ring runner whose only input is a belief WE feed
(our scent, our declared barriers). ``OrcaiThiefTracker`` therefore reproduces its
cell exactly rather than estimating it, which turns the match from a search problem
into a pursuit problem with perfect information:

* Their k-th move is already fixed when we are asked to move in round k, so being
  orthogonally adjacent to the modelled cell IS a capture -- we step onto it and the
  always-claim declares it (frozen ``PeerHalf`` policy, no protocol change).
* When they walk onto us -- which their heuristic does, because the ring term
  outweighs distance -- STAY captures for the same reason. That is the legal
  exploitation of their own scoring error; no simulator shortcut is involved.
* Otherwise we intercept where they are GOING (one ply through their real rule via
  ``peek``), not where they have been, so we cut the ring instead of trailing it.
* Barriers are spent only when the chase has provably stalled AND the wall strictly
  shrinks their reachable region -- the ring is a 16-cycle, so a single cut turns it
  into a dead-ended arc. Tempo is preserved: nothing is spent while we are closing.

Safety valve: the tracker grades itself against the scent they actually broadcast.
If the opponent is NOT the modelled policy (a repo change, a different team), the
agreement score collapses and every decision defers to ContainBayesBrain, our
general-purpose Cop. The counter can therefore only ever add captures.
"""

from collections import deque

from ..domain.board import Board, Cell
from ..domain.rules import barrier_cell, legal_barrier_targets
from .base import Action, BrainBase, Observation
from .cop_locate import CopLocator
from .corner_model import CornerRunnerTracker
from .graph import distance_map, reachable_area
from .moves import legal_steps, manhattan
from .orcai_track import OrcaiThiefTracker
from .police_contain_bayes import ContainBayesBrain

CONFIDENCE_GATE = 0.6  # below this the model is not describing this opponent
STALL_WINDOW = 6  # rounds of no progress before a wall is considered
BARRIER_RESERVE = 4  # never drop below this many walls on a mere squeeze


class RingBreakerBrain(BrainBase):
    """Opponent-adaptive Cop: exact ring-runner counter, ContainBayes fallback."""

    def __init__(self, rng, horizon: int = 35, seed: int = 0, thief_start: Cell = (3, 3)) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self.seed = seed
        self._start = tuple(thief_start)
        self.fallback = ContainBayesBrain(rng, horizon=horizon, seed=seed, thief_start=thief_start)
        self.tracker: OrcaiThiefTracker | None = None
        self.corner: CornerRunnerTracker | None = None
        self.locator: CopLocator | None = None
        self._gap: deque[int] = deque(maxlen=STALL_WINDOW)
        self.log: list[dict] = []

    # ------------------------------------------------------------------ helpers
    def _note(self, obs: Observation, mode: str, pred: Cell) -> None:
        self.log.append({"step": obs.step, "mode": mode, "pred": pred})

    def _stalled(self) -> bool:
        return len(self._gap) == STALL_WINDOW and min(self._gap) >= self._gap[0]

    def _cut(self, obs: Observation, board: Board, pred: Cell) -> Action | None:
        """Spend one wall only if it strictly shrinks the modelled Thief's region."""
        if obs.max_barriers - obs.barriers_used <= BARRIER_RESERVE:
            return None
        base = reachable_area(board, pred)
        best, best_gain = None, 0
        for target in legal_barrier_targets(obs.self_pos, board):
            cell = barrier_cell(obs.self_pos, target)
            if cell == obs.self_pos or cell == pred:
                continue  # never self-wall; a wall ON them is handled as a capture
            trial = Board(board.size, board.barriers | {cell})
            if not trial.neighbors(obs.self_pos):
                continue  # would seal ourselves in
            gain = base - reachable_area(trial, pred)
            if gain > best_gain:
                best, best_gain = target, gain
        return Action("BARRIER", best) if best is not None else None

    # --------------------------------------------------------------------- api
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        if self.tracker is None:
            self.tracker = OrcaiThiefTracker(obs.board_size, self._start)
            # No start term is assumed: a board-wide prior plus one scent broadcast
            # localises them outright, and no Barrier Law applies to a Thief.
            self.locator = CopLocator(obs.board_size, None, barrier_law=False)
            self.corner = CornerRunnerTracker(obs.board_size)
        evidence = self.locator.update(dict(obs.scent), frozenset(obs.barriers), board)
        pred = self.tracker.advance(obs, board)
        if evidence and pred not in evidence:
            pred = self.tracker.resync(min(evidence))  # the broadcast beats the model
        self.tracker.score(dict(obs.scent), self.locator.best if evidence else None)
        self.corner.observe(pred)  # grade last turn's NEXT-cell bet, not our localisation
        # The fallback keeps its own belief filter, so it is stepped EVERY turn and
        # stays correct the instant we need it.
        fb = self.fallback.decide(obs)
        if self.tracker.confidence < CONFIDENCE_GATE:
            self._note(obs, "fallback", pred)
            return fb

        steps = legal_steps(obs, board)
        # 1. Capture: their move for this round is already made, so any legal step onto
        #    the modelled cell ends it -- including STAY when they walked onto us.
        for direction, cell in steps:
            if cell == pred:
                self._note(obs, "capture", pred)
                return Action("STAY") if direction == "STAY" else Action("MOVE", direction)

        self._gap.append(manhattan(obs.self_pos, pred))
        # 2. Interception: score each candidate against where THEIR rule sends them
        #    once they have seen the scent that candidate would emit.
        moves = [dc for dc in steps if dc[0] != "STAY"] or steps
        far = board.size * board.size

        trust = self.corner.trusted  # a graded model beats an assumed one

        def cost(dc: tuple[str, Cell]) -> tuple[int, int, str]:
            cell = dc[1]
            nxt = (
                self.corner.predict(board.barriers, pred, cell)
                if trust
                else self.tracker.peek(cell, board)
            )
            after = distance_map(board, nxt).get(cell, far)
            now = distance_map(board, pred).get(cell, far)
            return (after, now, dc[0])

        best = min(moves, key=cost)
        # 3. Only when interception is provably not closing do we spend a wall.
        if self._stalled():
            cut = self._cut(obs, board, pred)
            if cut is not None:
                self._gap.clear()
                self._note(obs, "cut", pred)
                walls = board.barriers | {barrier_cell(obs.self_pos, cut.direction)}
                self.corner.commit(self.corner.predict(walls, pred, obs.self_pos))
                return cut
        self._note(obs, "intercept", pred)
        self.corner.commit(self.corner.predict(board.barriers, pred, best[1]))
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "closing the net street by street"
