# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import networkx as nx
import polars as pl

jupyter_black.load()

# %%
games = pl.scan_ndjson(
    source="../../../board-game-data/scraped/bgg_GameItem.jl",
    schema={
        "bgg_id": pl.Int64,
        "compilation_of": pl.List(pl.Int64),
        "implementation": pl.List(pl.Int64),
        "integration": pl.List(pl.Int64),
        "avg_rating": pl.Float64,
        "num_votes": pl.Int64,
    },
).select(
    "bgg_id",
    pl.concat_list(
        pl.col("compilation_of").fill_null([]),
        pl.col("implementation").fill_null([]),
        pl.col("integration").fill_null([]),
    ).alias("connected_id"),
    "avg_rating",
    "num_votes",
)

clusters = (
    games.explode("connected_id")
    .select(
        "bgg_id",
        pl.col("connected_id").fill_null(pl.col("bgg_id")),
    )
    .collect()
)

clusters.shape

# %%
clusters.describe()

# %%
clusters.sample(10)

# %%
graph = nx.Graph()
graph.add_edges_from(clusters.iter_rows())
graph.number_of_nodes(), graph.number_of_edges(), nx.number_connected_components(graph)

# %%
max(nx.connected_components(graph), key=len)
