"""Static "heatmap bracket": the average knockout bracket over many simulations.

The article's other figures are per-team marginals. This one is per-*slot*: for
every position in the knockout bracket (the 32 Round-of-32 entrant slots and the
winner of each of the 31 ties), it shows the distribution over which team lands
there. The result converges to the predicted average bracket -- a probability
field over the tree, not a single filled-in bracket (the per-slot argmax need not
be globally consistent, which is exactly the honest thing to draw).

The per-slot occupancy is produced by the canonical run: wc26-simulate
accumulates it alongside everything else and writes bracket_slot_probabilities.csv,
so the bracket is exact at the same N as the rest of the article. This module
just renders that CSV. `--collect` runs a standalone Monte Carlo to (re)generate
the CSV itself, as a fallback or when no full run exists yet.

  render_bracket()     reads bracket_slot_probabilities.csv plus the static
                       bracket geometry and draws knockout_bracket.svg/.png.
  collect_occupancy()  (fallback, via --collect) re-runs the engine to count
                       per-slot occupancy and write the CSV.

This is the static still that the planned convergence *animation* is a superset
of: the same per-slot occupancy, accumulated frame by frame.

Flags are cached PNGs from flagcdn (assets/flags/<team_id>.png), blitted into
each slot with the occupancy percentage; a missing asset falls back to the
two-letter team code.

TODO(layout): single-sided left-to-right cascade for now; a centred/mirrored
bracket (two halves converging on the final) is the prettier "iconic" form.
"""

from __future__ import annotations

import argparse
import urllib.request
from collections import defaultdict
from pathlib import Path

import matplotlib.image as mpimg
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
# flags: cached PNGs from flagcdn, keyed by the data's two-letter team_id
# --------------------------------------------------------------------------- #
FLAG_DIR = config.ROOT / "assets" / "flags"
# team_id is ISO 3166-1 alpha-2 except the UK home nations, which flagcdn
# serves as the gb-* subdivisions.
FLAG_CODE_OVERRIDE = {"EN": "gb-eng", "SQ": "gb-sct"}


def _flag_code(team_id: str) -> str:
    return FLAG_CODE_OVERRIDE.get(team_id, team_id.lower())


def ensure_flags(team_ids: list[str], size: str = "w160") -> None:
    """Download any missing flag PNGs into assets/flags/ (cached; offline after)."""
    FLAG_DIR.mkdir(parents=True, exist_ok=True)
    for tid in team_ids:
        path = FLAG_DIR / f"{tid}.png"
        if path.exists():
            continue
        url = f"https://flagcdn.com/{size}/{_flag_code(tid)}.png"
        req = urllib.request.Request(url, headers={"User-Agent": "wc26-bracket/1.0"})
        with urllib.request.urlopen(req) as resp:
            path.write_bytes(resp.read())
        print(f"  fetched flag {tid} <- {url}")


def load_flags(team_ids: list[str]) -> dict[str, np.ndarray]:
    flags: dict[str, np.ndarray] = {}
    for tid in team_ids:
        path = FLAG_DIR / f"{tid}.png"
        if path.exists():
            flags[tid] = mpimg.imread(path)
    return flags


def axes_xy_ratio(ax) -> float:
    """px-per-y-unit / px-per-x-unit, so flag widths can be aspect-corrected on
    non-equal-aspect axes. Valid once the axes has a size and limits set."""
    o = ax.transData.transform((0, 0))
    sx = abs(ax.transData.transform((1, 0))[0] - o[0])
    sy = abs(ax.transData.transform((0, 1))[1] - o[1])
    return sy / sx


def place_flag(ax, img, cx, cy, h, xy_ratio, max_w=None, zorder=5) -> float:
    """Blit a flag centred at (cx, cy) with data-height h, undistorted. Returns
    the flag's data-width (so callers can position a label after it).

    origin follows the axis orientation so the flag is always upright: "lower"
    for an inverted y-axis (the bracket), "upper" for a normal one (the counter).
    """
    aspect = img.shape[1] / img.shape[0]
    w = h * aspect * xy_ratio
    if max_w is not None and w > max_w:
        w = max_w
        h = w / (aspect * xy_ratio)
    ax.imshow(
        img,
        extent=(cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2),
        aspect="auto",
        origin="lower" if ax.yaxis_inverted() else "upper",
        zorder=zorder,
    )
    return w


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


