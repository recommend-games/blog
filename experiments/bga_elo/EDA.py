# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Board Game Arena data

# %%
import jupyter_black
import polars as pl
from datetime import datetime, timezone

jupyter_black.load()

seed = 13

# %% [markdown]
# ## Games

# %%
schema = {
    "id": pl.Int128,
    "name": pl.Utf8,
    "display_name_en": pl.Utf8,
    "status": pl.Utf8,
    "premium": pl.Boolean,
    "locked": pl.Boolean,
    "weight": pl.Int128,
    "priority": pl.Int128,
    "games_played": pl.Int128,
    "published_on": pl.Datetime,
    "average_duration": pl.Int128,
    "bgg_id": pl.Int128,
    "is_ranking_disabled": pl.Boolean,
}

# %%
games = (
    pl.read_ndjson("results/games.jl", schema=schema)
    .with_columns(days_online=pl.lit(datetime.now()) - pl.col("published_on"))
    .with_columns(
        games_per_day=pl.col("games_played") / pl.col("days_online").dt.total_days()
    )
)
games.shape

# %%
with pl.Config(tbl_rows=100):
    display(games.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
games.sample(10, seed=seed)

# %%
games.sort("games_played", descending=True).head(10)

# %%
games.sort("games_per_day", descending=True).head(10)

# %%
games.sort("weight", descending=True).head(10)

# %%
for k, v in games.partition_by("premium", maintain_order=False, as_dict=True).items():
    print("Premium:", *k)
    display(v.describe())

# %% [markdown]
# ## Rankings

# %%
rankings = (
    pl.read_ndjson(
        "results/rankings.jl",
        schema_overrides={
            "id": pl.Int64,
            # "ranking": pl.Float64,
            "nbr_game": pl.Int64,
            "rank_no": pl.Int64,
        },
    )
    .with_columns(pl.col("ranking").cast(pl.Float64))
    .with_columns(elo=pl.col("ranking") - 1300)
)
rankings.shape

# %%
rankings.sample(10, seed=seed)

# %%
with pl.Config(tbl_rows=100):
    display(rankings.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
rankings.group_by("game_id").agg(min_ranking=pl.col("ranking").min()).join(
    games,
    left_on="game_id",
    right_on="id",
).filter(~pl.col("is_ranking_disabled")).sort("min_ranking", descending=True).head(10)
