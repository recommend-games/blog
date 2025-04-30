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

game_id = 1741  # Ark Nova

# %%
data = (
    pl.scan_ipc("results/arrow/matches-*.arrow")
    .filter(pl.col("game_id") == game_id)
    .sort("scraped_at", "timestamp")
    .unique("id", keep="first")
    .select(
        num_players=pl.col("players").list.len(),
        player_ids=pl.col("players").list.eval(pl.element().struct.field("player_id")),
        places=pl.col("players").list.eval(pl.element().struct.field("place")),
    )
    .filter(pl.col("num_players") >= 2)
    .filter(pl.col("player_ids").list.eval(pl.element().is_not_null()).list.all())
    .filter(
        pl.col("places")
        .list.eval(pl.element().is_not_null() & (pl.element() >= 1))
        .list.all()
    )
    .with_columns(payoffs=pl.col("places").list.eval(pl.len() - pl.element()))
    .filter(pl.col("payoffs").list.eval(pl.element() >= 0).list.all())
    .collect()
)
data.shape

# %%
data.sample(10)

# %%
data.describe()

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
