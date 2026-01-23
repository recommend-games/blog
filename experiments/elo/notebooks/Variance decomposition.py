# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path

from elo.optimal_k import approximate_optimal_k
from elo.elo_ratings import TwoPlayerElo

import polars as pl
import numpy as np

import jupyter_black

jupyter_black.load()


pl.Config.set_tbl_rows(20)
pl.Config.set_tbl_width_chars(120)

# %%
df = pl.read_ipc("../results/arrow/matches/1081.arrow")
df.shape

# %%
# Expectation: you already have df loaded (like in your example).
# If not, load an Arrow/IPC file like:
# df = pl.read_ipc(".../go.arrow")

assert set(df.columns) >= {"num_players", "player_ids", "payoffs"}, df.columns

# Keep only 2-player matches and sanity-check payoffs
df2 = (
    df.filter(pl.col("num_players") == 2)
    .select(
        pl.col("player_ids").list.get(0).cast(pl.Int64).alias("p0"),
        pl.col("player_ids").list.get(1).cast(pl.Int64).alias("p1"),
        pl.col("payoffs").list.get(0).cast(pl.Float64).alias("y0"),
        pl.col("payoffs").list.get(1).cast(pl.Float64).alias("y1"),
    )
    .with_row_index("match_idx")
)

# No ties assumption: each match has one winner (1.0) and one loser (0.0)
# (Relax if needed.)
bad = df2.filter(
    (pl.col("y0") + pl.col("y1") != 1.0)
    | (~pl.col("y0").is_in([0.0, 1.0]))
    | (~pl.col("y1").is_in([0.0, 1.0]))
)
assert bad.is_empty(), bad.head()

df2.head()

# %%
def iter_match_dicts(df2: pl.DataFrame) -> "list[dict[int, float]] | object":
    """
    Generator of matches in the format expected by your Elo code:
    {player_id: payoff, ...} where payoffs sum to 1.0 in the 2p case.
    """
    # Keep it as a generator to avoid big Python lists if you have tons of matches.
    for p0, p1, y0, y1 in df2.select(["p0", "p1", "y0", "y1"]).iter_rows():
        yield {int(p0): float(y0), int(p1): float(y1)}


# %%
# 1) Fit "optimal" Elo K* using your existing code (Rust-backed by default)
#    (Adjust bounds if desired)
elo_scale = 400.0
k_star = float(
    approximate_optimal_k(
        matches=iter_match_dicts(df2),
        two_player_only=True,
        min_elo_k=0.0,
        max_elo_k=elo_scale / 2,
        elo_scale=elo_scale,
        max_iterations=None,
        x_absolute_tol=None,
        python=False,  # set True if you explicitly want the Python optimiser
    )
)
k_star

# %%
def collect_predictions_two_player_no_ties(
    df2: pl.DataFrame,
    *,
    elo_k: float,
    elo_scale: float = 400.0,
    elo_initial: float = 0.0,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """
    Runs sequential 2-player Elo updates, recording pre-match predictions.

    We work in the "higher-rated player perspective" per match:
      y_hi = 1 if the higher-rated player (pre-match) wins, else 0
      p_hi = Elo-implied P(higher-rated wins) given pre-match ratings
    """
    elo = TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale, elo_initial=elo_initial)

    rows: list[dict[str, object]] = []

    for match_idx, p0, p1, y0, y1 in df2.select(
        ["match_idx", "p0", "p1", "y0", "y1"]
    ).iter_rows():
        p0 = int(p0)
        p1 = int(p1)
        y0 = float(y0)
        y1 = float(y1)

        r0 = float(elo.elo_ratings[p0])
        r1 = float(elo.elo_ratings[p1])

        # Expected outcomes for (p0, p1) BEFORE updating
        exp = elo.expected_outcome((p0, p1))
        p0_win = float(exp[0])  # P(p0 wins)

        # Convert to "higher-rated player" view
        if r0 >= r1:
            hi = p0
            lo = p1
            r_hi = r0
            r_lo = r1
            p_hi = p0_win
            y_hi = y0
            diff = r0 - r1
        else:
            hi = p1
            lo = p0
            r_hi = r1
            r_lo = r0
            p_hi = 1.0 - p0_win  # P(p1 wins)
            y_hi = y1
            diff = r1 - r0

        rows.append(
            {
                "match_idx": int(match_idx),
                "p0": p0,
                "p1": p1,
                "y0": y0,
                "y1": y1,
                "hi": hi,
                "lo": lo,
                "r_hi_pre": r_hi,
                "r_lo_pre": r_lo,
                "diff_pre": diff,
                "p_hi": p_hi,
                "y_hi": y_hi,
            }
        )

        # Update Elo using the observed outcome
        elo.update_elo_ratings({p0: y0, p1: y1})

    preds = pl.DataFrame(rows).sort("match_idx")

    ratings_df = pl.DataFrame(
        {"player_id": list(elo.elo_ratings.keys()), "elo_rating": list(elo.elo_ratings.values())}
    )

    return preds, ratings_df


