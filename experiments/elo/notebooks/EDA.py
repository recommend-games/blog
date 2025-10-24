# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
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
import seaborn as sns
from datetime import datetime, timezone
from elo.data import load_data

jupyter_black.load()

seed = 13
solitaire_games = [
    "vault",
    "thebrambles",
    "dicepyramid",
    "orchard",
    "grovesolitaire",
    "gammelogic",
]

# %% [markdown]
# ## Games

# %%
games = load_data(
    bgg_games_path="../../../board-game-data/scraped/bgg_GameItem.jl",
    bga_games_path="games.jl",
    bga_rankings_path="rankings.jl",
    exclude_bga_slugs=solitaire_games,
)
games.shape

# %%
games.sample(10, seed=seed)

# %%
with pl.Config(tbl_rows=100):
    display(games.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
games.sort("games_played", descending=True).head(10)

# %%
games.sort("games_per_day", descending=True).head(10)

# %%
games.sort("num_players", descending=True).head(10)

# %%
games.sort("games_per_player", descending=True).head(10)

# %%
games.sort("elo_std", descending=True).head(10)

# %%
games.sort("elo_iqr", descending=True).head(10)

# %% [markdown]
# ## Plots

# %%
# most_played = (
#     games.sort("games_played", descending=True)
#     .head(5)
#     .select("id", "display_name_en")
#     .join(rankings, left_on="id", right_on="game_id", how="inner")
# )

# sns.kdeplot(
#     data=most_played.select("elo", "display_name_en").to_pandas(),
#     x="elo",
#     hue="display_name_en",
# )

# %%
sns.scatterplot(
    data=games.sort("num_players", descending=True)
    .head(250)
    .select("elo_std", "complexity")
    .to_pandas(),
    x="elo_std",
    y="complexity",
)

# %%
sns.scatterplot(
    data=games.sort("num_players", descending=True)
    .head(250)
    .select("elo_iqr", "complexity")
    .to_pandas(),
    x="elo_iqr",
    y="complexity",
)
