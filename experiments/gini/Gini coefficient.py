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

jupyter_black.load()

# %%
rankings_dir = Path("../../../bgg-ranking-historicals").resolve()
rankings_dir


# %%
def scan_rankings(path, date_fmt="%Y-%m-%dT%H-%M-%S"):
    pub_date = datetime.strptime(path.stem, date_fmt)
    return (
        pl.scan_csv(path)
        .select(
            pl.col("ID").alias("bgg_id"),
            pl.col("Users rated").alias("num_ratings"),
        )
        .with_columns(pl.lit(pub_date).alias("date"))
    )


# %%
paths = sorted(rankings_dir.glob("*.csv"))
dfs = map(scan_rankings, paths)
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
