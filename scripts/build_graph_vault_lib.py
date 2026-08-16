#!/usr/bin/env python3
"""Graph analysis helpers for the Obsidian knowledge-graph vault.

Graphify produces the graph; this turns it into the browsable vault used for reverse
engineering — `index.md`, `hot.md`, `architecture.md` and one page per top node, all
cross-linked with Obsidian wikilinks. Every figure is computed from the graph; nothing is
hand-written here.

    graphify update . --force                       # produce graphify-out/graph.json
    uv run python scripts/build_graph_vault.py      # turn it into docs/graphify/
"""

import collections
import re

TOP_NODES = 40
LAYER_RE = re.compile(r"^src/[a-z_]+/([a-z_]+)/")


def layer_of(node: dict) -> str:
    """Architectural layer a node belongs to, from its source path."""
    path = (node or {}).get("source_file") or ""
    match = LAYER_RE.match(path)
    if match:
        return match.group(1)
    for prefix in ("tests/", "docs/", "scripts/", "config/", "schemas/"):
        if path.startswith(prefix):
            return prefix.rstrip("/")
    return "(package root)" if path.startswith("src/") else "other"


def slug(node_id: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", node_id.lower())[:80]


def analyse(graph: dict) -> dict:
    """Degrees, layer sizes and the cross-layer dependency matrix."""
    by_id = {n["id"]: n for n in graph["nodes"]}
    degree: collections.Counter = collections.Counter()
    neighbours: dict = collections.defaultdict(set)
    cross: collections.Counter = collections.Counter()
    for link in graph["links"]:
        src, dst = link["source"], link["target"]
        degree[src] += 1
        degree[dst] += 1
        neighbours[src].add((dst, link.get("relation", "->")))
        neighbours[dst].add((src, link.get("relation", "<-")))
        a, b = layer_of(by_id.get(src)), layer_of(by_id.get(dst))
        if a != b and "other" not in (a, b):
            cross[(a, b)] += 1
    return {
        "by_id": by_id,
        "degree": degree,
        "neighbours": neighbours,
        "cross": cross,
        "layers": collections.Counter(layer_of(n) for n in graph["nodes"]),
    }
