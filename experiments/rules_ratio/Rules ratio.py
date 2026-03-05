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
    pl.scan_ndjson("results/*.jl", schema_overrides={"last_post_date": pl.Datetime})
    .unique("forum_id", keep="any")
    .collect()
)
forums.shape

# %%
forums.sample(10, seed=seed)

# %%
forums.describe()

# %%
forums.group_by("title").agg(pl.len()).sort("len", "title", descending=[True, False])

# %%
rules_ratios = (
    forums.lazy()
    .group_by("bgg_id")
    .agg(
        num_threads_rules=pl.when(title="Rules").then("num_threads").otherwise(0).sum(),
        num_threads_total=pl.col("num_threads").sum(),
    )
    .with_columns(rules_ratio=pl.col("num_threads_rules") / pl.col("num_threads_total"))
    .sort("num_threads_total", descending=True)
    .collect()
)
rules_ratios.shape

# %%
rules_ratios.head(100)

# %%
games = pl.scan_ndjson(
    "/Users/markus/Recommend.Games/board-game-data/scraped/bgg_GameItem.jl",
).select("bgg_id", "name", "year", "num_votes", "complexity")
rrw = (
    rules_ratios.lazy()
    .join(games, on="bgg_id", how="left")
    .with_columns(rules_ratio_by_weight=pl.col("rules_ratio") / pl.col("complexity"))
    .sort("rules_ratio_by_weight", descending=True)
    .collect()
)
rrw.shape

# %%
rrw.head(100)

# %%
rrw.tail(100)
