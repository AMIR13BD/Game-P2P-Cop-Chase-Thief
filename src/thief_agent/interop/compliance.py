"""Fail-closed check that an official ``result_<game_id>.json`` carries every field the book
makes MANDATORY, run before the report is emailed to the lecturer.

Sources (police_thief_p2p.pdf v3.0.0): ch.9 p.78 §9.3.3 "the mandatory signed report" (identity,
GitHub addresses, MCP addresses, hardware declaration, game timestamp, SHA-256 mutual-agreement
approvals) and p.78 ("the mandatory fields include both groups' GitHub links, the commit id of
each sub-game, and the total tokens consumed"); §9.4 + App. E rule 49 (four repository links in
the attached JSON); ch.5.5 box + App. E rule 53 (per-sub-game ``github_commit``); App. E rule 54
(tokens per sub-game and per series); App. E rules 33/34/35/36 (machine-readable JSON, mutual
agreement); App. F table 18 row 1 (a series against one opponent is six sub-games).

Two severities, because rule 35 also punishes NOT reporting:
- ``problems_with`` — blocking. Structure, and every value our own side controls. The report is
  not sent while one of these stands.
- ``warnings_for`` — loud but non-blocking: values only the OPPONENT can supply (its commit, its
  repositories, its MCP/identity data). A peer that declared nothing must not stop us from
  reporting at all; the gap is printed, never silently swallowed, and never filled with a guess.

Only book-mandatory fields are inspected: local or optional extras are never rejected.
"""

from .compliance_spec import (
    GROUP_DETAIL_FIELDS,
    OFFICIAL_SUB_GAMES,
    REQUIRED_AGREEMENT,
    REQUIRED_FINAL,
    REQUIRED_ROW,
    REQUIRED_TOP,
)


def _hex(value, size: int) -> bool:
    text = str(value or "")
    return len(text) == size and all(c in "0123456789abcdefABCDEF" for c in text)


def _own_group(doc: dict, own_group):
    """Our own group id. Our builder always writes ``groups = [ours, theirs]``."""
    groups = doc.get("groups") or []
    return own_group or (groups[0] if groups else None)


def _structure(doc: dict, groups: list, expected: int, problems: list) -> None:
    rows = doc.get("sub_games")
    if not isinstance(rows, list) or len(rows) != expected:
        problems.append(f"sub_games must hold exactly {expected} rows (found {len(rows or [])})")
        return
    for row in rows:
        n = row.get("sub_game_number")
        problems += [f"sub_game {n}: missing '{k}'" for k in REQUIRED_ROW if k not in row]
        for key in ("roles", "score", "tokens", "github_commit", "log_files"):
            block = row.get(key)
            if not isinstance(block, dict) or any(g not in block for g in groups):
                problems.append(f"sub_game {n}: '{key}' must be keyed by both group ids")
    github = (doc.get("links") or {}).get("github")
    if not isinstance(github, dict) or any(g not in github for g in groups):
        problems.append("links.github must carry both groups' repositories (rule 49)")
    details = doc.get("group_details")
    if not isinstance(details, dict) or len(details) != 2:
        problems.append("group_details must describe both groups (§9.3.3)")


def _own_values(doc: dict, ours: str, problems: list) -> None:
    """Everything we ourselves must have filled in — never excusable."""
    for row in doc.get("sub_games") or []:
        n = row.get("sub_game_number")
        if not _hex((row.get("github_commit") or {}).get(ours), 40):
            problems.append(f"sub_game {n}: our own github_commit is not a 40-hex SHA (rule 53)")
        if not isinstance((row.get("tokens") or {}).get(ours), int):
            problems.append(f"sub_game {n}: our own token count is missing (rule 54)")
    repos = ((doc.get("links") or {}).get("github") or {}).get(ours) or {}
    if not repos.get("cop") or not repos.get("thief"):
        problems.append("our own cop+thief repository links are missing (rule 49)")
    for block in (doc.get("group_details") or {}).values():
        if isinstance(block, dict) and block.get("group_id") == ours:
            problems += [
                f"group_details[ours] missing '{k}'"
                for k in GROUP_DETAIL_FIELDS
                if not block.get(k)
            ]


def problems_with(doc, expected_sub_games: int = OFFICIAL_SUB_GAMES, own_group=None) -> list:
    """Blocking problems: structure plus every value our own side owns. Empty == sendable."""
    problems: list = []
    if not isinstance(doc, dict):
        return ["result is not a JSON object (rule 33)"]
    problems += [f"missing top-level '{k}'" for k in REQUIRED_TOP if k not in doc]
    groups = doc.get("groups")
    if not isinstance(groups, list) or len(groups) != 2 or not all(groups):
        return problems + ["groups must name exactly the two group ids"]
    _structure(doc, groups, expected_sub_games, problems)
    final = doc.get("final_result") or {}
    problems += [f"final_result missing '{k}'" for k in REQUIRED_FINAL if k not in final]
    for key in ("total_score", "tokens_total_series"):
        block = final.get(key)
        if not isinstance(block, dict) or any(g not in block for g in groups):
            problems.append(f"final_result.{key} must be keyed by both group ids")
    agreement = doc.get("mutual_agreement") or {}
    problems += [
        f"mutual_agreement missing '{k}'" for k in REQUIRED_AGREEMENT if k not in agreement
    ]
    if not _hex(agreement.get("sha256"), 64):
        problems.append("mutual_agreement.sha256 is not a 64-hex SHA-256 digest")
    if not problems:  # value checks only make sense once the shape is sound
        _own_values(doc, _own_group(doc, own_group), problems)
    return problems


def warnings_for(doc, own_group=None) -> list:
    """Non-blocking gaps the OPPONENT alone could have filled. Report them loudly: they are
    holes in a report that must still be sent (rule 35), and the fix is a peer declaration."""
    if not isinstance(doc, dict) or not isinstance(doc.get("groups"), list):
        return []
    ours = _own_group(doc, own_group)
    peers = [g for g in doc["groups"] if g != ours]
    warnings: list = []
    for peer in peers:
        for row in doc.get("sub_games") or []:
            if not _hex((row.get("github_commit") or {}).get(peer), 40):
                warnings.append(
                    f"sub_game {row.get('sub_game_number')}: '{peer}' declared no 40-hex commit"
                )
        repos = ((doc.get("links") or {}).get("github") or {}).get(peer) or {}
        if not repos.get("cop") or not repos.get("thief"):
            warnings.append(f"'{peer}' declared no cop+thief repository links")
        for block in (doc.get("group_details") or {}).values():
            if isinstance(block, dict) and block.get("group_id") == peer:
                warnings += [
                    f"'{peer}' declared no '{k}'" for k in GROUP_DETAIL_FIELDS if not block.get(k)
                ]
    return warnings


def assert_compliant(doc, expected_sub_games: int = OFFICIAL_SUB_GAMES, own_group=None) -> None:
    """Raise ValueError listing every blocking problem, so an incomplete report is never sent."""
    problems = problems_with(doc, expected_sub_games, own_group)
    if problems:
        raise ValueError("official result is not book-compliant: " + "; ".join(problems))
