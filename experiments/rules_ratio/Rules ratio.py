# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl

jupyter_black.load()

pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_rows(100)

seed = 13

# %%
forums = (
    pl.scan_ndjson("results/*.jl")
    .unique("forum_id", keep="any")
    .select("bgg_id", "title", "num_threads")
)
rules_ratios = (
    forums.group_by("bgg_id")
    .agg(
        num_forums=pl.len(),
        num_threads_rules=pl.when(title="Rules").then("num_threads").otherwise(0).sum(),
        num_threads_total=pl.col("num_threads").sum(),
    )
    .remove(pl.col("num_forums") < 10)
    .remove(pl.col("num_threads_total") < 10)
    .with_columns(rules_ratio=pl.col("num_threads_rules") / pl.col("num_threads_total"))
)
games = (
    pl.scan_ndjson(
        "/Users/markus/Recommend.Games/board-game-data/scraped/bgg_GameItem.jl",
        infer_schema_length=10_000,
    )
    .remove(pl.col("compilation"))
    .select("bgg_id", "name", "year", "num_votes", "complexity")
    .remove(pl.col("num_votes") < 100)
)
rrw = (
    rules_ratios.join(games, on="bgg_id", how="inner")
    .with_columns(rules_ratio_by_weight=pl.col("rules_ratio") / pl.col("complexity"))
    .sort(
        "rules_ratio_by_weight",
        "rules_ratio",
        "num_threads_total",
        descending=[True, True, False],
    )
    .collect()
)
rrw.shape

# %%
forums.group_by("title").agg(pl.len()).sort(
    "len",
    "title",
    descending=[True, False],
).collect()

# %%
rrw.sample(10, seed=seed)

# %%
rrw.describe()

# %%
rrw.head(10)

# %%
rrw.tail(10)
