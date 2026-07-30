"""Normalized belief distribution over opponent cells, from legally visible data."""

from ..domain.board import Board, Cell


class BeliefMap:
    def __init__(self, board: Board) -> None:
        self.board = board
        cells = [c for c in board.all_cells() if c not in board.barriers]
        p = 1.0 / len(cells) if cells else 0.0
        self.dist: dict[Cell, float] = {c: p for c in cells}

    def update(self, scent: dict[Cell, float]) -> None:
        """Weight cells by received scent (+ small floor), zero barriers, renormalize."""
        weights: dict[Cell, float] = {}
        for cell in self.dist:
            if cell in self.board.barriers:
                continue
            weights[cell] = 0.01 + scent.get(cell, 0.0)
        total = sum(weights.values())
        if total <= 0:
            n = len(weights)
            self.dist = {c: 1.0 / n for c in weights} if n else {}
            return
        self.dist = {c: w / total for c, w in weights.items()}

    def argmax(self) -> Cell | None:
        if not self.dist:
            return None
        return max(self.dist, key=self.dist.get)

    def total(self) -> float:
        return sum(self.dist.values())
