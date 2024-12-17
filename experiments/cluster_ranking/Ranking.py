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
import polars as pl

jupyter_black.load()

# %%
games = pl.scan_ndjson("../../../board-game-data/scraped/v3/bgg_GameItem.jl").select(
    "bgg_id",
    "name",
    "year",
)
clusters = pl.scan_csv("clusters.csv")
cluster_lists = (
    clusters.group_by("representative_id")
    .agg(pl.col("bgg_id").sort(), pl.len())
    .filter(pl.col("len") > 1)
    .drop("len")
    .rename({"representative_id": "bgg_id", "bgg_id": "cluster"})
)
ranking = (
    pl.scan_ndjson("../../../board-game-data/scraped/bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_rating")
    .drop_nulls()
    .join(clusters, on="bgg_id")
    .group_by("representative_id", "bgg_user_name")
    .agg(pl.col("bgg_user_rating").max())
    .rename({"representative_id": "bgg_id"})
    .group_by("bgg_id")
    .agg(
        avg_rating=pl.col("bgg_user_rating").mean(),
        num_votes=pl.len(),
    )
    .with_columns(num_dummies=pl.col("num_votes").sum() / 10_000)
    .filter(pl.col("num_votes") >= 30)
    .with_columns(
        bayes_rating=(
            pl.col("avg_rating") * pl.col("num_votes") + 5.5 * pl.col("num_dummies")
        )
        / (pl.col("num_votes") + pl.col("num_dummies")),
    )
    .with_columns(rank=pl.col("bayes_rating").rank(method="min", descending=True))
    .sort("rank")
    .join(games, on="bgg_id", how="left")
    .join(cluster_lists, on="bgg_id", how="left")
    .select(
        "rank",
        "bgg_id",
        "name",
        "year",
        "num_votes",
        "avg_rating",
        "bayes_rating",
        "cluster",
    )
    .collect()
)
ranking.shape

# %%
ranking.head(10)

# %%
ranking.with_columns(
    pl.col("cluster").cast(pl.List(pl.String)).list.join(", "),
).write_csv("ranking.csv", float_precision=5)
