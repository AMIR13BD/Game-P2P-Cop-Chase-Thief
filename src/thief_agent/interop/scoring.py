"""Sub-game outcomes, points, role alternation, and series aggregation (book ch.3
table 2 / App. F table 17). These values are permanent (not negotiable) and match the
official/reference scoring so two peers' result artifacts agree on the cross-team join.
"""

# (police, thief) points per outcome. Zeroed outcomes sanction BOTH sides.
SCORES: dict = {
    "capture": (20, 5),
    "survival": (5, 10),
    "timeout": (0, 0),
    "technical_loss": (0, 0),
    "tamper_forfeit": (0, 0),
}
ZEROED = frozenset({"timeout", "technical_loss", "tamper_forfeit"})
TIE_SCORE = 2


def score_for(outcome: str, role: str) -> int:
    police, thief = SCORES.get(outcome, (0, 0))
    return police if role == "police" else thief


def role_for(natural: str, sub_game_number: int) -> str:
    """Odd sub-games play the natural role; even ones play the opposite (alternation)."""
    if sub_game_number % 2 == 1:
        return natural
    return "thief" if natural == "police" else "police"


def is_tie_row(outcome: str, a: int, b: int) -> bool:
    return outcome not in ZEROED and a == b


def aggregate(rows: list, ours: str, theirs: str) -> dict:
    """Fold per-sub-game rows into the final_result block (both peers derive the same)."""
    totals = {ours: 0, theirs: 0}
    won = {ours: 0, theirs: 0}
    tokens = {ours: 0, theirs: 0}
    ties = 0
    for row in rows:
        so, st = row["score"][ours], row["score"][theirs]
        totals[ours] += so
        totals[theirs] += st
        per_row = row.get("tokens") or {}
        tokens[ours] += int(per_row.get(ours, 0) or 0)
        tokens[theirs] += int(per_row.get(theirs, 0) or 0)
        if so > st:
            won[ours] += 1
        elif st > so:
            won[theirs] += 1
        elif is_tie_row(row["result"], so, st):
            ties += 1
    series_tie = totals[ours] == totals[theirs]
    awarded = {g: v + TIE_SCORE for g, v in totals.items()} if series_tie else dict(totals)
    return {
        "total_score": awarded,
        "sub_games_won": won,
        "ties": ties,
        "winner_group": None if series_tie else max(totals, key=lambda k: totals[k]),
        "series_tie": series_tie,
        "tie_score_each": TIE_SCORE if series_tie else None,
        # Series total of the per-sub-game consumption (book App. E rule 54: report the tokens
        # consumed in the sub-game AND in the series).
        "tokens_total_series": tokens,
    }
