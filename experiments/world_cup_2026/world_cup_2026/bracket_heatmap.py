"""Static "heatmap bracket": the average knockout bracket over many simulations.

The article's other figures are per-team marginals. This one is per-*slot*: for
every position in the knockout bracket (the 32 Round-of-32 entrant slots and the
winner of each of the 31 ties), it shows the distribution over which team lands
there. The result converges to the predicted average bracket -- a probability
field over the tree, not a single filled-in bracket (the per-slot argmax need not
be globally consistent, which is exactly the honest thing to draw).

Two stages, deliberately decoupled so the drawing can be re-tuned without paying
for another Monte Carlo run:

  collect_occupancy()  re-runs the real engine (group_stage -> qualifiers ->
                       knockout, conditional on played results) and counts, per
                       slot, how often each team occupies it. Writes
                       bracket_slot_probabilities.csv.
  render_bracket()     reads that CSV plus the static bracket geometry and draws
                       knockout_bracket.svg/.png.

This is the static still that the planned convergence *animation* is a superset
of: the same per-slot occupancy, accumulated frame by frame.

TODO(flags): slots are labelled with two-letter team codes for now. Swap in flag
PNG assets (e.g. flag-icons) blitted into each box once the layout is signed off.
TODO(layout): single-sided left-to-right cascade for now; a centred/mirrored
bracket (two halves converging on the final) is the prettier "iconic" form.
TODO(exact): occupancy is collected from its own modest run. To make the still
exact at the full 10M, thread a per-slot accumulator through simulate.py instead.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

from . import config, group_stage, knockout, load_data, qualifiers, simulate
from .build_article_charts import SEQ_CMAP

# Bracket columns left -> right: entrants, then the winner of each round.
STAGE_COL = {"R32": 1, "R16": 2, "QF": 3, "SF": 4, "FINAL": 5}
ENTRANT_COL = 0
FINAL_MID = 104


# --------------------------------------------------------------------------- #
# geometry: derive the bracket tree from the static knockout_slots table
# --------------------------------------------------------------------------- #
class BracketGeometry:
    """Positions for every slot, derived purely from knockout_slots.csv."""

    def __init__(self, knockout_slots: pl.DataFrame) -> None:
        self.stage: dict[int, str] = {}
        self.feeders: dict[int, tuple[int, int]] = {}
        self.sources: dict[int, tuple[str, str]] = {}
        for row in knockout_slots.iter_rows(named=True):
            mid, stage = row["match_id"], row["stage"]
            self.stage[mid] = stage
            sa, sb = row["team_a_source"], row["team_b_source"]
            self.sources[mid] = (sa, sb)
            if stage != "R32":
                self.feeders[mid] = (int(sa[1:]), int(sb[1:]))

        # Leaf order (top -> bottom) by DFS from the final; a-source first.
        self.leaf_order: list[int] = self._leaves(FINAL_MID)
        # Entrant rows: each R32 match contributes its a- then b-slot.
        self.row_y: dict[tuple[int, str], float] = {}
        i = 0
        for mid in self.leaf_order:
            for ab in ("a", "b"):
                self.row_y[(mid, ab)] = float(i)
                i += 1
        self.n_rows = i
        self._wy_cache: dict[int, float] = {}

    def _leaves(self, mid: int) -> list[int]:
        if self.stage[mid] == "R32":
            return [mid]
        a, b = self.feeders[mid]
        return self._leaves(a) + self._leaves(b)

    def winner_y(self, mid: int) -> float:
        if mid in self._wy_cache:
            return self._wy_cache[mid]
        if self.stage[mid] == "R32":
            y = (self.row_y[(mid, "a")] + self.row_y[(mid, "b")]) / 2
        else:
            a, b = self.feeders[mid]
            y = (self.winner_y(a) + self.winner_y(b)) / 2
        self._wy_cache[mid] = y
        return y

    def entrant_pos(self, mid: int, ab: str) -> tuple[int, float]:
        return ENTRANT_COL, self.row_y[(mid, ab)]

    def winner_pos(self, mid: int) -> tuple[int, float]:
        return STAGE_COL[self.stage[mid]], self.winner_y(mid)

    def feeder_slots(self, mid: int) -> list[tuple[str, int, str]]:
        """The two slots that feed match ``mid`` (kind, match_id, ab)."""
        if self.stage[mid] == "R32":
            return [("entrant", mid, "a"), ("entrant", mid, "b")]
        a, b = self.feeders[mid]
        return [("winner", a, ""), ("winner", b, "")]


# --------------------------------------------------------------------------- #
# occupancy: count how often each team lands in each slot
# --------------------------------------------------------------------------- #
def collect_occupancy(
    teams: pl.DataFrame,
    results: pl.DataFrame | None,
    n_sims: int,
    seed: int,
    block: int = 20_000,
) -> dict[str, dict[str, int]]:
    """Return slot_id -> {team_slot: count} over ``n_sims`` simulations.

    Mirrors simulate._simulate_chunk's per-sim walk exactly (same conditional
    pinning), but accumulates per-slot occupancy instead of round marginals.
    """
    group_matches = load_data.load_group_matches()
    knockout_slots = load_data.load_knockout_slots()
    third_place_lookup = load_data.load_third_place_lookup()

    group_ctx = group_stage.build_group_contexts(teams, group_matches)
    ko_ctx = knockout.build_knockout_context(knockout_slots, teams)
    third_place_dict, r32_specs = qualifiers.precompute_qualifier_data(
        third_place_lookup, knockout_slots
    )
    fifa_ranks = {
        row["group_slot"]: int(row["fifa_ranking"]) for row in teams.iter_rows(named=True)
    }
    lambdas_a, lambdas_b = simulate._precompute_group_lambdas(
        teams, group_matches, config.HOST_ADVANTAGE
    )
    fixed_mask, fixed_a, fixed_b = simulate._build_fixed_results(group_matches, results)
    fixed_ko = simulate._build_fixed_ko_winners(teams, knockout_slots, results)

    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rng = np.random.default_rng(seed)
    done = 0
    while done < n_sims:
        size = min(block, n_sims - done)
        ga = rng.poisson(lambdas_a, size=(size, len(lambdas_a)))
        gb = rng.poisson(lambdas_b, size=(size, len(lambdas_b)))
        if fixed_mask is not None and fixed_mask.any():
            ga[:, fixed_mask] = fixed_a
            gb[:, fixed_mask] = fixed_b
        ga_l, gb_l = ga.tolist(), gb.tolist()
        for k in range(size):
            group_results = group_stage.simulate_group_stage(group_ctx, ga_l[k], gb_l[k])
            r32_resolution, _ = qualifiers.select_qualifiers(
                group_results, third_place_dict, r32_specs, fifa_ranks
            )
            winners = knockout.simulate_knockout(
                r32_resolution, ko_ctx, rng, fixed_winners=fixed_ko
            )
            for mid, (sa, sb) in r32_resolution.items():
                counts[f"E{mid}a"][sa] += 1
                counts[f"E{mid}b"][sb] += 1
            for mid, slot in winners.items():
                counts[f"W{mid}"][slot] += 1
        done += size
    return counts


def write_slot_probabilities(
    counts: dict[str, dict[str, int]],
    teams: pl.DataFrame,
    n_sims: int,
    out_path: Path,
) -> None:
    name_by_slot = {r["group_slot"]: r["team_name"] for r in teams.iter_rows(named=True)}
    id_by_slot = {r["group_slot"]: r["team_id"] for r in teams.iter_rows(named=True)}
    rows = []
    for slot_id, team_counts in counts.items():
        kind = "winner" if slot_id.startswith("W") else "entrant"
        ab = "" if kind == "winner" else slot_id[-1]
        match_id = int(slot_id[1:-1]) if kind == "entrant" else int(slot_id[1:])
        for team_slot, c in team_counts.items():
            rows.append(
                {
                    "slot_id": slot_id,
                    "kind": kind,
                    "match_id": match_id,
                    "ab": ab,
                    "team_id": id_by_slot[team_slot],
                    "team_name": name_by_slot[team_slot],
                    "prob": c / n_sims,
                    "n_sims": n_sims,
                }
            )
    pl.DataFrame(rows).with_columns(pl.col("prob").round(5)).sort(
        ["match_id", "kind", "ab", "prob"], descending=[False, False, False, True]
    ).write_csv(out_path)


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
COL_W = 2.7   # horizontal spacing between bracket columns
BOX_W = 2.25
BOX_H = 0.78
BG = (0.16, 0.16, 0.18)  # dark canvas so weak slots fade out and strong ones glow


def _text_color(face, alpha: float) -> str:
    """Black or white, by the luminance of the box as composited over BG."""
    r = alpha * face[0] + (1 - alpha) * BG[0]
    g = alpha * face[1] + (1 - alpha) * BG[1]
    b = alpha * face[2] + (1 - alpha) * BG[2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return "#111111" if lum > 0.55 else "#f5f5f5"


def _top_per_slot(slot_df: pl.DataFrame) -> dict[str, tuple[str, float]]:
    top: dict[str, tuple[str, float]] = {}
    for slot_id, sub in slot_df.group_by("slot_id"):
        best = sub.sort("prob", descending=True).row(0, named=True)
        top[slot_id[0]] = (best["team_id"], best["prob"])
    return top


def render_bracket(
    slot_df: pl.DataFrame,
    geom: BracketGeometry,
    out_dir: Path,
    name: str,
    n_sims: int,
    subtitle: str,
) -> None:
    top = _top_per_slot(slot_df)

    fig, ax = plt.subplots(figsize=(15.5, 11))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-BOX_W, 5 * COL_W + BOX_W)
    ax.set_ylim(-1, geom.n_rows)
    ax.invert_yaxis()  # row 0 at the top
    ax.axis("off")

    def xy(col: int, y: float) -> tuple[float, float]:
        return col * COL_W, y

    def draw_slot(slot_id: str, col: int, y: float, hero: bool = False) -> None:
        team, prob = top.get(slot_id, ("", 0.0))
        cx, cy = xy(col, y)
        face = SEQ_CMAP(prob)
        box = FancyBboxPatch(
            (cx - BOX_W / 2, cy - BOX_H / 2),
            BOX_W,
            BOX_H,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.4 if hero else 0.6,
            edgecolor="white" if hero else "#dddddd",
            facecolor=face,
            alpha=0.35 + 0.65 * prob,
            zorder=3,
        )
        ax.add_patch(box)
        if prob > 0:
            ax.text(
                cx,
                cy,
                f"{team}  {prob * 100:.0f}%",
                ha="center",
                va="center",
                fontsize=10 if hero else 7.5,
                color=_text_color(face, 0.35 + 0.65 * prob),
                fontweight="bold" if hero else "normal",
                zorder=4,
            )

    def slot_xy(kind: str, mid: int, ab: str) -> tuple[float, float]:
        if kind == "entrant":
            col, y = geom.entrant_pos(mid, ab)
        else:
            col, y = geom.winner_pos(mid)
        return xy(col, y)

    # connectors first (under the boxes): each match's two feeders -> its winner
    for mid in geom.stage:
        wcol, wy = geom.winner_pos(mid)
        wx, _ = xy(wcol, wy)
        for kind, fmid, ab in geom.feeder_slots(mid):
            fx, fy = slot_xy(kind, fmid, ab)
            midx = (fx + BOX_W / 2 + wx - BOX_W / 2) / 2
            ax.plot(
                [fx + BOX_W / 2, midx, midx, wx - BOX_W / 2],
                [fy, fy, wy, wy],
                color="#888888",
                linewidth=0.7,
                zorder=1,
            )

    # entrant column (32 leaf slots)
    for mid in geom.leaf_order:
        for ab in ("a", "b"):
            col, y = geom.entrant_pos(mid, ab)
            draw_slot(f"E{mid}{ab}", col, y)
    # winner slots for every tie
    for mid in geom.stage:
        col, y = geom.winner_pos(mid)
        draw_slot(f"W{mid}", col, y, hero=(mid == FINAL_MID))

    # column headers
    headers = ["Round of 32", "Round of 16", "Quarter-finals", "Semi-finals", "Final", "Champion"]
    for col, label in enumerate(headers):
        ax.text(
            col * COL_W,
            -0.7,
            label,
            ha="center",
            va="center",
            fontsize=10,
            color="#cccccc",
            fontweight="bold",
        )

    ax.set_title(
        f"The average knockout bracket over {n_sims:,} simulations\n{subtitle}",
        fontsize=13,
        color="white",
        pad=18,
    )
    fig.tight_layout()
    fig.savefig(out_dir / f"{name}.svg")
    fig.savefig(out_dir / f"{name}.png", dpi=144)
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditional",
        action="store_true",
        help="Condition on played results; read teams_conditional + results, "
        "write into outputs/conditional and plots/conditional.",
    )
    parser.add_argument(
        "--n-sims",
        type=int,
        default=200_000,
        help="Simulations for the occupancy estimate (default 200k; enough for "
        "a stable still without the cost of the full 10M run).",
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Skip the Monte Carlo and re-render from the existing slot CSV.",
    )
    args = parser.parse_args()

    out_dir = config.OUTPUTS_CONDITIONAL if args.conditional else config.OUTPUTS
    plot_dir = config.PLOTS_CONDITIONAL if args.conditional else config.PLOTS
    plot_dir.mkdir(parents=True, exist_ok=True)
    slot_csv = out_dir / "bracket_slot_probabilities.csv"

    teams_csv = config.TEAMS_CONDITIONAL_CSV if args.conditional else config.TEAMS_CSV
    teams = load_data.load_teams(teams_csv)

    if not args.render_only:
        results = load_data.load_results() if args.conditional else None
        counts = collect_occupancy(teams, results, args.n_sims, config.SEED)
        write_slot_probabilities(counts, teams, args.n_sims, slot_csv)
        print(f"Wrote {slot_csv}")

    slot_df = pl.read_csv(slot_csv)
    n_sims = int(slot_df["n_sims"][0])  # from the data, so --render-only stays honest
    geom = BracketGeometry(load_data.load_knockout_slots())
    sns.set_style("dark")
    champ = (
        slot_df.filter(pl.col("slot_id") == f"W{FINAL_MID}")
        .sort("prob", descending=True)
        .row(0, named=True)
    )
    subtitle = (
        f"conditional on played results — most likely champion: "
        f"{champ['team_name']} ({champ['prob'] * 100:.0f}%)"
        if args.conditional
        else f"pre-tournament — most likely champion: "
        f"{champ['team_name']} ({champ['prob'] * 100:.0f}%)"
    )
    render_bracket(slot_df, geom, plot_dir, "knockout_bracket", n_sims, subtitle)
    print(f"Wrote bracket to {plot_dir}/knockout_bracket.svg")


if __name__ == "__main__":
    main()
