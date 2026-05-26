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
# # Game weight: reimplementation pairs
#
# Build a dataset of (original, reimplementation) pairs from BGG data and compute
# the complexity delta for each pair.

# %%
from pathlib import Path

import jupyter_black
import polars as pl

jupyter_black.load()

# %%
base_dir = Path(".").resolve()
save_dir = base_dir / "data"
save_dir.mkdir(parents=True, exist_ok=True)
project_dir = base_dir.parent.parent
data_dir = project_dir.parent / "board-game-data" / "scraped"
base_dir, save_dir, data_dir

# %%
games = pl.read_csv(data_dir / "bgg_GameItem.csv", infer_schema_length=0)
games.shape

# %% [markdown]
# ## Build reimplementation pairs
#
# The `implementation` column on BGG records that game B is a reimplementation of
# game A. We explode multi-valued entries into one row per directed pair, then join
# to attach the original game's attributes.

# %%
pairs = (
    games.filter(pl.col("implementation") != "")
    .with_columns(pl.col("implementation").str.split(","))
    .explode("implementation")
    .rename(
        {
            "bgg_id": "reimpl_id",
            "name": "reimpl_name",
            "year": "reimpl_year",
            "complexity": "reimpl_complexity",
            "num_votes": "reimpl_votes",
            "implementation": "orig_id",
        }
    )
    .select(["reimpl_id", "reimpl_name", "reimpl_year", "reimpl_complexity", "reimpl_votes", "orig_id"])
)

orig = games.select(
    [
        pl.col("bgg_id").alias("orig_id"),
        pl.col("name").alias("orig_name"),
        pl.col("year").alias("orig_year"),
        pl.col("complexity").alias("orig_complexity"),
        pl.col("num_votes").alias("orig_votes"),
    ]
)

# %%
all_pairs = (
    pairs.join(orig, on="orig_id", how="inner")
    .with_columns(
        [
            pl.col("reimpl_complexity").cast(pl.Float64, strict=False),
            pl.col("orig_complexity").cast(pl.Float64, strict=False),
            pl.col("reimpl_year").cast(pl.Int32, strict=False),
            pl.col("orig_year").cast(pl.Int32, strict=False),
            pl.col("reimpl_votes").cast(pl.Int32, strict=False),
            pl.col("orig_votes").cast(pl.Int32, strict=False),
        ]
    )
    .drop_nulls()
    .filter(pl.col("reimpl_complexity") > 0, pl.col("orig_complexity") > 0)
    .filter(pl.col("reimpl_year") > pl.col("orig_year"))
    .with_columns(
        [
            (pl.col("reimpl_complexity") - pl.col("orig_complexity")).alias("delta"),
            (pl.col("reimpl_year") - pl.col("orig_year")).alias("year_gap"),
        ]
    )
)

print(f"Total directed pairs (reimpl newer than orig): {len(all_pairs)}")
all_pairs.head(5)

# %% [markdown]
# ## Filter by minimum votes
#
# Complexity ratings with very few votes are noisy (integer values like 1.0, 2.0, 4.0
# from a handful of raters). Require at least 100 votes on each game.

# %%
MIN_VOTES = 100

pairs_filtered = all_pairs.filter(
    (pl.col("reimpl_votes") >= MIN_VOTES) & (pl.col("orig_votes") >= MIN_VOTES)
)

print(f"Pairs after min_votes={MIN_VOTES} filter: {len(pairs_filtered)}")
pairs_filtered.head(10)

# %%
pairs_filtered.write_csv(save_dir / "reimpl_pairs.csv", float_precision=5)
print("Saved to", save_dir / "reimpl_pairs.csv")
