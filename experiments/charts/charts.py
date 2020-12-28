# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json

import pandas as pd

from pytility import parse_date

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
def process_ratings(
    lines, keys=("item_id", "bgg_id", "bgg_user_name", "bgg_user_rating", "updated_at")
):
    for line in lines:
        item = json.loads(line)
        if not item or not item.get("bgg_user_rating"):
            continue
        yield {
            k: parse_date(item.get(k)) if k.endswith("_at") else item.get(k)
            for k in keys
        }


# %%
with open(
    "../../../board-game-scraper/feeds/bgg/RatingItem/2020-12-28T07-00-47-merged.jl"
) as file:
    df = pd.DataFrame.from_records(process_ratings(file), index="updated_at")
df.shape

# %%
df.sample(25)

# %%
df.reset_index().to_feather("charts.feather")

# %%
df.to_pickle("charts.pickle")

# %%
weeks = df.resample("W").item_id.count()
weeks[-52:]

# %%
weeks.plot()

# %%
df.bgg_user_rating.hist(bins=10)

# %%
(df.bgg_user_rating >= 8).mean()

# %%
cutoff = parse_date("2020-12-01T00:00Z")
recent = df[df.index >= cutoff]
recent.bgg_user_rating.describe()

# %%
positive = (
    recent[recent.bgg_user_rating >= recent.bgg_user_rating.quantile(0.75)]
    .groupby("bgg_id")
    .item_id.count()
)
positive.sort_values(ascending=False)[:50]

# %%
negative = (
    recent[recent.bgg_user_rating <= recent.bgg_user_rating.quantile(0.25)]
    .groupby("bgg_id")
    .item_id.count()
)
negative.sort_values(ascending=False)[:50]

# %%
diff = (positive - negative).sort_values(ascending=False)
diff[:50]

# %% [markdown]
# **Idea**: Discount that `positive - negative` score by rank according to number of ratings:
#
# ```python
# score = (positive - negative) * games.num_ratings.rank(pct=True)
# ```
#
# That way, games with a lot of ratings will have their value heavily discounted (almost to zero), while games with very few ratings will get the full score.

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
games.shape

# %%
games["score"] = diff * games.num_votes.rank(pct=True, ascending=False)
games.sort_values("score", ascending=False)[["name", "year", "score"]][:50]
