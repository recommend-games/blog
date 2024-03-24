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
# import warnings
from pathlib import Path
import polars as pl
import jupyter_black

# import seaborn as sns
# from matplotlib import pyplot as plt

jupyter_black.load()
# warnings.filterwarnings("ignore")

# %%
rankings_path = Path(
    "../../../bgg-ranking-historicals/2024-03-24T00-43-41.csv"
).resolve()
rankings_path

# %%
gini = (
    pl.scan_csv(rankings_path)
    .select(pl.col("Users rated").alias("num_ratings"))
    .sort("num_ratings")
    .with_columns(
        pl.col("num_ratings").rank(method="ordinal").alias("rank"),
        pl.col("num_ratings").cum_sum().alias("cum_num_ratings"),
        pl.col("num_ratings").sum().alias("total_ratings"),
        pl.len().alias("num_games"),
    )
    .with_columns(
        (pl.col("cum_num_ratings") / pl.col("total_ratings")).alias("share_ratings"),
        (pl.col("rank") / pl.col("num_games")).alias("equal_share"),
    )
    .with_columns((pl.col("equal_share") - pl.col("share_ratings")).alias("diff"))
    .select(2 * pl.col("diff").mean())
    .collect()
    .item()
)
gini
