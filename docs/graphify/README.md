# Graphify knowledge graph — Obsidian vault

This folder **is** an Obsidian vault. Open `docs/graphify/` directly in Obsidian
("Open folder as vault") and the wikilinks and Graph View work immediately — the
`.obsidian/` config is committed alongside the notes.

| File | What it is |
|---|---|
| [`index.md`](index.md) | Entry point — graph summary and the top 40 hubs by degree |
| [`hot.md`](hot.md) | Highest-connectivity nodes, ranked as investigation candidates |
| [`architecture.md`](architecture.md) | Nodes per layer and the cross-layer dependency matrix |
| [`reverse-engineering.md`](reverse-engineering.md) | The written analysis derived from the graph |
| `nodes/*.md` | One page per top node — source location, layer, degree, community, neighbours |
| `graph/graph.json` | The full graph (3,231 nodes · 7,385 edges) as produced by Graphify |
| `graph/graph.html` | Graphify's own interactive visualisation — open in any browser |
| `graph/GRAPH_REPORT.md` | Graphify's generated report (communities, extraction stats) |

## How this was produced

Graphify was run against a **pristine clone of the committed tree** at the tagged
submission commit, not against the working directory. That keeps the graph free of local
scratch files (`runs/`, `bench/`, rehearsal output) and makes it exactly reproducible:

```bash
uv tool install graphifyy                     # provides the `graphify` CLI (v0.9.45 used here)

git clone --branch master <this-repo> /tmp/graph-src
cd /tmp/graph-src && rm -rf .git
graphify update . --force                     # AST extraction, no LLM, no API key

cd <this-repo>
uv run python scripts/build_graph_vault.py \
    --graph /tmp/graph-src/graphify-out/graph.json \
    --out docs/graphify \
    --repo Game-P2P-Cop-Chase-Thief \
    --commit $(git rev-parse HEAD)
```

`graphify update` performs pure AST extraction — no LLM, no API key, no token cost (see
[`../COST_AUDIT.md`](../COST_AUDIT.md)). The vault pages are rendered from `graph.json` by
[`scripts/build_graph_vault.py`](../../scripts/build_graph_vault.py); every number in them
is computed, none typed in.

The regenerable `graphify-out/cache/` directory (~4 MB of per-file AST caches) is
deliberately **not** committed.

## Reading the graph

Graphify's own guidance applies: hubs are where the architecture concentrates, communities
approximate modules, and a node's degree measures how much of the system depends on it —
not how important or how correct it is. Read
[`reverse-engineering.md`](reverse-engineering.md) for what this particular graph shows,
including a section on what it *cannot* show.

## Using Graphify's query commands

The committed `graph/graph.json` can be queried directly:

```bash
graphify explain "BeliefMap"        --graph docs/graphify/graph/graph.json
graphify path    "PeerHalf" "Board" --graph docs/graphify/graph/graph.json
```

Both were run against the committed graph. `explain "BeliefMap"` reports degree 79 in
community *BeliefMap*; `path "PeerHalf" "Board"` returns a 2-hop path
(`PeerHalf --method--> .__init__() --calls--> Board`). Reversing that query —
`path "Board" "PeerHalf"` — returns **no directed path**, which is the layering result of
[`reverse-engineering.md`](reverse-engineering.md) §4 restated as a query: `domain` never
reaches upward into `peer`.

## Screenshots

### Captured automatically (real, not mock-ups)

![Graphify knowledge graph](graph-visualisation.png)

`graph-visualisation.png` is a headless-Chrome capture of the committed
[`graph/graph.html`](graph/graph.html) — Graphify's own interactive rendering of this
repository's graph. The node/edge/community counts in the footer and the community
sidebar are the live values from `graph.json`. Reproduce with:

```bash
chrome --headless=new --disable-gpu --hide-scrollbars \
       --window-size=1600,1000 --virtual-time-budget=25000 \
       --screenshot=docs/graphify/graph-visualisation.png \
       file:///<abs-path>/docs/graphify/graph/graph.html
```

### Captured in Obsidian (manual — Graph View cannot be driven headlessly)

The vault was opened in Obsidian and the three views below captured by hand. Together with
the automatic capture above they are the visual evidence that the graph is browsable, not
just a JSON file.

**Vault index** — `index.md` rendered in Obsidian, showing the repository, the commit the
graph was built from, the node/link/community counts and the hub table with working
`[[nodes/...]]` wikilinks:

![Obsidian — vault index](obsidian-index.png)

**Investigation list** — `hot.md`, the highest-connectivity nodes ranked by degree:

![Obsidian — hot list](obsidian-hot.png)

**Obsidian Graph View** — the vault's own link graph. The three navigation hubs
(`index`, `hot`, `architecture`) sit at the centre because every node page links back to
them; the surrounding ring is the per-node documentation, each labelled with its source
module:

![Obsidian — graph view](obsidian-graph-view.png)

To reproduce: open `<this-repo>/docs/graphify` in Obsidian via *Open folder as vault* (the
committed `.obsidian/` config loads automatically), open `index.md` or `hot.md`, and use
the Graph View ribbon icon — or `Ctrl/Cmd-P` → *"Open graph view"*.

## Freshness

The graph is a snapshot of the commit named in [`index.md`](index.md). After any code
change, re-run the two commands above; `graphify update` costs nothing to run.
