"""Prototype: animate the bracket converging to the predicted average.

The static heatmap bracket is the *last frame* of this. Here we draw individual
simulated brackets one after another over a running-mean heatmap base, so the
picture starts as a noisy flicker and settles into the converged average bracket
as the sample grows. Each frame also flashes the current sample's champion path,
so you can see the "individual draws" texture on top of the accumulating field.

Deliberately a prototype to judge the *motion*:
  * team codes, not flags (per-frame flag blitting is the slow part);
  * GIF via matplotlib's pillow writer (no ffmpeg dependency);
  * a modest sample with a log-ish frame schedule, so early noise and the
    settling are both visible in a short clip.

The real version would use flags, WebM/MP4 (needs ffmpeg) and the exact 10M
occupancy as its final frame. Run:

    uv run python -m world_cup_2026.animate_bracket --conditional
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

from . import config, group_stage, knockout, load_data, qualifiers, simulate
from .bracket_heatmap import (
    BG,
    BOX_H,
    BOX_W,
    COL_W,
    FINAL_MID,
    BracketGeometry,
    SEQ_CMAP,
    _text_color,
)

HIGHLIGHT = "#ffd24a"  # gold edge on the current sample's champion path


def collect_sample_brackets(
    teams: pl.DataFrame,
    results: pl.DataFrame | None,
    n_samples: int,
    seed: int,
) -> list[dict[str, str]]:
    """Return a list of full per-sim brackets: slot_id -> team group_slot."""
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

    rng = np.random.default_rng(seed)
    ga = rng.poisson(lambdas_a, size=(n_samples, len(lambdas_a)))
    gb = rng.poisson(lambdas_b, size=(n_samples, len(lambdas_b)))
    if fixed_mask is not None and fixed_mask.any():
        ga[:, fixed_mask] = fixed_a
        gb[:, fixed_mask] = fixed_b
    ga_l, gb_l = ga.tolist(), gb.tolist()

    samples: list[dict[str, str]] = []
    for k in range(n_samples):
        group_results = group_stage.simulate_group_stage(group_ctx, ga_l[k], gb_l[k])
        r32_resolution, _ = qualifiers.select_qualifiers(
            group_results, third_place_dict, r32_specs, fifa_ranks
        )
        winners = knockout.simulate_knockout(
            r32_resolution, ko_ctx, rng, fixed_winners=fixed_ko
        )
        b: dict[str, str] = {}
        for mid, (sa, sb) in r32_resolution.items():
            b[f"E{mid}a"] = sa
            b[f"E{mid}b"] = sb
        for mid, slot in winners.items():
            b[f"W{mid}"] = slot
        samples.append(b)
    return samples


def _frame_schedule(n: int) -> list[int]:
    """Sample counts to render: dense early (noisy), sparse late (settled)."""
    cps = set(range(1, min(n, 30) + 1))
    cps.update(range(30, min(n, 100) + 1, 5))
    cps.update(range(100, n + 1, 20))
    cps.add(n)
    return sorted(cps)


def build_frames(
    samples: list[dict[str, str]], id_by_slot: dict[str, str]
) -> list[tuple[int, dict[str, tuple[str, float]], dict[str, str]]]:
    """Precompute (k, top-per-slot, current-sample-bracket) for each rendered frame."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    schedule = set(_frame_schedule(len(samples)))
    frames = []
    for i, b in enumerate(samples, start=1):
        for sid, team in b.items():
            counts[sid][team] += 1
        if i in schedule:
            top = {}
            for sid, c in counts.items():
                team, cnt = max(c.items(), key=lambda kv: kv[1])
                top[sid] = (id_by_slot[team], cnt / i)
            frames.append((i, top, b))
    return frames


