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

# %%
import jupyter_black
import polars as pl

jupyter_black.load()

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
games = pl.read_ndjson("results/games.jl", schema=schema)
games.shape

# %%
games.describe()

# %%
games.sample(10, seed=13)

# %%
games.sort("games_played", descending=True).head(10)

# %%
games.sort("weight", descending=True).head(10)
