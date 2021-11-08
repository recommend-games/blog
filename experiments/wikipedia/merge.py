# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import logging
import sys
from board_game_scraper.merge import merge_data, _spark_session

# %load_ext nb_black
# %load_ext lab_black

# %%
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
)

# %%
spark = _spark_session(log_level="WARN")

# %%
df = merge_data(
    in_paths="/Users/markus/Recommend.Games/board-game-scraper/feeds/wiki_stats/GameItem/2021-11-05T11-13-58-riemann.jl",
    keys=("url", "published_at"),
    key_types=("str", "date"),
    latest="scraped_at",
    latest_types="date",
    latest_required=True,
    fieldnames=("url", "published_at", "page_views", "scraped_at"),
    log_level="WARN",
)

# %%
wiki_bgg = spark.read.csv(
    path="/Users/markus/Recommend.Games/recommend-games-blog/experiments/wikipedia/wiki_bgg_links.csv",
    header=True,
    inferSchema=True,
).withColumnRenamed("wikipedia_url", "url")

# %%
joined = df.join(wiki_bgg, on="url", how="inner")

# %%
agged = (
    joined.groupBy("published_at", "bgg_id", "lang")
    .sum("page_views")
    .withColumnRenamed("sum(page_views)", "page_views")
)

# %%
pivoted = (
    agged.groupby("published_at", "bgg_id")
    .pivot("lang")
    .sum("page_views")
    .sort("published_at", "bgg_id")
)

# %%
pivoted.coalesce(1).write.json("out")
