"""Plot the title-probability trajectory across the whole tournament, from
outputs/probability_trajectory.csv (see build_probability_trajectory.py).

Writes two charts, each as .svg + .png:

- probability_trajectory: one solid line per tracked team, the model's own
  title-probability estimate over an ordinal snapshot axis.
- probability_edge: one line per tracked team, model minus market title
  probability (percentage points), with a zero line as reference — above
  zero means the model was more bullish than the market, below means the
  market was more bullish than the model.

Both share light vertical dividers marking the pre-tournament / group-stage
/ knockout boundaries.

The x-axis is ordinal (one tick per snapshot), not calendar time: snapshots
are unevenly spaced in real time (six commits in two days pre-tournament,
then a multi-week gap), so calendar spacing would compress the interesting
knockout-stage swings into a sliver of the plot.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from world_cup_2026 import config

PHASE_LABELS = {
    "pre_tournament": "Pre-tournament",
    "group_stage": "Group stage",
    "knockout": "Knockout",
}
DEFAULT_TEAMS = ["ES", "AR", "FR", "EN"]
TEAM_COLORS = {
    "ES": "#e63946",  # Spain
    "AR": "#457b9d",  # Argentina
    "FR": "#8d99ae",  # France — secondary storyline, muted
    "EN": "#2a9d8f",  # England — pre-tournament #4, semifinalist
}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def _save(fig: plt.Figure, name: str, out_dir: Path) -> None:
    # bbox_inches="tight" (not fig.tight_layout()) because the legend lives
    # outside the axes; tight_layout only accounts for in-axes artists and
    # would clip it.
    fig.savefig(out_dir / f"{name}.svg", bbox_inches="tight")
    fig.savefig(out_dir / f"{name}.png", dpi=144, bbox_inches="tight")
    plt.close(fig)


def _snapshot_order(rows: list[dict[str, str]]) -> list[tuple[str, str]]:
    """Unique (phase, commit) pairs in first-seen order (already
    chronological: build_probability_trajectory.py writes pre_tournament,
    then group_stage, then knockout, each internally oldest-commit-first).
    """
    seen: list[tuple[str, str]] = []
    seen_set: set[tuple[str, str]] = set()
    for r in rows:
        key = (r["phase"], r["commit"])
        if key not in seen_set:
            seen_set.add(key)
            seen.append(key)
    return seen


def _drop_resolved(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Drop snapshots where the tournament is already fully decided (some
    team's model probability has collapsed to 1.0). Those points are
    confirmations, not forecasts, and their trivial 0%/100% values would
    otherwise flatten the rest of the trajectory against the axis.
    """
    resolved = {
        (r["phase"], r["commit"])
        for r in rows
        if float(r["model_p_winner"]) >= 0.999
    }
    return [r for r in rows if (r["phase"], r["commit"]) not in resolved]


def _by_team(
    rows: list[dict[str, str]], team_ids: list[str], index: dict[tuple[str, str], int]
) -> tuple[dict[str, dict[str, list[float]]], dict[str, str]]:
    by_team: dict[str, dict[str, list[float]]] = {
        tid: {"x": [], "model": [], "market": []} for tid in team_ids
    }
    team_names: dict[str, str] = {}
    for r in rows:
        tid = r["team_id"]
        if tid not in by_team:
            continue
        x = index[(r["phase"], r["commit"])]
        by_team[tid]["x"].append(x)
        by_team[tid]["model"].append(float(r["model_p_winner"]) * 100)
        by_team[tid]["market"].append(float(r["market_p_winner"]) * 100)
        team_names[tid] = r["team_name"]
    return by_team, team_names


def _draw_phase_bounds(
    ax: plt.Axes, snapshots: list[tuple[str, str]], label_y: float
) -> None:
    # Light dividers + labels placed inside the plot near the top, so they
    # don't compete with the title for vertical space.
    bounds: dict[str, list[int]] = {}
    for i, (phase, _commit) in enumerate(snapshots):
        bounds.setdefault(phase, [i, i])[1] = i
    for phase, (start, end) in bounds.items():
        if start > 0:
            ax.axvline(start - 0.5, color="#888", linewidth=0.8, linestyle=":", alpha=0.6)
        ax.text(
            (start + end) / 2, label_y, PHASE_LABELS.get(phase, phase),
            ha="center", va="bottom", fontsize=9, color="#888",
        )


