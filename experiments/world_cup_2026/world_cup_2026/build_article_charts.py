"""Generate the four figures for the blog article from the simulation outputs.

Reads:
  outputs/team_probabilities.csv
  outputs/group_probabilities.csv
  outputs/market_comparison.csv

Writes (into plots/):
  title_probabilities.svg + .png   horizontal bar of the top 15 by p_winner
  group_qualification_heatmap.svg  12 groups x 4 teams, coloured by p_qualify
  draw_luck.svg                    scatter of elo_rank vs title_probability_rank
  market_vs_model.svg              log-log scatter of model vs Polymarket p_winner

The PNG version of title_probabilities doubles as the post's share image.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

from world_cup_2026.config import OUTPUTS, ROOT

PLOTS = ROOT / "plots"

TEAM_PROBS = OUTPUTS / "team_probabilities.csv"
GROUP_PROBS = OUTPUTS / "group_probabilities.csv"
MARKET_COMPARISON = OUTPUTS / "market_comparison.csv"

# Shared red <-> dark <-> purple diverging cmap for "signed" axes (rank diff,
# model-vs-market edge). The sequential palette is the right (purple) half of
# the same cmap, so all four charts share one colour family on the dark
# seaborn background.
DIV_CMAP = sns.diverging_palette(
    h_neg=15, h_pos=290, s=95, l=60, sep=15, center="dark", as_cmap=True,
)
SEQ_CMAP = LinearSegmentedColormap.from_list(
    # High values map to the deep purple end so the strongest teams glow
    # darkest and the long tail fades into the background.
    "seq_glow", DIV_CMAP(np.linspace(1.0, 0.5, 256)),
)


def _seq_palette(n: int):
    # Skip the darkest end so the lowest-value bar/cell isn't lost in the
    # background; samples run light -> dark to match the cmap direction.
    return [SEQ_CMAP(x) for x in np.linspace(0.05, 0.75, n)]


def _read(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def _save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(PLOTS / f"{name}.svg")
    fig.savefig(PLOTS / f"{name}.png", dpi=144)
    plt.close(fig)


def plot_title_probabilities(rows: list[dict[str, str]], top_n: int = 15) -> None:
    ranked = sorted(rows, key=lambda r: -float(r["p_winner"]))[:top_n]
    names = [r["team_name"] for r in ranked][::-1]
    probs = np.array([float(r["p_winner"]) for r in ranked][::-1])

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    bars = ax.barh(names, probs * 100, color=_seq_palette(len(names)))
    ax.set_xlabel("Title probability (%)")
    ax.set_title(f"Top {top_n} teams by simulated title probability")
    ax.grid(True, axis="x", alpha=0.4)
    ax.set_axisbelow(True)
    for bar, p in zip(bars, probs):
        ax.text(
            bar.get_width() + 0.4,
            bar.get_y() + bar.get_height() / 2,
            f"{p * 100:.1f}%",
            va="center",
            fontsize=9,
        )
    ax.set_xlim(0, max(probs) * 100 * 1.15)
    _save(fig, "title_probabilities")


def plot_group_qualification_heatmap(rows: list[dict[str, str]]) -> None:
    groups = sorted({r["group"] for r in rows})
    grid_p = np.zeros((len(groups), 4))
    grid_labels = [["" for _ in range(4)] for _ in groups]
    for gi, group in enumerate(groups):
        team_rows = [r for r in rows if r["group"] == group]
        team_rows.sort(key=lambda r: -float(r["p_qualify"]))
        for slot, r in enumerate(team_rows):
            p = float(r["p_qualify"])
            grid_p[gi, slot] = p
            grid_labels[gi][slot] = f"{r['team_name']}\n{p * 100:.0f}%"

    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(
        grid_p * 100,
        annot=grid_labels,
        fmt="",
        cmap=SEQ_CMAP,
        vmin=0,
        vmax=100,
        cbar_kws={"label": "P(qualify) (%)"},
        linewidths=0.5,
        linecolor="white",
        annot_kws={"fontsize": 9},
        ax=ax,
    )
    ax.set_yticklabels([f"Group {g}" for g in groups], rotation=0)
    ax.set_xticklabels(["1st", "2nd", "3rd", "4th"])
    ax.set_xlabel("Within-group rank by P(qualify)")
    ax.set_title("Group-stage qualification probability")
    _save(fig, "group_qualification_heatmap")


def plot_draw_luck(rows: list[dict[str, str]], min_wins: int = 100) -> None:
    # Drop teams the simulator essentially never crowned champion: below
    # min_wins their title_probability_rank is shaped by MC noise.
    kept = [
        r
        for r in rows
        if r["title_probability_rank"] != "" and int(r["n_wins"]) >= min_wins
    ]
    kept.sort(key=lambda r: int(r["elo_rank"]))

    elo_ranks = np.array([int(r["elo_rank"]) for r in kept])
    title_ranks = np.array([int(r["title_probability_rank"]) for r in kept])
    names = [r["team_name"] for r in kept]
    diffs = np.array([int(r["rank_difference"]) for r in kept])

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    lim = max(elo_ranks.max(), title_ranks.max()) + 1
    ax.plot([0, lim], [0, lim], color="#999", linestyle="--", linewidth=1, zorder=1)
    cmax = max(abs(int(diffs.min())), abs(int(diffs.max())))
    sc = ax.scatter(
        elo_ranks,
        title_ranks,
        c=diffs,
        cmap=DIV_CMAP,
        vmin=-cmax,
        vmax=cmax,
        s=70,
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )
    movers = [i for i in range(len(diffs)) if diffs[i] != 0]
    for i in movers:
        # Helped teams sit above the diagonal in display; hurt teams below.
        # Anchor each label by the corner pointing into its dot's free
        # quadrant so the label always extends away from the diagonal.
        if diffs[i] >= 0:
            dx, dy, ha, va = -6, 6, "right", "bottom"
        else:
            dx, dy, ha, va = 6, -6, "left", "top"
        ax.annotate(
            names[i],
            (elo_ranks[i], title_ranks[i]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8,
            ha=ha,
            va=va,
        )

    ax.set_xlim(lim, 0)
    ax.set_ylim(lim, 0)
    ax.set_xlabel("Rank by Elo")
    ax.set_ylabel("Rank by simulated title probability")
    ax.set_title("Did the draw help? Elo rank vs simulation rank")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Rank difference\n(positive = helped by draw)")
    ax.grid(True, alpha=0.4)
    ax.set_axisbelow(True)
    _save(fig, "draw_luck")


def plot_market_vs_model(
    rows: list[dict[str, str]], min_p: float = 0.01
) -> None:
    model_p = np.array([float(r["model_p_winner"]) for r in rows])
    market_p = np.array([float(r["market_p_winner"]) for r in rows])
    names = [r["team_name"] for r in rows]
    edges = model_p - market_p

    # Require both sides to price the team as a >=1% contender; otherwise the
    # mid-cluster (teams the market gives 1-2% but the model gives <1%) drowns
    # out the real signal among the top contenders.
    keep = (model_p >= min_p) & (market_p >= min_p)
    model_p_k = model_p[keep] * 100
    market_p_k = market_p[keep] * 100
    names_k = [n for n, k in zip(names, keep) if k]
    edges_k = edges[keep] * 100

    fig, ax = plt.subplots(figsize=(7.5, 6))
    lo = min(market_p_k.min(), model_p_k.min()) * 0.7
    hi = max(market_p_k.max(), model_p_k.max()) * 1.3
    ax.plot(
        [lo, hi], [lo, hi],
        color="#999", linestyle="--", linewidth=1,
        label="Model = Market", zorder=1,
    )

    cmax = max(abs(edges_k.min()), abs(edges_k.max()))
    sc = ax.scatter(
        market_p_k, model_p_k,
        c=edges_k, cmap=DIV_CMAP, vmin=-cmax, vmax=cmax,
        s=80, zorder=3,
    )

    # Label every kept team; anchor labels off the diagonal so they extend
    # into the dot's free quadrant.
    for i in range(len(names_k)):
        if edges_k[i] >= 0:
            dx, dy, ha, va = -6, 6, "right", "bottom"
        else:
            dx, dy, ha, va = 6, -6, "left", "top"
        ax.annotate(
            names_k[i],
            (market_p_k[i], model_p_k[i]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8,
            ha=ha,
            va=va,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("Polymarket implied probability (%, log scale)")
    ax.set_ylabel("Model probability (%, log scale)")
    ax.set_title("Where the model and the market disagree")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Edge (pp)\nmodel − market")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right")
    _save(fig, "market_vs_model")


def main() -> None:
    PLOTS.mkdir(exist_ok=True)
    sns.set_style("dark")

    team_probs = _read(TEAM_PROBS)
    group_probs = _read(GROUP_PROBS)
    market = _read(MARKET_COMPARISON)

    plot_title_probabilities(team_probs)
    plot_group_qualification_heatmap(group_probs)
    plot_draw_luck(team_probs)
    plot_market_vs_model(market)

    print(f"Wrote charts to {PLOTS}")


if __name__ == "__main__":
    main()
