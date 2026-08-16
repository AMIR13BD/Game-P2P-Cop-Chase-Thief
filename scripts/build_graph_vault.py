#!/usr/bin/env python3
"""Build the Obsidian knowledge-graph vault from a Graphify `graph.json`.

Graphify produces the graph; this turns it into the browsable vault used for reverse
engineering - `index.md`, `hot.md`, `architecture.md` and one page per top node, all
cross-linked with Obsidian wikilinks. Every figure is computed from the graph.

    graphify update . --force                       # produce graphify-out/graph.json
    uv run python scripts/build_graph_vault.py --repo <name>
"""

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from build_graph_vault_lib import analyse  # noqa: E402
from graph_vault_pages import (  # noqa: E402
    write_architecture,
    write_hot,
    write_index,
    write_nodes,
)


def main() -> int:
    parser = argparse.ArgumentParser(prog="build_graph_vault")
    parser.add_argument("--graph", default="graphify-out/graph.json")
    parser.add_argument("--out", default="docs/graphify")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", default="unknown")
    args = parser.parse_args()

    graph = json.loads(pathlib.Path(args.graph).read_text(encoding="utf-8"))
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    analysis = analyse(graph)
    write_index(out, graph, analysis, args.repo, args.commit)
    write_hot(out, analysis, args.repo)
    write_architecture(out, analysis, args.repo)
    write_nodes(out, analysis)
    print(f"vault written to {out} ({len(graph['nodes'])} nodes, {len(graph['links'])} links)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
