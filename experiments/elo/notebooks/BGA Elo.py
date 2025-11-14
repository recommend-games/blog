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
import itertools
import jupyter_black
import networkx as nx
import polars as pl
from elo.elo_ratings import RankOrderedLogitElo
from elo.optimal_k import approximate_optimal_k
from tqdm import tqdm

jupyter_black.load()
pl.Config.set_tbl_rows(100)

game_id = 9  # Lost Cities
num_matches_regulars = 25
elo_scale = 400

# %%
data = pl.read_ipc(f"../results/arrow/matches/{game_id}.arrow", memory_map=False)
num_all_matches = len(data)
data.shape

# %%
graph = nx.Graph()
for player_ids in tqdm(data["player_ids"]):
    graph.add_edges_from(itertools.combinations(player_ids, 2))
num_all_players = graph.number_of_nodes()
graph.number_of_nodes(), graph.number_of_edges()

# %%
largest_community = max(nx.connected_components(graph), key=len)
num_players = len(largest_community)
num_players

# %%
data = data.filter(
    pl.col("player_ids").list.eval(pl.element().is_in(largest_community)).list.any()
)
num_matches = len(data)
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
player_stats = players.describe(
    percentiles=(0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99)
)
num_matches_max = int(player_stats["count"][-1])
player_stats

# %%
num_regular_players = (
    players.filter(pl.col("count") >= num_matches_regulars)
    .select(pl.len())
    .collect()
    .item()
)
num_regular_players

# %%
print(f"Number of matches: {num_all_matches} (all) / {num_matches} (connected only)")
print(
    f"Number of players: {num_all_players} (all) / {num_players} (connected only) / {num_regular_players} (regulars only)"
)
print(f"Maximum number of plays by a single player: {num_matches_max}")

# %%
matches = [
    dict(zip(player_ids, payoffs))
    for player_ids, payoffs in zip(data["player_ids"], data["payoffs"])
]

# %%
# This will take very very long if there's a large number of matches
optimal_k = approximate_optimal_k(
    matches=matches,
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
    elo_scale=elo_scale,
)
optimal_k

# %%
elo = RankOrderedLogitElo(elo_k=optimal_k, elo_scale=elo_scale)
elo.update_elo_ratings_batch(
    matches,
    full_results=True,
    progress_bar=True,
    tqdm_kwargs={"total": len(data)},
)
len(elo.elo_ratings)

# %%
sorted(elo.elo_ratings.items(), key=lambda x: -x[1])[:100]