def plot_probability_trajectory(
    rows: list[dict[str, str]],
    out_dir: Path,
    team_ids: list[str],
) -> None:
    rows = _drop_resolved(rows)
    snapshots = _snapshot_order(rows)
    index = {key: i for i, key in enumerate(snapshots)}
    by_team, team_names = _by_team(rows, team_ids, index)

    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    peak = 0.0
    for tid in team_ids:
        data = by_team[tid]
        if not data["x"]:
            continue
        xs, model_ys = zip(*sorted(zip(data["x"], data["model"])))
        # Stop the line once the team is mathematically eliminated (model
        # probability collapses to 0) instead of trailing a flat zero tail.
        if 0.0 in model_ys:
            cut = model_ys.index(0.0)
            xs, model_ys = xs[:cut], model_ys[:cut]
        if not xs:
            continue
        peak = max(peak, max(model_ys))
        color = TEAM_COLORS.get(tid, "#cccccc")
        label = team_names.get(tid, tid)
        ax.plot(xs, model_ys, color=color, linewidth=2.2, label=label)

    _draw_phase_bounds(ax, snapshots, peak * 1.06)
    ax.set_ylim(top=peak * 1.22)

    ax.set_xticks([])
    ax.set_xlabel("Tournament progression →")
    ax.set_ylabel("Title probability (%)")
    ax.set_title("The model's title probability, the whole tournament")
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8, frameon=False)
    _save(fig, "probability_trajectory", out_dir)


def plot_probability_edge(
    rows: list[dict[str, str]],
    out_dir: Path,
    team_ids: list[str],
) -> None:
    rows = _drop_resolved(rows)
    snapshots = _snapshot_order(rows)
    index = {key: i for i, key in enumerate(snapshots)}
    by_team, team_names = _by_team(rows, team_ids, index)

    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    peak = 0.0
    for tid in team_ids:
        data = by_team[tid]
        if not data["x"]:
            continue
        xs, model_ys, market_ys = zip(
            *sorted(zip(data["x"], data["model"], data["market"]))
        )
        # Stop the line once the team is mathematically eliminated instead
        # of trailing a flat tail at -market_p_winner.
        if 0.0 in model_ys:
            cut = model_ys.index(0.0)
            xs, model_ys, market_ys = xs[:cut], model_ys[:cut], market_ys[:cut]
        if not xs:
            continue
        edge_ys = [m - k for m, k in zip(model_ys, market_ys)]
        peak = max(peak, max(abs(y) for y in edge_ys))
        color = TEAM_COLORS.get(tid, "#cccccc")
        label = team_names.get(tid, tid)
        ax.plot(xs, edge_ys, color=color, linewidth=2.2, label=label)

    ax.axhline(0, color="#888", linewidth=1.0)
    _draw_phase_bounds(ax, snapshots, peak * 1.12)
    ax.set_ylim(-peak * 1.3, peak * 1.3)

    ax.set_xticks([])
    ax.set_xlabel("Tournament progression →")
    ax.set_ylabel("Model minus market (pp)")
    ax.set_title("Who was more right: model vs. market")
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8, frameon=False)
    _save(fig, "probability_edge", out_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=config.OUTPUTS / "probability_trajectory.csv",
        type=Path,
        help="Long-format trajectory CSV from build_probability_trajectory.py",
    )
    parser.add_argument(
        "--output-dir",
        default=config.PLOTS,
        type=Path,
        help="Directory to write probability_trajectory.svg/.png into",
    )
    parser.add_argument(
        "--teams",
        default=",".join(DEFAULT_TEAMS),
        help=f"Comma-separated team_ids to plot (default: {','.join(DEFAULT_TEAMS)})",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_style("dark")

    rows = _read(args.input)
    team_ids = [t.strip() for t in args.teams.split(",") if t.strip()]
    plot_probability_trajectory(rows, args.output_dir, team_ids)
    plot_probability_edge(rows, args.output_dir, team_ids)

    print(f"Wrote probability_trajectory.svg/.png and probability_edge.svg/.png to {args.output_dir}")


if __name__ == "__main__":
    main()
