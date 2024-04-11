# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import datetime
from pathlib import Path
import jupyter_black
import polars as pl
from gini.data import scan_all_rankings

jupyter_black.load()

# %%
rankings_dir = Path("../../../bgg-ranking-historicals").resolve()
rankings_dir

# %%
dfs = scan_all_rankings(rankings_dir)
all_rankings = pl.concat(dfs, how="vertical", parallel=True)

# %%
gini = (
    all_rankings.group_by_dynamic("date", every="1d", by="bgg_id")
    .agg(pl.col("num_ratings").max())
    .select(pl.col("num_ratings"), pl.col("date").dt.date())
    .select(pl.all().sort_by("num_ratings").over("date"))
    .with_columns(
        pl.col("num_ratings").rank(method="ordinal").over("date").alias("rank"),
        pl.col("num_ratings").cum_sum().over("date").alias("cum_num_ratings"),
        pl.col("num_ratings").sum().over("date").alias("total_ratings"),
        pl.len().over("date").alias("num_games"),
    )
    .with_columns(
        (pl.col("cum_num_ratings") / pl.col("total_ratings")).alias("share_ratings"),
        (pl.col("rank") / pl.col("num_games")).alias("equal_share"),
    )
    .with_columns((pl.col("equal_share") - pl.col("share_ratings")).alias("diff"))
    .group_by(pl.col("date"))
    .agg((2 * pl.col("diff").mean()).alias("gini"))
    .sort(pl.col("date"))
    .collect()
)

gini.shape

# %%
gini.head()

# %%
gini.tail()

# %%
gini.write_csv("gini.csv")
