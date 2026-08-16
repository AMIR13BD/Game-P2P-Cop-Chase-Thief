#!/usr/bin/env python3
"""Render the result charts used in the README and the analysis notebook.

Every figure is drawn from a committed CSV produced by a real run - the paired
scenario benchmark in `evidence/` and the OAT sweeps in `docs/research/`. No value is
typed in here; if a CSV is missing the corresponding figure is skipped loudly.

    uv run python scripts/make_charts.py
"""

import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = pathlib.Path("docs/images")
FG, BG, GRID = "#1b2129", "#ffffff", "#d8dee6"
BLUE, AMBER, RED = "#2f6fb0", "#d99000", "#b03030"


def read(path: str) -> list[dict]:
    file = pathlib.Path(path)
    if not file.exists():
        print(f"  SKIP (missing): {path}")
        return []
    with file.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def style(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, color=FG, fontsize=11, pad=10)
    ax.set_xlabel(xlabel, color=FG, fontsize=9)
    ax.set_ylabel(ylabel, color=FG, fontsize=9)
    ax.tick_params(colors=FG, labelsize=8)
    ax.grid(True, color=GRID, linewidth=0.6, axis="y")
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(GRID)


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote docs/images/{name}")


def chart_matchups() -> None:
    """Paired strategy benchmark: baseline vs candidate, with 95% intervals."""
    rows = read("evidence/scenario_matchups.csv")
    if not rows:
        return
    labels = [r["matchup"].split("_", 1)[1].replace("_", " ") for r in rows]
    rates = [float(r["rate"]) for r in rows]
    lo = [float(r["rate"]) - float(r["ci_lo"]) for r in rows]
    hi = [float(r["ci_hi"]) - float(r["rate"]) for r in rows]
    colours = [BLUE if r["matchup"].startswith("A") else AMBER for r in rows]

    fig, ax = plt.subplots(figsize=(8.4, 4.2), facecolor=BG)
    ax.barh(labels, rates, xerr=[lo, hi], color=colours, height=0.6, error_kw={"ecolor": FG})
    style(ax, "Paired scenario benchmark (600 scenarios//matchup, 95% CI)", "win rate", "")
    ax.set_xlim(0, 1)
    ax.invert_yaxis()
    save(fig, "chart-strategy-benchmark.png")


def chart_oat() -> None:
    """OAT sensitivity: capture rate vs each parameter, one line per opponent."""
    rows = read("docs/research/oat_sensitivity.csv")
    if not rows:
        return
    params = sorted({r["parameter"] for r in rows})
    opponents = sorted({r["opponent"] for r in rows})
    fig, axes = plt.subplots(1, len(params), figsize=(4 * len(params), 3.4), facecolor=BG)
    for ax, param in zip(axes, params, strict=False):
        for idx, opponent in enumerate(opponents):
            pts = [r for r in rows if r["parameter"] == param and r["opponent"] == opponent]
            pts.sort(key=lambda r: float(r["value"]))
            ax.plot(
                [float(p["value"]) for p in pts],
                [float(p["capture_rate"]) for p in pts],
                marker="o",
                linewidth=1.6,
                markersize=4,
                label=opponent,
                alpha=0.9,
                zorder=3 - 0.1 * idx,
            )
        style(ax, param, param, "cop capture rate")
        ax.set_ylim(-0.05, 1.05)
    axes[0].legend(fontsize=7, frameon=False, labelcolor=FG)
    fig.suptitle(
        "OAT parameter sensitivity - local simulation, 200 seeds/point",
        color=FG,
        fontsize=12,
        y=1.06,
    )
    fig.tight_layout()
    save(fig, "chart-oat-sensitivity.png")


def chart_horizon() -> None:
    """Grid x horizon interaction: where the self-play capture rate collapses."""
    rows = read("docs/research/horizon_interaction.csv")
    if not rows:
        return
    grids = sorted({int(r["grid_size"]) for r in rows})
    moves = sorted({int(r["max_moves"]) for r in rows})
    fig, ax = plt.subplots(figsize=(6.2, 3.8), facecolor=BG)
    width = 0.8 / len(moves)
    for idx, move in enumerate(moves):
        vals = [
            next(
                (
                    float(r["capture_rate"])
                    for r in rows
                    if int(r["grid_size"]) == g and int(r["max_moves"]) == move
                ),
                0.0,
            )
            for g in grids
        ]
        xs = [g_i + idx * width - 0.4 + width / 2 for g_i in range(len(grids))]
        ax.bar(xs, vals, width=width, label=f"{move} steps", zorder=3)
    ax.set_xticks(range(len(grids)))
    ax.set_xticklabels([f"{g}x{g}" for g in grids])
    style(ax, "Board size x horizon (self-play, 60 seeds/point)", "board size", "capture rate")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8, frameon=False, labelcolor=FG, title="max_moves", title_fontsize=8)
    save(fig, "chart-horizon-interaction.png")


def main() -> int:
    print("rendering charts from committed CSV data")
    chart_matchups()
    chart_oat()
    chart_horizon()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