def render_gif(
    frames,
    geom: BracketGeometry,
    id_by_slot: dict[str, str],
    out_path,
    n_total: int,
    fps: int,
    subtitle: str,
) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 8))
    fig.patch.set_facecolor(BG)

    def xy(col: int, y: float) -> tuple[float, float]:
        return col * COL_W, y

    def slot_xy(kind: str, mid: int, ab: str) -> tuple[float, float]:
        col, y = (
            geom.entrant_pos(mid, ab) if kind == "entrant" else geom.winner_pos(mid)
        )
        return xy(col, y)

    def draw(frame_idx: int) -> None:
        k, top, sample = frames[frame_idx]
        champ = sample[f"W{FINAL_MID}"]
        champ_path = {sid for sid, team in sample.items() if team == champ}

        ax.clear()
        ax.set_facecolor(BG)
        ax.set_xlim(-BOX_W, 5 * COL_W + BOX_W)
        ax.set_ylim(-1, geom.n_rows)
        ax.invert_yaxis()
        ax.axis("off")

        # connectors
        for mid in geom.stage:
            wx, wy = xy(*geom.winner_pos(mid))
            for kind, fmid, ab in geom.feeder_slots(mid):
                fx, fy = slot_xy(kind, fmid, ab)
                midx = (fx + BOX_W / 2 + wx - BOX_W / 2) / 2
                ax.plot(
                    [fx + BOX_W / 2, midx, midx, wx - BOX_W / 2],
                    [fy, fy, wy, wy],
                    color="#777777",
                    linewidth=0.6,
                    zorder=1,
                )

        def box(sid: str, col: int, y: float, hero: bool) -> None:
            team, prob = top.get(sid, ("", 0.0))
            cx, cy = xy(col, y)
            face = SEQ_CMAP(prob)
            on_path = sid in champ_path
            ax.add_patch(
                FancyBboxPatch(
                    (cx - BOX_W / 2, cy - BOX_H / 2),
                    BOX_W,
                    BOX_H,
                    boxstyle="round,pad=0.02,rounding_size=0.12",
                    linewidth=2.2 if on_path else (1.4 if hero else 0.5),
                    edgecolor=HIGHLIGHT if on_path else ("white" if hero else "#cfcfcf"),
                    facecolor=face,
                    alpha=0.35 + 0.65 * prob,
                    zorder=3,
                )
            )
            if prob > 0:
                ax.text(
                    cx,
                    cy,
                    f"{team} {prob * 100:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=9 if hero else 6.5,
                    color=_text_color(face, 0.35 + 0.65 * prob),
                    fontweight="bold" if hero else "normal",
                    zorder=4,
                )

        for mid in geom.leaf_order:
            for ab in ("a", "b"):
                box(f"E{mid}{ab}", *geom.entrant_pos(mid, ab), hero=False)
        for mid in geom.stage:
            box(f"W{mid}", *geom.winner_pos(mid), hero=(mid == FINAL_MID))

        ax.set_title(
            f"{k:,} of {n_total:,} simulated tournaments\n{subtitle}",
            fontsize=12,
            color="white",
            pad=12,
        )

    # Hold the converged final frame for a beat.
    order = list(range(len(frames))) + [len(frames) - 1] * max(1, fps)
    ani = animation.FuncAnimation(fig, draw, frames=order, interval=1000 // fps)
    ani.save(out_path, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditional", action="store_true")
    parser.add_argument("--n-samples", type=int, default=300)
    parser.add_argument("--fps", type=int, default=7)
    args = parser.parse_args()

    plot_dir = config.PLOTS_CONDITIONAL if args.conditional else config.PLOTS
    plot_dir.mkdir(parents=True, exist_ok=True)
    teams_csv = config.TEAMS_CONDITIONAL_CSV if args.conditional else config.TEAMS_CSV
    teams = load_data.load_teams(teams_csv)
    results = load_data.load_results() if args.conditional else None
    id_by_slot = {r["group_slot"]: r["team_id"] for r in teams.iter_rows(named=True)}

    samples = collect_sample_brackets(teams, results, args.n_samples, config.SEED)
    frames = build_frames(samples, id_by_slot)
    geom = BracketGeometry(load_data.load_knockout_slots())
    sns.set_style("dark")
    subtitle = (
        "conditional on played results" if args.conditional else "pre-tournament"
    )
    out_path = plot_dir / "bracket_convergence.gif"
    render_gif(
        frames, geom, id_by_slot, out_path, args.n_samples, args.fps, subtitle
    )
    print(f"Wrote {out_path} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
