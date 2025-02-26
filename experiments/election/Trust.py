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
import numpy as np
from board_game_recommender import LightGamesRecommender
from election.schulze import compute_pairwise_preferences
from election.trust import user_trust

jupyter_black.load()

# %%
trust = user_trust("../../../board-game-data/scraped/bgg_RatingItem.jl", progress=True)

# %%
users, trust_scores = zip(*trust.items())
trust_scores = np.array(trust_scores)
p = trust_scores / trust_scores.sum()
trust_scores.shape

# %%
rng = np.random.default_rng()
sampled_users = rng.choice(users, size=10, replace=False, p=p, shuffle=False)
