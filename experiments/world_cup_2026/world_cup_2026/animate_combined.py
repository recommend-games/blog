"""Prototype: the freeze bracket and the title counter, side by side.

Two views of the same 10M run, animated on one shared timeline:
  * LEFT  — the freeze bracket: a concrete sampled bracket whose slots lock to
            their modal team as a falling threshold sweeps past their 10M
            probability (outside-in, champion last).
  * RIGHT — the title counter: champions pile up into a bar chart that grows
            into the title-probability plot.

By the end the bracket has settled on Argentina-over-Spain and the counter shows
the title distribution — the same result, structure on the left, marginal on the
right. Prototype: team codes + flags, GIF via pillow (no ffmpeg), dark canvas.

    uv run python -m world_cup_2026.animate_combined --conditional
"""

from __future__ import annotations

import argparse

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

from . import config, load_data
from .animate_bracket import LIVE_FILL, collect_sample_brackets, load_modal
from .animate_counter import TOP_N, _batch_schedule
from .bracket_heatmap import (
    BG,
    BOX_H,
    BOX_W,
    COL_W,
    FINAL_MID,
    BracketGeometry,
    SEQ_CMAP,
    _text_color,
    axes_xy_ratio,
    ensure_flags,
    load_flags,
    place_flag,
)

HIGHLIGHT = "#ffd24a"
PANEL = "#242128"  # counter panel, a touch lighter than the bracket canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditional", action="store_true")
    parser.add_argument("--n-frames", type=int, default=150)
    parser.add_argument("--total", type=int, default=100_000)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--format", choices=["webm", "gif"], default="webm")
    args = parser.parse_args()

    out_dir = config.OUTPUTS_CONDITIONAL if args.conditional else config.OUTPUTS
    plot_dir = config.PLOTS_CONDITIONAL if args.conditional else config.PLOTS
    plot_dir.mkdir(parents=True, exist_ok=True)
    slot_csv = out_dir / "bracket_slot_probabilities.csv"
    if not slot_csv.exists():
        cond = " --conditional" if args.conditional else ""
        raise SystemExit(f"{slot_csv} not found. Run `wc26-simulate{cond}` first.")

    teams_csv = config.TEAMS_CONDITIONAL_CSV if args.conditional else config.TEAMS_CSV
    teams = load_data.load_teams(teams_csv)
    results = load_data.load_results() if args.conditional else None
    id_by_slot = {r["group_slot"]: r["team_id"] for r in teams.iter_rows(named=True)}
    team_ids = teams["team_id"].to_list()
    ensure_flags(team_ids)
    flags = load_flags(team_ids)

    # ---- bracket data (one sampled bracket per frame, + 10M modal/probs) ----
    modal, pmodal = load_modal(slot_csv)
    samples = collect_sample_brackets(teams, results, args.n_frames, config.SEED)
    geom = BracketGeometry(load_data.load_knockout_slots())
    floor = min(pmodal.values()) * 0.97

    # ---- counter data (champion stream -> per-frame cumulative counts) ----
    tp = pl.read_csv(out_dir / "team_probabilities.csv")
    p = tp["p_winner"].to_numpy().astype(float)
    p = p / p.sum()
    names_all, tids_all = tp["team_name"].to_list(), tp["team_id"].to_list()
    disp = list(np.argsort(-p)[:TOP_N])
    names = [names_all[i] for i in disp]
    tids_disp = [tids_all[i] for i in disp]
    stream = np.random.default_rng(config.SEED + 1).choice(len(p), size=args.total, p=p)
    schedule = _batch_schedule(args.total, args.n_frames)
    counts_seq = [np.bincount(stream[:n], minlength=len(p))[disp].astype(float) for n in schedule]
    final_counts = counts_seq[-1]
    xmax = final_counts.max() * 1.16
    gap = xmax * 0.012
    flag_h_c = 0.62
    disp_order = list(np.argsort(final_counts, kind="stable"))
    palette = [SEQ_CMAP(x) for x in np.linspace(0.78, 0.12, TOP_N)]
    bar_colour = [palette[r] for r in range(TOP_N)][::-1]

    sns.set_style("dark")
    subtitle = "conditional on played results" if args.conditional else "pre-tournament"
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.8, 1], wspace=0.04)
    axL = fig.add_subplot(gs[0])
    axR = fig.add_subplot(gs[1])
    fig.suptitle(
        f"Ten million simulations — the bracket settles, the title count piles up\n{subtitle}",
        color="white", fontsize=13,
    )

    def xy(col: int, y: float) -> tuple[float, float]:
        return col * COL_W, y

    def slot_xy(kind: str, mid: int, ab: str) -> tuple[float, float]:
        c, y = geom.entrant_pos(mid, ab) if kind == "entrant" else geom.winner_pos(mid)
        return xy(c, y)

    def draw_bracket(fi: int) -> None:
        t = fi / (args.n_frames - 1) if args.n_frames > 1 else 1.0
        threshold = 1.0 - t * (1.0 - floor)
        sample = samples[fi]
        axL.clear()
        axL.set_facecolor(BG)
        axL.set_xlim(-BOX_W, 5 * COL_W + BOX_W)
        axL.set_ylim(-1, geom.n_rows)
        axL.invert_yaxis()
        axL.axis("off")
        xyr = axes_xy_ratio(axL)
        for mid in geom.stage:
            wx, wy = xy(*geom.winner_pos(mid))
            for kind, fmid, ab in geom.feeder_slots(mid):
                fx, fy = slot_xy(kind, fmid, ab)
                mx = (fx + BOX_W / 2 + wx - BOX_W / 2) / 2
                axL.plot([fx + BOX_W / 2, mx, mx, wx - BOX_W / 2], [fy, fy, wy, wy],
                         color="#777777", linewidth=0.6, zorder=1)
        live = 0
        for sid, col, y, hero in _slots(geom):
            p_ = pmodal.get(sid, 0.0)
            frozen = p_ >= threshold
            if frozen:
                team, face, alpha = modal.get(sid, ""), SEQ_CMAP(p_), 0.35 + 0.65 * p_
                edge, lw = ("white" if hero else "#cfcfcf"), (1.6 if hero else 0.6)
            else:
                live += 1
                team, face, alpha = id_by_slot[sample[sid]], LIVE_FILL, 1.0
                edge, lw = HIGHLIGHT, 1.8
            cx, cy = xy(col, y)
            axL.add_patch(FancyBboxPatch(
                (cx - BOX_W / 2, cy - BOX_H / 2), BOX_W, BOX_H,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                linewidth=lw, edgecolor=edge, facecolor=face, alpha=alpha, zorder=3))
            img = flags.get(team)
            flag_h = BOX_H * (0.66 if hero else 0.5)
            tcol = _text_color(face, alpha) if frozen else "#f5f5f5"
            fs, fw = (8 if hero else 6.2), ("bold" if hero else "normal")
            fcx = cx - BOX_W * (0.30 if frozen else 0.16)
            if img is not None:
                w = place_flag(axL, img, fcx, cy, flag_h, xyr, BOX_W * 0.34)
                axL.text(fcx + w / 2 + BOX_W * 0.05, cy, team, ha="left", va="center",
                         fontsize=fs, color=tcol, fontweight=fw, zorder=4)
            else:
                axL.text(cx - BOX_W * (0.2 if frozen else 0.0), cy, team, ha="center",
                         va="center", fontsize=fs, color=tcol, fontweight=fw, zorder=4)
            if frozen:
                axL.text(cx + BOX_W * 0.43, cy, f"{p_ * 100:.0f}%", ha="right",
                         va="center", fontsize=fs, color=tcol, fontweight=fw, zorder=4)
        champ_sid = f"W{FINAL_MID}"
        champ = (modal[champ_sid] if pmodal.get(champ_sid, 0.0) >= threshold
                 else id_by_slot[sample[champ_sid]])
        status = "settled" if live == 0 else f"{live} slots still live"
        axL.set_title(f"The bracket — {status}   ·   champion: {champ}",
                      color="white", fontsize=11)

    def draw_counter(fi: int) -> None:
        counts, n = counts_seq[fi], schedule[fi]
        ypos = list(range(TOP_N))
        axR.clear()
        axR.set_facecolor(PANEL)
        axR.barh(ypos, [counts[i] for i in disp_order], color=bar_colour)
        axR.set_yticks(ypos)
        axR.set_yticklabels([names[i] for i in disp_order], fontsize=8, color="#f0f0f0")
        axR.set_xlim(0, xmax)
        axR.set_ylim(-0.7, TOP_N - 0.3)
        axR.tick_params(labelbottom=False, colors="#f0f0f0")
        for sp in axR.spines.values():
            sp.set_color("#555")
        axR.grid(True, axis="x", alpha=0.25, color="#888")
        axR.set_axisbelow(True)
        xyr = axes_xy_ratio(axR)
        for y, i in zip(ypos, disp_order):
            c = counts[i]  # flags show from the start, at the bar's (possibly zero) tip
            xt, img = c + gap, flags.get(tids_disp[i])
            if img is not None:
                w = flag_h_c * (img.shape[1] / img.shape[0]) * xyr
                place_flag(axR, img, c + gap + w / 2, y, flag_h_c, xyr)
                xt = c + gap + w + gap
            axR.text(xt, y, f"{c / n * 100:.1f}%", va="center", fontsize=7.5,
                     color="#f0f0f0")
        axR.set_title(f"Title count — {n:,} simulated", color="white", fontsize=11)

    def draw(fi: int) -> None:
        draw_bracket(fi)
        draw_counter(fi)

    order = list(range(args.n_frames)) + [args.n_frames - 1] * (2 * args.fps)
    ani = animation.FuncAnimation(fig, draw, frames=order, interval=1000 // args.fps)
    if args.format == "webm":
        # VP9, constant-quality (crf, b:v 0); yuv420p for browser compatibility.
        writer = animation.FFMpegWriter(
            fps=args.fps, codec="libvpx-vp9",
            extra_args=["-b:v", "0", "-crf", "30", "-pix_fmt", "yuv420p",
                        "-row-mt", "1", "-deadline", "good", "-cpu-used", "2"],
        )
        out_path = plot_dir / "bracket_and_counter.webm"
    else:
        writer = animation.PillowWriter(fps=args.fps)
        out_path = plot_dir / "bracket_and_counter.gif"
    ani.save(out_path, writer=writer)
    plt.close(fig)
    print(f"Wrote {out_path} ({args.n_frames} frames @ {args.fps}fps)")


def _slots(geom: BracketGeometry):
    """Yield (slot_id, column, y, hero) for every bracket slot."""
    for mid in geom.leaf_order:
        for ab in ("a", "b"):
            col, y = geom.entrant_pos(mid, ab)
            yield f"E{mid}{ab}", col, y, False
    for mid in geom.stage:
        col, y = geom.winner_pos(mid)
        yield f"W{mid}", col, y, mid == FINAL_MID


if __name__ == "__main__":
    main()
