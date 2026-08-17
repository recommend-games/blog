"""Prototype: the freeze bracket — a single simulated bracket that crystallises
into the predicted average.

Every frame shows a full concrete bracket. Each slot is either:
  * LIVE  — the current sample's actual team for that slot (gold edge); it
            flickers frame to frame, so the champion really does flash up as
            Germany now and then.
  * FROZEN — locked to that slot's modal team from the canonical 10M occupancy
            (calm purple glow, labelled with its probability).

A slot freezes once its true probability clears a threshold tau(t) that falls
from 1.0 to just below the least-certain slot over the run. So the bracket
freezes from the outside in — the near-certain R32 entrants first, the champion
last — and the final frame is exactly the published static bracket. Motion is
just the number of live slots, which only decreases, so it self-calms (no
seizure-flicker by the end).

Prototype: team codes not flags, GIF via pillow (no ffmpeg). Reads the canonical
`bracket_slot_probabilities.csv` written by wc26-simulate. Run:

    uv run python -m world_cup_2026.animate_bracket --conditional
"""

from __future__ import annotations



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
    axes_xy_ratio,
    ensure_flags,
    load_flags,
    place_flag,
)

HIGHLIGHT = "#ffd24a"          # gold edge on live (still-spinning) slots
LIVE_FILL = (0.32, 0.30, 0.36)  # neutral slate for live slots


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


def load_modal(slot_csv) -> tuple[dict[str, str], dict[str, float]]:
    """Per-slot modal team_id and its probability, from the canonical 10M CSV."""
    df = pl.read_csv(slot_csv)
    modal: dict[str, str] = {}
    pmodal: dict[str, float] = {}
    for sid, sub in df.group_by("slot_id"):
        best = sub.sort("prob", descending=True).row(0, named=True)
        modal[sid[0]] = best["team_id"]
        pmodal[sid[0]] = best["prob"]
    return modal, pmodal


def render_freeze_gif(
    samples: list[dict[str, str]],
    modal: dict[str, str],
    pmodal: dict[str, float],
    id_by_slot: dict[str, str],
    flags: dict,
    geom: BracketGeometry,
    out_path,
    fps: int,
    subtitle: str,
) -> None:
    n_frames = len(samples)
    floor = min(pmodal.values()) * 0.97  # so the least-certain slot freezes at the end
    fig, ax = plt.subplots(figsize=(11.5, 8))
    fig.patch.set_facecolor(BG)

    def xy(col: int, y: float) -> tuple[float, float]:
        return col * COL_W, y

    def slot_xy(kind: str, mid: int, ab: str) -> tuple[float, float]:
        col, y = (
            geom.entrant_pos(mid, ab) if kind == "entrant" else geom.winner_pos(mid)
        )
        return xy(col, y)

    def draw(fi: int) -> None:
        t = fi / (n_frames - 1) if n_frames > 1 else 1.0
        threshold = 1.0 - t * (1.0 - floor)
        sample = samples[fi]

        ax.clear()
        ax.set_facecolor(BG)
        ax.set_xlim(-BOX_W, 5 * COL_W + BOX_W)
        ax.set_ylim(-1, geom.n_rows)
        ax.invert_yaxis()
        ax.axis("off")
        xy_ratio = axes_xy_ratio(ax)

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

        live = 0

        def box(sid: str, col: int, y: float, hero: bool) -> None:
            nonlocal live
            cx, cy = xy(col, y)
            p = pmodal.get(sid, 0.0)
            frozen = p >= threshold
            if frozen:  # modal team, calm glow
                team, face, alpha = modal.get(sid, ""), SEQ_CMAP(p), 0.35 + 0.65 * p
                edge, lw = ("white" if hero else "#cfcfcf"), (1.6 if hero else 0.6)
            else:  # current sample's team, gold edge
                live += 1
                team, face, alpha = id_by_slot[sample[sid]], LIVE_FILL, 1.0
                edge, lw = HIGHLIGHT, 1.8
            ax.add_patch(
                FancyBboxPatch(
                    (cx - BOX_W / 2, cy - BOX_H / 2),
                    BOX_W,
                    BOX_H,
                    boxstyle="round,pad=0.02,rounding_size=0.12",
                    linewidth=lw,
                    edgecolor=edge,
                    facecolor=face,
                    alpha=alpha,
                    zorder=3,
                )
            )
            img = flags.get(team)
            flag_h = BOX_H * (0.66 if hero else 0.5)
            tcol = _text_color(face, alpha) if frozen else "#f5f5f5"
            fs, fw = (8 if hero else 6.2), ("bold" if hero else "normal")
            # Flag + code pair tightly on the left; the probability sits apart
            # on the right (frozen only).
            fcx = cx - BOX_W * (0.30 if frozen else 0.16)
            if img is not None:
                w = place_flag(ax, img, fcx, cy, flag_h, xy_ratio, BOX_W * 0.34)
                ax.text(fcx + w / 2 + BOX_W * 0.05, cy, team, ha="left", va="center",
                        fontsize=fs, color=tcol, fontweight=fw, zorder=4)
            else:
                ax.text(cx - BOX_W * (0.2 if frozen else 0.0), cy, team, ha="center",
                        va="center", fontsize=fs, color=tcol, fontweight=fw, zorder=4)
            if frozen:
                ax.text(cx + BOX_W * 0.43, cy, f"{p * 100:.0f}%", ha="right",
                        va="center", fontsize=fs, color=tcol, fontweight=fw, zorder=4)

        for mid in geom.leaf_order:
            for ab in ("a", "b"):
                box(f"E{mid}{ab}", *geom.entrant_pos(mid, ab), hero=False)
        for mid in geom.stage:
            box(f"W{mid}", *geom.winner_pos(mid), hero=(mid == FINAL_MID))

        champ_sid = f"W{FINAL_MID}"
        champ = (
            modal[champ_sid]
            if pmodal.get(champ_sid, 0.0) >= threshold
            else id_by_slot[sample[champ_sid]]
        )
        status = "settled" if live == 0 else f"{live} slots still live"
        ax.set_title(
            f"Simulating the knockouts — {status}\n"
            f"champion: {champ}   ·   {subtitle}",
            fontsize=12,
            color="white",
            pad=12,
        )

    order = list(range(n_frames)) + [n_frames - 1] * max(1, 2 * fps)  # hold the result
    ani = animation.FuncAnimation(fig, draw, frames=order, interval=1000 // fps)
    ani.save(out_path, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)

