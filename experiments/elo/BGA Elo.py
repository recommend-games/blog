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
import polars as pl
from elo.elo_ratings_multi import RankOrderedLogitElo
from elo.optimal_k import approximate_optimal_k_multi

jupyter_black.load()
pl.Config.set_tbl_rows(100)

num_matches_regulars = 25
game_id = 1741  # Ark Nova

# %%
data = pl.read_ipc(f"results/arrow/matches/{game_id}.arrow", memory_map=False)
data.shape

# %%
data.sample(10)

# %%
data.describe()

# %%
players = (
    data.lazy()
    .select(pl.col("player_ids").explode().value_counts())
    .unnest("player_ids")
)
players.describe(percentiles=(0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99))

# %%
players.select(
    frac_regulars=(pl.col("count") >= num_matches_regulars).sum() / pl.len()
).collect()

# %%
matches = (
    dict(zip(player_ids, payoffs))
    for player_ids, payoffs in zip(data["player_ids"], data["payoffs"])
)

# %%
elo = RankOrderedLogitElo()
elo.update_elo_ratings_batch(matches, full_results=True, progress_bar=True)
len(elo.elo_ratings)

# %%
sorted(elo.elo_ratings.items(), key=lambda x: -x[1])[:100]

# %%
# This will take very very long if there's a large number of matches
optimal_k = approximate_optimal_k_multi(
    matches=matches,
    min_elo_k=0,
    max_elo_k=200,
    elo_scale=400,
)
optimal_k
