"""League-interop scent emission (compat, max-merge). Reproduces the real G002 g01 thief
sequence (esp. step 13, the co-location where the opponent missed the capture) and proves
our emitted field's unique peak is the CURRENT thief cell, so a reference-style Cop can
localize us. The spec (additive) emission stays available and unchanged; emitting is
emit-only and never touches strategy. Capture/HOLD behavior is covered elsewhere.
"""

from thief_agent.domain import smell
from thief_agent.domain.board import Board
from thief_agent.interop import DEFAULT_GROUP_ID
from thief_agent.interop.engine import SubEngine
from thief_agent.interop.terms import default_terms

# exact thief move sequence from /mnt/.../log_G002_g01 (1).json (row, col)
SEQ = [
    (4, 3),
    (5, 3),
    (5, 4),
    (5, 5),
    (6, 5),
    (6, 6),
    (5, 6),
    (6, 6),
    (5, 6),
    (6, 6),
    (5, 6),
    (6, 6),
    (5, 6),
    (4, 6),
    (3, 6),
    (2, 6),
    (2, 5),
    (1, 5),
]
RHO = 0.1


def _argmax(grid):
    return max(grid.items(), key=lambda kv: kv[1])


def test_compat_current_cell_is_unique_peak_over_real_sequence():
    b = Board(7)
    field = smell.compat_update({}, (3, 3), b, RHO)  # start-pos init, then per-step emit
    for k, pos in enumerate(SEQ, start=1):
        field = smell.compat_update(field, pos, b, RHO)
        cell, val = _argmax(field)
        assert cell == pos, f"step {k}: emitted peak {cell} != current thief {pos}"
        assert val == 0.9  # centre is 0.9
        others = [v for c, v in field.items() if c != pos]
        assert not others or max(others) < val  # strictly unique peak (no stale plateau)


def test_reference_style_cop_localizes_current_cell_incl_step13():
    """A reference-style Cop that trusts the strongest received scent cell localizes the
    CURRENT thief cell at every step — including step 13, the missed-capture co-location."""
    b = Board(7)
    field = smell.compat_update({}, (3, 3), b, RHO)
    localized = 0
    for k, pos in enumerate(SEQ, start=1):
        field = smell.compat_update(field, pos, b, RHO)
        wire = {f"{r},{c}": v for (r, c), v in field.items()}  # exact wire form
        cop_guess = max(wire.items(), key=lambda kv: kv[1])
        guess = tuple(int(x) for x in cop_guess[0].split(","))
        localized += guess == pos
        if k == 13:
            assert guess == (5, 6) == pos  # step-13 co-location IS now localizable
    assert localized == len(SEQ)  # every turn (vs 0/18 with the old additive emission)


def test_spec_emission_unchanged_and_differs_from_compat():
    b = Board(7)
    for centre in ((3, 3), (5, 6)):
        assert smell.step_update({}, centre, b, RHO) == smell.step_update({}, centre, b, RHO)
    # after oscillation the spec (additive) field plateaus; compat keeps a unique peak
    sf = {}
    cf = {}
    for pos in [(5, 6), (6, 6), (5, 6), (6, 6), (5, 6)]:
        sf = smell.step_update(sf, pos, b, RHO)
        cf = smell.compat_update(cf, pos, b, RHO)
    spec_peaks = [c for c, v in sf.items() if v >= 0.9]
    compat_peaks = [c for c, v in cf.items() if v >= 0.9]
    assert len(spec_peaks) > 1  # additive plateau (the old, un-localizable behaviour)
    assert compat_peaks == [(5, 6)]  # compat: single current-cell peak


def test_subengine_emits_compat_peaked_scent_at_current_state(commit):
    """Current-turn emitted scent corresponds to the current-turn sealed position."""
    eng = SubEngine("thief", default_terms(max_steps=10), DEFAULT_GROUP_ID, commit, 1)
    msg = eng.take_turn()
    peak = max(msg.smell_grid.items(), key=lambda kv: kv[1])
    guess = tuple(int(x) for x in peak[0].split(","))
    assert guess == eng.half.pos  # emitted peak == our true current cell (no stale position)
    assert peak[1] == 0.9
