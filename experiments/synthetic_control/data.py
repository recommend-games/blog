# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
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

jupyter_black.load()

# %%
date_format = "%Y-%m-%dT%H-%M-%S"

# %%
rankings_dir = Path().resolve().parent.parent.parent / "bgg-ranking-historicals"
rankings_dir

# %%
dfs = (
    pl.scan_csv(f)
    .select(
        pl.col("ID").cast(str).alias("bgg_id"),
        pl.col("Users rated").alias("num_ratings"),
    )
    .collect()
    .transpose(column_names="bgg_id")
    .select(
        pl.lit(datetime.strptime(f.stem, date_format)).alias("timestamp"),
        pl.all(),
    )
    for f in sorted(rankings_dir.glob("*.csv"))
)

# %%
df = (
    pl.concat(dfs, how="diagonal")
    .lazy()
    .group_by_dynamic("timestamp", every="1d")
    .agg(pl.exclude("timestamp").last())
    .interpolate()
    .select("timestamp", pl.exclude("timestamp"))
    .collect()
)
df.shape

# %%
df.head(10)

# %%
df.write_csv("num_ratings.csv")