preds, final_ratings = collect_predictions_two_player_no_ties(
    df2,
    elo_k=k_star,
    elo_scale=elo_scale,
    elo_initial=0.0,
)

preds.head()

# %%
def variance_decomp_plug_in_binary(preds: pl.DataFrame) -> dict[str, float]:
    """
    Model-implied decomposition for binary outcomes using:
      luck  = E[p(1-p)]
      skill = Var(p)
      total = Var(y)
    where y and p are for the higher-rated player.

    This matches the clean total-variance identity if p is the true conditional mean.
    In practice, 'total - (skill + luck)' diagnoses miscalibration / model error.
    """
    y = preds["y_hi"]
    p = preds["p_hi"]

    var_total = float(y.var(ddof=0))
    var_skill = float(p.var(ddof=0))
    var_luck = float((p * (1.0 - p)).mean())

    return {
        "var_total": var_total,
        "var_skill": var_skill,
        "var_luck": var_luck,
        "frac_skill": var_skill / var_total if var_total > 0 else 0.0,
        "frac_luck": var_luck / var_total if var_total > 0 else 0.0,
        "check_total_minus_parts": var_total - (var_skill + var_luck),
    }


plug_in = variance_decomp_plug_in_binary(preds)
plug_in

# %%
def variance_decomp_binned(
    preds: pl.DataFrame,
    *,
    n_bins: int = 30,
) -> dict[str, float]:
    """
    Empirical total-variance decomposition by binning on p_hi.

    This *always* satisfies:
      Var(y) = E[Var(y | bin)] + Var(E[y | bin])
    by construction.

    Interpretation:
      - 'skill' = between-bin variance (resolution of the predictor)
      - 'luck'  = within-bin variance (residual randomness + miscalibration within bins)
    """
    y_col = "y_hi"
    m_col = "p_hi"

    df = preds.select([y_col, m_col])

    # Robust-ish quantile bins. If qcut makes duplicate edges, fall back to rank-binning.
    try:
        dfb = df.with_columns(pl.col(m_col).qcut(n_bins).alias("bin"))
    except Exception:
        # Rank-based equal-count binning
        N = df.height
        dfb = (
            df.with_columns((pl.col(m_col).rank("ordinal") - 1).cast(pl.Int64).alias("_r"))
            .with_columns((pl.col("_r") * n_bins // N).alias("bin"))
            .drop("_r")
        )

    g = (
        dfb.group_by("bin")
        .agg(
            n=pl.len(),
            y_mean=pl.col(y_col).mean(),
            y_var=pl.col(y_col).var(ddof=0),
        )
    )

    N = float(g["n"].sum())
    y_mean = float(df.select(pl.col(y_col).mean()).item())

    var_luck = float((g["n"] * g["y_var"]).sum() / N)
    var_skill = float((g["n"] * (g["y_mean"] - y_mean) ** 2).sum() / N)
    var_total = float(df.select(pl.col(y_col).var(ddof=0)).item())

    return {
        "var_total": var_total,
        "var_skill": var_skill,
        "var_luck": var_luck,
        "frac_skill": var_skill / var_total if var_total > 0 else 0.0,
        "frac_luck": var_luck / var_total if var_total > 0 else 0.0,
        "check_total_minus_parts": var_total - (var_skill + var_luck),
    }


binned = variance_decomp_binned(preds, n_bins=30)
binned

# %%
# Optional: Elo spread (your "skill-o-meter" sigma) on the final ratings,
# optionally restricted to "regular" players by match count.

# match counts per player
match_counts = (
    df2.select(pl.col("p0").alias("player_id"))
    .vstack(df2.select(pl.col("p1").alias("player_id")))
    .group_by("player_id")
    .agg(num_matches=pl.len())
)

players = match_counts.join(final_ratings, on="player_id", how="inner")

threshold = 25  # adjust
sigma_all = float(players.select(pl.col("elo_rating").std(ddof=0)).item())
sigma_regulars = float(
    players.filter(pl.col("num_matches") >= threshold).select(pl.col("elo_rating").std(ddof=0)).item()
)

{"k_star": k_star, "sigma_all": sigma_all, f"sigma_matches>={threshold}": sigma_regulars}

# %%
# Quick one-line summary for your writeup:
summary = {
    "k_star": k_star,
    "plug_in_frac_skill": plug_in["frac_skill"],
    "plug_in_frac_luck": plug_in["frac_luck"],
    "plug_in_check": plug_in["check_total_minus_parts"],
    "binned_frac_skill": binned["frac_skill"],
    "binned_frac_luck": binned["frac_luck"],
    "sigma_all": sigma_all,
    "sigma_regulars": sigma_regulars,
}
summary
