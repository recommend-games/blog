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
from elo.p_deterministic import elo_probability, update_elo_scores_p_deterministic

jupyter_black.load()

# %%
seed = 13
rng = np.random.default_rng(seed)
num_players = 1000
num_games = 100_000_000
p_deterministic = 0.5
elo_scale = 400
elo_k = 32

# %%
elo_scores = np.zeros(num_players)
elo_scores.shape, elo_scores.dtype

# %%
elo_scores = update_elo_scores_p_deterministic(
    rng=rng,
    elo_scores=elo_scores,
    num_games=num_games,
    p_deterministic=p_deterministic,
    elo_k=elo_k,
    elo_scale=elo_scale,
    inplace=True,
    progress_bar=True,
)
elo_scores.shape, elo_scores.dtype

# %% jp-MarkdownHeadingCollapsed=true
with pl.Config(tbl_rows=100):
    display(pl.Series(elo_scores).describe([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
p_std = elo_probability(diff=np.std(elo_scores), scale=elo_scale)
p_std

# %%
quart = np.quantile(elo_scores, [0.25, 0.75])
iqr = quart[1] - quart[0]
p_iqr = elo_probability(diff=iqr, scale=elo_scale)
p_iqr

# %%
sns.kdeplot(elo_scores)
