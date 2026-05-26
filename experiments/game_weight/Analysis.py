# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Game weight: analysis of complexity deltas
#
# Do reimplementations get rated heavier than their originals on BGG?
# And does the effect grow with time?

# %%
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
from scipy import stats

jupyter_black.load()
pl.Config.set_tbl_rows(30)

# %%
base_dir = Path(".").resolve()
data_dir = base_dir / "data"

pairs = pl.read_csv(data_dir / "reimpl_pairs.csv")
pairs.shape

# %% [markdown]
# ## Headline test: are reimplementations heavier on average?

# %%
delta = pairs["delta"].to_numpy()
t, p = stats.ttest_1samp(delta, 0)
print(f"n         = {len(delta)}")
print(f"mean Δ    = {delta.mean():.4f}")
print(f"median Δ  = {np.median(delta):.4f}")
print(f"t         = {t:.2f}")
print(f"p         = {p:.4f}")

# %% [markdown]
# ## Does the delta scale with the year gap?
#
# If complexity ratings drift upward over time (the baseline for "heavy" shifts),
# we'd expect larger deltas for larger year gaps.

# %%
gap = pairs["year_gap"].to_numpy()
r, p_r = stats.pearsonr(gap, delta)
slope, intercept, *_ = stats.linregress(gap, delta)
print(f"Pearson r = {r:.4f}  (p = {p_r:.4f})")
print(f"Slope     = {slope:.5f} per year")
print(f"Intercept = {intercept:.4f}")

# %% [markdown]
# ## Delta by year-gap bucket

# %%
buckets = [(1, 5), (6, 10), (11, 20), (21, 50), (51, 200)]
rows = []
for lo, hi in buckets:
    sub = pairs.filter(pl.col("year_gap").is_between(lo, hi))
    d = sub["delta"].to_numpy()
    if len(d) > 5:
        t_b, p_b = stats.ttest_1samp(d, 0)
        rows.append(
            {
                "gap": f"{lo}–{hi}yr",
                "n": len(d),
                "mean_delta": round(float(d.mean()), 4),
                "p": round(float(p_b), 4),
            }
        )

pl.DataFrame(rows)

# %% [markdown]
# ## Notable pairs: largest positive delta

# %%
pairs.sort("delta", descending=True).select(
    [
        "orig_name",
        "orig_year",
        "orig_complexity",
        "reimpl_name",
        "reimpl_year",
        "reimpl_complexity",
        "delta",
        "year_gap",
    ]
).head(20)

# %% [markdown]
# ## Notable pairs: largest negative delta (reimpl got lighter)

# %%
pairs.sort("delta").select(
    [
        "orig_name",
        "orig_year",
        "orig_complexity",
        "reimpl_name",
        "reimpl_year",
        "reimpl_complexity",
        "delta",
        "year_gap",
    ]
).head(20)

# %% [markdown]
# ## Ticket examples: Through the Ages and Here I Stand

# %%
spotlight = ["Through the Ages", "Here I Stand"]
for name in spotlight:
    print(f"\n--- {name} ---")
    sub = pairs.filter(
        pl.col("orig_name").str.contains(name) | pl.col("reimpl_name").str.contains(name)
    )
    print(
        sub.select(
            ["orig_name", "orig_year", "orig_complexity", "reimpl_name", "reimpl_year", "reimpl_complexity", "delta"]
        )
    )