def _fmt_pct(prob: float) -> str:
    """Percent label that never rounds up to a misleading "100%".

    A slot reads "100%" only when it is *exactly* locked (prob == 1.0). A
    near-certain but still undecided slot — e.g. a third-place pairing that
    lands here in 0.999 of sims because the qualifying-thirds combination
    isn't settled yet — clamps to "99%" rather than rounding up to a 100%
    that overstates the certainty.
    """
    pct = round(prob * 100)
    if pct >= 100 and prob < 1.0:
        pct = 99
    return f"{pct}%"


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
    flags: dict[str, np.ndarray] | None = None,
) -> None:
    top = _top_per_slot(slot_df)
    flags = flags or {}
    slot_jobs: list[tuple[str, float, float, float, bool]] = []  # team, prob, cx, cy, hero

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
        ax.add_patch(
            FancyBboxPatch(
                (cx - BOX_W / 2, cy - BOX_H / 2),
                BOX_W,
                BOX_H,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                linewidth=1.4 if hero else 0.6,
                edgecolor="white" if hero else "#dddddd",
                facecolor=SEQ_CMAP(prob),
                alpha=0.35 + 0.65 * prob,
                zorder=3,
            )
        )
        # Flag + code + probability are placed in a second pass (after layout is
        # final, so the flag's pixel size can be matched to the box height).
        if prob > 0:
            slot_jobs.append((team, prob, cx, cy, hero))

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

    # Flag + label pass: done after the layout is final so the flag's data width
    # can be matched to the box height (the axes are not equal-aspect, so widths
    # need the x/y pixel-scale ratio). Same arrangement as the animation: flag +
    # country code paired on the left, probability on the right.
    fig.tight_layout()
    fig.canvas.draw()
    xy_ratio = axes_xy_ratio(ax)
    for team, prob, cx, cy, hero in slot_jobs:
        face = SEQ_CMAP(prob)
        tcol = _text_color(face, 0.35 + 0.65 * prob)
        fs, fw = (11 if hero else 8.5), ("bold" if hero else "normal")
        flag_h = BOX_H * (0.66 if hero else 0.5)
        img = flags.get(team)
        if img is not None:
            w = place_flag(ax, img, cx - BOX_W * 0.30, cy, flag_h, xy_ratio, BOX_W * 0.34)
            ax.text(cx - BOX_W * 0.30 + w / 2 + BOX_W * 0.05, cy, team, ha="left",
                    va="center", fontsize=fs, color=tcol, fontweight=fw, zorder=4)
            ax.text(cx + BOX_W * 0.43, cy, _fmt_pct(prob), ha="right", va="center",
                    fontsize=fs, color=tcol, fontweight=fw, zorder=4)
        else:  # fallback when a flag asset is missing
            ax.text(cx, cy, f"{team} {_fmt_pct(prob)}", ha="center", va="center",
                    fontsize=fs, color=tcol, fontweight=fw, zorder=4)

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
        "write into outputs/{tag} and plots/{tag}.",
    )
    parser.add_argument(
        "--tag",
        default="conditional",
        metavar="TAG",
        help="Output subdirectory tag for the conditional run (default: 'conditional'). "
             "Use e.g. 'conditional_r32' to preserve earlier conditional outputs.",
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Run a standalone Monte Carlo to (re)generate the slot CSV instead "
        "of reading the canonical one wc26-simulate writes. A fallback/dev path "
        "(e.g. before a full run exists); the full run already writes exact "
        "occupancy at its N.",
    )
    parser.add_argument(
        "--n-sims",
        type=int,
        default=200_000,
        help="Simulations for --collect (default 200k).",
    )
    args = parser.parse_args()

    if args.conditional:
        cpaths = config.conditional_paths(args.tag)
        out_dir = cpaths.outputs
        plot_dir = cpaths.plots
    else:
        out_dir = config.OUTPUTS
        plot_dir = config.PLOTS
    plot_dir.mkdir(parents=True, exist_ok=True)
    slot_csv = out_dir / "bracket_slot_probabilities.csv"

    teams_csv = config.TEAMS_CONDITIONAL_CSV if args.conditional else config.TEAMS_CSV
    teams = load_data.load_teams(teams_csv)

    if args.collect:
        results = load_data.load_results() if args.conditional else None
        counts = collect_occupancy(teams, results, args.n_sims, config.SEED)
        write_slot_probabilities(counts, teams, args.n_sims, slot_csv)
        print(f"Wrote {slot_csv}")
    elif not slot_csv.exists():
        tag_arg = f" --tag {args.tag}" if args.tag != "conditional" else ""
        cond = f" --conditional{tag_arg}" if args.conditional else ""
        raise SystemExit(
            f"{slot_csv} not found. Run `wc26-simulate{cond}` first (it now writes "
            f"the slot occupancy), or pass --collect to generate it here."
        )

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
        f"{champ['team_name']} ({_fmt_pct(champ['prob'])})"
        if args.conditional
        else f"pre-tournament — most likely champion: "
        f"{champ['team_name']} ({_fmt_pct(champ['prob'])})"
    )
    team_ids = teams["team_id"].to_list()
    ensure_flags(team_ids)
    flags = load_flags(team_ids)
    render_bracket(
        slot_df, geom, plot_dir, "knockout_bracket", n_sims, subtitle, flags=flags
    )
    print(f"Wrote bracket to {plot_dir}/knockout_bracket.svg")


if __name__ == "__main__":
    main()
