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
seed = 13
cluster_fields = ("compilation_of", "implementation", "integration")
schema = {f: pl.List(pl.Int64) for f in cluster_fields}
schema.update({"bgg_id": pl.Int64, "avg_rating": pl.Float64, "num_votes": pl.Int64})

# %%
games = pl.scan_ndjson(
    source="../../../board-game-data/scraped/v3/bgg_GameItem.jl",
    schema=schema,
).select(
    "bgg_id",
    "avg_rating",
    "num_votes",
    connected_id=pl.concat_list([pl.col(f).fill_null([]) for f in cluster_fields]),
)

# %%
clusters = (
    games.select("bgg_id", "connected_id")
    .explode("connected_id")
    .drop_nulls()
    .collect()
)
clusters.shape

# %%
clusters.describe()

# %%
clusters.sample(10, seed=seed)

# %%
graph = nx.Graph()
graph.add_edges_from(clusters.iter_rows())
graph.number_of_nodes(), graph.number_of_edges(), nx.number_connected_components(graph)

# %%
largest_cluster = max(nx.connected_components(graph), key=len)
min(largest_cluster), len(largest_cluster)


# %%
def find_cluster_ids(graph):
    for component in nx.connected_components(graph):
        cluster_id = min(component)
        for bgg_id in component:
            yield bgg_id, cluster_id


cluster_id_mapping = dict(find_cluster_ids(graph))
len(cluster_id_mapping)

# %%
rankings = (
    games.select(
        "bgg_id",
        "avg_rating",
        "num_votes",
        num_dummies=pl.col("num_votes").sum() / 10_000,
    )
    .with_columns(
        bayes_rating=(
            pl.col("avg_rating").fill_null(0.0) * pl.col("num_votes").fill_null(0)
            + 5.5 * pl.col("num_dummies")
        )
        / (pl.col("num_votes").fill_null(0) + pl.col("num_dummies"))
    )
    .select(
        "bgg_id",
        rank=pl.col("bayes_rating").rank(method="random", descending=True, seed=seed),
    )
    .sort("rank")
    .with_columns(cluster_id=pl.col("bgg_id").replace(cluster_id_mapping))
)
representative = rankings.group_by("cluster_id").agg(
    representative_id=pl.col("bgg_id")
    .filter(pl.col("rank") == pl.col("rank").min())
    .first()
)
rankings = rankings.join(representative, on="cluster_id").collect()
rankings.shape

# %%
rankings.describe()

# %%
rankings.head(10)

# %%
rankings.select("bgg_id", "representative_id").write_csv("clusters.csv")