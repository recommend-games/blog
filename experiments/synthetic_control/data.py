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
from pathlib import Path

import polars as pl
from tqdm import tqdm

try:
    import jupyter_black
    jupyter_black.load()
except:
    pass

# %%
rankings_dir = Path().resolve().parent.parent.parent / "bgg-ranking-historicals"
rankings_dir

# %%
files = list(rankings_dir.glob("*.csv"))
dfs = (
    pl.scan_csv(f).select(
        pl.col("ID").alias("bgg_id"),
        pl.col("Users rated").alias("num_ratings"),
        pl.lit(f.stem[:10]).alias("day"),
    )
    for f in files
)

# %%
pivoted = (
    pl.concat(tqdm(dfs, total=len(files)))
    .collect()
    .pivot(
        values="num_ratings",
        index="day",
        columns="bgg_id",
        aggregate_function="max",
    )
)
pivoted.shape

# %%
pivoted.head(10)

# %%
game_columns = sorted(pivoted.select(pl.exclude("day")).columns, key=int)
df = (
    pivoted.lazy()
    .sort("day")
    .select(
        "day",
        pl.col(*game_columns)
        .interpolate()
        .fill_null(strategy="forward")
        .cast(pl.Int64),
    )
    .collect()
    .write_csv("num_ratings.csv")
)
