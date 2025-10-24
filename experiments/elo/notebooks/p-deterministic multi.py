# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import numpy as np
from elo.elo_ratings import RankOrderedLogitElo
from elo.optimal_k import approximate_optimal_k

jupyter_black.load()
rng = np.random.default_rng()

# %%
p_deterministic = 0.5
elo_scale = 400
num_players = 1000
num_matches = 100_000
player_per_match = 4
players = np.arange(num_players)

# %%
random_outcomes = np.array(
    [
        rng.choice(
            players,
            size=player_per_match,
            replace=False,
        )
        for _ in range(num_matches)
    ]
)
deterministic_outcomes = np.sort(random_outcomes, axis=1)
mask = rng.random(size=num_matches) < p_deterministic
outcomes = np.where(mask[:, np.newaxis], deterministic_outcomes, random_outcomes)
random_outcomes.shape, deterministic_outcomes.shape, outcomes.shape

# %%
optimal_k = approximate_optimal_k(
    matches=outcomes,
    elo_scale=elo_scale,
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
)
optimal_k

# %%
elo = RankOrderedLogitElo(elo_k=optimal_k, elo_scale=elo_scale)
elo.update_elo_ratings_batch(matches=outcomes, progress_bar=True)

# %%
np.std(tuple(elo.elo_ratings.values()))
