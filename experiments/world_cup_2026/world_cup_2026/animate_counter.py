"""Prototype: the title-win counter, a bar-chart that converges to the article's
title-probability plot.

Every simulated tournament drops a "vote" into its champion's bar. The bars grow
from zero toward their final lengths (fixed x-axis, "progress bar" fill) and by
the end the chart matches `title_probabilities` in shape. Batches ramp up — tiny
early (noisy ranking, the odd Germany-tops-the-count moment) to large late
(smooth convergence).

Bars are in fixed final-ranking order (a race that reorders rows just reads as
confusing) and labelled with the running probability, not the raw count, so each
bar is a live estimate that converges to the final title prediction.

Separate from and simpler than the freeze bracket; this is the right-hand panel
of the eventual combined piece. Prototype: GIF via pillow (no ffmpeg), champions
drawn from the canonical p_winner (identical in distribution to streaming real
sims, instant).

    uv run python -m world_cup_2026.animate_counter --conditional
"""

from __future__ import annotations

import argparse

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns

from . import config, load_data  # noqa: F401  (load_data kept for parity/future use)
from .build_article_charts import SEQ_CMAP

TOP_N = 15


def _batch_schedule(total: int, frames: int, power: float = 2.0) -> list[int]:
    """Cumulative sim counts per frame: few early (noisy), many late (settled)."""
    ns = [max(1, round(total * (f / frames) ** power)) for f in range(1, frames + 1)]
    ns[-1] = total
    # strictly non-decreasing
    for i in range(1, len(ns)):
        ns[i] = max(ns[i], ns[i - 1])
    return ns


def render_counter_gif(
    names: list[str],
    final_counts: np.ndarray,
    per_frame_counts: list[np.ndarray],
    cum_n: list[int],
    out_path,
    fps: int,
    subtitle: str,
) -> None:
    n_disp = len(names)
    # Fixed x-axis: leader's final count, with headroom (the article chart's look).
    # Bar length is the raw count (so the bars "fill up"); the labels are the
    # running probability, which converges to the final title prediction.
    xmax = final_counts.max() * 1.16
    # Fixed final-ranking order, ascending so the leader sits at the top.
    disp_order = list(np.argsort(final_counts, kind="stable"))
    palette = [SEQ_CMAP(x) for x in np.linspace(0.78, 0.12, n_disp)]
    colour = [palette[r] for r in range(n_disp)][::-1]  # leader (top) darkest

    fig, ax = plt.subplots(figsize=(7.4, 5.6))

    def draw(fi: int) -> None:
        counts = per_frame_counts[fi]
        n = cum_n[fi]
        ypos = list(range(n_disp))
        ax.clear()
        ax.set_facecolor("#f5f5f5")
        ax.barh(ypos, [counts[idx] for idx in disp_order], color=colour)
        ax.set_yticks(ypos)
        ax.set_yticklabels([names[idx] for idx in disp_order], fontsize=9)
        ax.set_xlim(0, xmax)
        ax.tick_params(labelbottom=False)  # raw counts are arbitrary; % labels carry it
        ax.grid(True, axis="x", alpha=0.3)
        ax.set_axisbelow(True)
        for y, idx in zip(ypos, disp_order):
            c = counts[idx]
            if c > 0:
                ax.text(
                    c + xmax * 0.01, y, f"{c / n * 100:.1f}%", va="center", fontsize=8
                )
        ax.set_title(
            f"Title wins after {n:,} simulated tournaments\n{subtitle}",
            fontsize=12,
        )
        fig.tight_layout()

    order_frames = list(range(len(per_frame_counts))) + [len(per_frame_counts) - 1] * fps
    ani = animation.FuncAnimation(fig, draw, frames=order_frames, interval=1000 // fps)
    ani.save(out_path, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditional", action="store_true")
    parser.add_argument("--total", type=int, default=100_000)
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--fps", type=int, default=7)
    args = parser.parse_args()

    in_dir = config.OUTPUTS_CONDITIONAL if args.conditional else config.OUTPUTS
    plot_dir = config.PLOTS_CONDITIONAL if args.conditional else config.PLOTS
    plot_dir.mkdir(parents=True, exist_ok=True)

    tp = pl.read_csv(in_dir / "team_probabilities.csv")
    p = tp["p_winner"].to_numpy().astype(float)
    p = p / p.sum()  # renormalise (rounding / zero-win teams)
    names_all = tp["team_name"].to_list()

    rng = np.random.default_rng(config.SEED)
    stream = rng.choice(len(p), size=args.total, p=p)

    # Display the TOP_N teams by final title probability (the article chart's set).
    disp = list(np.argsort(-p)[:TOP_N])
    names = [names_all[i] for i in disp]

    schedule = _batch_schedule(args.total, args.frames)
    per_frame_counts = []
    for n in schedule:
        c = np.bincount(stream[:n], minlength=len(p))
        per_frame_counts.append(c[disp].astype(float))
    final_counts = per_frame_counts[-1]

    sns.set_style("dark")
    subtitle = "conditional on played results" if args.conditional else "pre-tournament"
    out_path = plot_dir / "title_counter.gif"
    render_counter_gif(
        names, final_counts, per_frame_counts, schedule, out_path, args.fps, subtitle,
    )
    print(f"Wrote {out_path} ({len(schedule)} frames, {args.total:,} sims)")


if __name__ == "__main__":
    main()
