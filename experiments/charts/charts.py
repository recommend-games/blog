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
    end_date = end_date or datetime.utcnow().replace(tzinfo=timezone.utc)
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
print(charts.shape)
charts[:50]

# %%
charts[-10:]

# %%
for end_date in pd.date_range(
    start=df.index.min().replace(hour=23, minute=59, second=59),
    end=df.index.max(),
    freq="M",
):
    print(f"Charts as of {end_date.strftime('%Y-%m-%d')}")
    charts = calculate_charts(ratings=df, end_date=end_date)
    charts["name"] = games["name"]
    print(charts[:10])
    print()
