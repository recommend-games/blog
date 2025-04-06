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
import polars as pl
import seaborn as sns
from tqdm import trange

jupyter_black.load()

# %%
seed = 13
rng = np.random.default_rng(seed)
num_players = 1000
num_games = 100_000_000
p_deterministic = 0.5
elo_s = 400
elo_k = 32

# %%
players_a = rng.integers(low=0, high=num_players, size=num_games)
# Sample offset for second player, ensuring it's not equal to the first
offset = rng.integers(low=1, high=num_players, size=num_games)
players_b = (players_a + offset) % num_players
players_a.shape, players_b.shape, np.sum(players_a == players_b)

# %%
deterministic = rng.random(size=num_games) < p_deterministic
deterministic.shape, deterministic.dtype

# %%
prob_player_a_wins = rng.random(size=num_games) < 0.5
prob_player_a_wins.shape, prob_player_a_wins.dtype

# %%
det_player_a_wins = players_a < players_b
det_player_a_wins.shape, det_player_a_wins.dtype

# %%
player_a_wins = np.where(deterministic, det_player_a_wins, prob_player_a_wins)
player_a_wins.shape, player_a_wins.dtype

# %%
elo_scores = np.zeros(num_players)
elo_scores.shape, elo_scores.dtype


# %%
def elo_probability(diff: float, scale: float = elo_s) -> float:
    return 1 / (1 + 10 ** (-diff / scale))


# %%
for i in trange(num_games):
    player_a = players_a[i]
    elo_a = elo_scores[player_a]
    player_b = players_b[i]
    elo_b = elo_scores[player_b]
    prob_a_wins = elo_probability(diff=elo_a - elo_b, scale=elo_s)
    outcome_a_wins = player_a_wins[i]
    elo_update = elo_k * (outcome_a_wins - prob_a_wins)
    elo_scores[player_a] += elo_update
    elo_scores[player_b] -= elo_update

# %% jp-MarkdownHeadingCollapsed=true
with pl.Config(tbl_rows=100):
    display(pl.Series(elo_scores).describe([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
p_std = elo_probability(diff=np.std(elo_scores), scale=elo_s)
p_std

# %%
quart = np.quantile(elo_scores, [0.25, 0.75])
iqr = quart[1] - quart[0]
p_iqr = elo_probability(diff=iqr, scale=elo_s)
p_iqr

# %%
sns.kdeplot(elo_scores)
