"""Local-truth board view + scent overlay (P21).

Renders ONLY the local player's truth: own position (P/T), own known barriers, and
the received opponent scent. It never marks the opponent's true cell -- exactly one
player marker appears, guaranteeing no hidden-position leak."""

MARK = {"police": "P", "thief": "T"}


def _scent_char(v: float) -> str | None:
    if v >= 0.6:
        return "*"
    if v >= 0.3:
        return "+"
    if v > 0:
        return "."
    return None


def _norm_scent(scent) -> dict:
    """Accept {(r,c): v} or {'r,c': v}; return a {(r,c): float} map."""
    out: dict = {}
    for k, v in (scent or {}).items():
        cell = k if isinstance(k, tuple) else tuple(int(x) for x in str(k).split(","))
        out[cell] = v
    return out


def render_board(size: int, self_pos, self_role: str, barriers=(), scent=None) -> str:
    sc = _norm_scent(scent)
    bset = {tuple(b) for b in barriers}
    mark = MARK.get(self_role, "?")
    rows = []
    for r in range(size):
        cells = []
        for c in range(size):
            cell = (r, c)
            if cell == tuple(self_pos):
                ch = mark
            elif cell in bset:
                ch = "#"
            else:
                ch = _scent_char(sc.get(cell, 0.0)) or "·"
            cells.append(ch)
        rows.append(" ".join(cells))
    return "\n".join(rows)


def player_marker_count(board_text: str) -> int:
    """Number of player markers on a rendered local board (must always be 1)."""
    return board_text.count("P") + board_text.count("T")
