# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
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
from elo.p_deterministic import (
    simulate_p_deterministic_matches,
    update_elo_ratings_p_deterministic,
)
from elo.elo_ratings import RankOrderedLogitElo, TwoPlayerElo, elo_probability

jupyter_black.load()

# %%
seed = 13
rng = np.random.default_rng(seed)
num_players = 1000
num_matches = 1_000_000
players_per_match = 2
p_deterministic = 0.5
elo_scale = 400

# %%
matches = simulate_p_deterministic_matches(
    rng=rng,
    num_players=num_players,
    num_matches=num_matches,
    players_per_match=players_per_match,
    p_deterministic=p_deterministic,
)
matches.shape

# %%
elo_k = approximate_optimal_k(
    matches=matches,
    two_player_only=players_per_match == 2,
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
    elo_scale=elo_scale,
)
elo_k

# %%
elo_kwargs = {"elo_k": elo_k, "elo_scale": elo_scale}
elo = (
    TwoPlayerElo(**elo_kwargs)
    if players_per_match == 2
    else RankOrderedLogitElo(**elo_kwargs)
)
elo = update_elo_ratings_p_deterministic(
    rng=rng,
    elo=elo,
    num_players=num_players,
    num_matches=num_matches,
    players_per_match=players_per_match,
    p_deterministic=p_deterministic,
    progress_bar=True,
)
elo_ratings = np.array(list(elo.elo_ratings.values()))
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
