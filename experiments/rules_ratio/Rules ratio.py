# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import numpy as np
import polars as pl
import statsmodels.api as sm
from pathlib import Path

jupyter_black.load()

pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_rows(100)

seed = 13

# %%
# Additive smoothing
alpha = 0.5
beta = 0.5
# File paths
results_dir = Path("./results").resolve()
data_dir = Path("../../../board-game-data").resolve()
results_dir, data_dir

# %%
forums = (
    pl.scan_ndjson(results_dir / "*.jl")
    .unique("forum_id", keep="any")
    .select("bgg_id", "title", "num_threads")
)
rules_ratios = (
    forums.group_by("bgg_id")
    .agg(
        num_forums=pl.len(),
        num_threads_rules=pl.when(title="Rules").then("num_threads").otherwise(0).sum(),
        num_threads_total=pl.col("num_threads").sum(),
    )
    .remove(pl.col("num_forums") < 10)
    .remove(pl.col("num_threads_total") < 10)
    .with_columns(
        rules_ratio=(pl.col("num_threads_rules") + alpha)
        / (pl.col("num_threads_total") + alpha + beta)
    )
)
games = (
    pl.scan_ndjson(data_dir / "scraped" / "bgg_GameItem.jl", infer_schema_length=10_000)
    .remove(pl.col("compilation"))
    .select("bgg_id", "name", "year", "num_votes", "complexity")
    .remove(pl.col("num_votes") < 100)
    .remove(pl.col("complexity").is_null())
)
rrw = (
    rules_ratios.join(games, on="bgg_id", how="inner")
    .with_columns(rules_ratio_by_weight=pl.col("rules_ratio") / pl.col("complexity"))
    .sort(
        "rules_ratio_by_weight",
        "rules_ratio",
        "num_threads_total",
        descending=[True, True, False],
    )
    .collect()
)
rrw.shape

# %%
forums.group_by("title").agg(pl.len()).sort(
    "len",
    "title",
    descending=[True, False],
).collect()

# %%
rrw.sample(10, seed=seed)

# %%
rrw.describe()

# %%
rrw.head(10)

# %%
rrw.tail(10)

# %%
# Fit Binomial GLM using smoothed proportion with frequency weights
y = rrw["rules_ratio"].to_pandas()
X = sm.add_constant(rrw.select("complexity").to_pandas())
w = rrw["num_votes"].to_pandas() + alpha + beta

model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
print(model.summary())
rr_hat = model.predict(X)

rrw = rrw.with_columns(
    residual_rules_ratio=pl.col("rules_ratio") - pl.Series("rr_hat", rr_hat),
)
rrw.shape

# %%
rrw.sort("residual_rules_ratio", descending=True).head(10)

# %%
rrw.sort("residual_rules_ratio", descending=False).head(10)
