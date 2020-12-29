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
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
from pytility import parse_date

SEED = 23

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
games.shape


# %%
def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


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
# %%time
try:
    df = pd.read_feather("charts.feather").set_index('updated_at')
except Exception:
    with open(
        "../../../board-game-scraper/feeds/bgg/RatingItem/2020-12-28T07-00-47-merged.jl"
    ) as file:
        df = pd.DataFrame.from_records(process_ratings(file), index="updated_at")
    df.reset_index().to_feather("charts.feather")
    df.to_pickle("charts.pickle")
df.shape

# %%
df.sample(10, random_state=SEED)

# %%
weeks = df.resample("W").item_id.count()
weeks[-52:]

# %%
weeks.plot()

# %%
df.bgg_user_rating.hist(bins=10)


# %%
def calculate_charts(
    ratings, end_date=None, window=timedelta(days=30), percentiles=(0.25, 0.75)
):
    end_date = end_date or now()
    start_date = end_date - window

    previous_ratings = ratings[ratings.index <= end_date]
    recent_ratings = previous_ratings[previous_ratings.index >= start_date]

    pct_lower, pct_upper = percentiles

    tmp = pd.DataFrame()
    tmp["positive"] = (
        recent_ratings[
            recent_ratings["bgg_user_rating"]
            >= recent_ratings["bgg_user_rating"].quantile(pct_upper)
        ]
        .groupby("bgg_id")["item_id"]
        .count()
    )
    tmp["negative"] = (
        recent_ratings[
            recent_ratings["bgg_user_rating"]
            <= recent_ratings["bgg_user_rating"].quantile(pct_lower)
        ]
        .groupby("bgg_id")["item_id"]
        .count()
    )
    tmp.fillna(0, inplace=True)
    tmp["diff"] = tmp["positive"] - tmp["negative"]

    games = previous_ratings.groupby("bgg_id")["bgg_user_rating"].count()
    scores = tmp["diff"] * games.rank(pct=True, ascending=False)
    scores.dropna(inplace=True)

    ranking = pd.DataFrame(
        data={
            "rank": scores.rank(ascending=False, method="min").astype(int),
            "score": scores,
        },
        index=scores.index,
    )
    return ranking.sort_values("rank")


# %%
charts = calculate_charts(df)
charts["name"] = games["name"]
charts[:10]


# %% [markdown]
# # Exponential decay
#
# **Idea**: Use exponential decay. For each rating, calculate its weight through its age (e.g., `1` if it's been cast right now, `0.5` if a month ago, `0.25` if two months ago, etc). Then sum weights instead of just counting within window.

# %%
def decay(
    dates,
    anchor=None,
    halflife=60 * 60 * 24 * 30,  # 30 days
):
    anchor = pd.Timestamp(anchor) if anchor is not None else pd.Timestamp.utcnow()
    ages = (anchor - dates).total_seconds()
    return np.exp2(-ages / halflife)


# %%
def calculate_decayed_charts(
    ratings,
    end_date=None,
    halflife=60 * 60 * 24 * 30,  # 30 days
    percentiles=(0.25, 0.75),
):
    end_date = end_date or pd.Timestamp.utcnow()
    pct_lower, pct_upper = percentiles

    ratings = ratings[ratings.index <= end_date]
    weights = decay(dates=ratings.index, anchor=end_date, halflife=halflife)

    tmp = pd.DataFrame(
        data={
            "bgg_id": ratings["bgg_id"],
            "positive": np.where(
                ratings["bgg_user_rating"]
                >= ratings["bgg_user_rating"].quantile(pct_upper),
                weights,
                0,
            ),
            "negative": np.where(
                ratings["bgg_user_rating"]
                <= ratings["bgg_user_rating"].quantile(pct_lower),
                weights,
                0,
            ),
        }
    )

    grouped = tmp.groupby("bgg_id").sum()
    raw_scores = grouped["positive"] - grouped["negative"]
    games = ratings.groupby("bgg_id")["bgg_user_rating"].count()
    scores = raw_scores * games.rank(pct=True, ascending=False)
    scores.dropna(inplace=True)

    ranking = pd.DataFrame(
        data={
            "rank": scores.rank(ascending=False, method="min").astype(int),
            "score": scores,
        },
        index=scores.index,
    )
    return ranking.sort_values("rank")


# %%
decayed_charts = calculate_decayed_charts(df)
decayed_charts["name"] = games["name"]
decayed_charts[:10]
