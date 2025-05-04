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

# %%
import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from elo.optimal_k import approximate_optimal_k
from elo.p_deterministic import simulate_p_deterministic_matches, update_elo_ratings_p_deterministic
from elo.elo_ratings import elo_probability

jupyter_black.load()

# %%
seed = 13
rng = np.random.default_rng(seed)
num_players = 1000
num_games = 1_000_000
p_deterministic = 0.5
elo_scale = 400

# %%
player_1_ids, player_2_ids, player_1_outcomes = simulate_p_deterministic_matches(
    rng=rng,
    num_players=num_players,
    num_games=num_games,
    p_deterministic=p_deterministic,
)
elo_k = approximate_optimal_k(
    player_1_ids=player_1_ids,
    player_2_ids=player_2_ids,
    player_1_outcomes=player_1_outcomes,
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
    elo_scale=elo_scale,
)
elo_k

# %%
elo_ratings = np.zeros(num_players)
elo_ratings.shape, elo_ratings.dtype

# %%
elo_scores = update_elo_ratings_p_deterministic(
    rng=rng,
    elo_ratings=elo_ratings,
    num_games=num_games,
    p_deterministic=p_deterministic,
    elo_k=elo_k,
    elo_scale=elo_scale,
    inplace=True,
    progress_bar=True,
)
elo_ratings.shape, elo_ratings.dtype

# %% jp-MarkdownHeadingCollapsed=true
with pl.Config(tbl_rows=100):
    display(pl.Series(elo_ratings).describe([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
p_std = elo_probability(diff=np.std(elo_ratings), scale=elo_scale)
p_std

# %%
quart = np.quantile(elo_ratings, [0.25, 0.75])
iqr = quart[1] - quart[0]
p_iqr = elo_probability(diff=iqr, scale=elo_scale)
p_iqr

# %%
sns.kdeplot(elo_ratings)
