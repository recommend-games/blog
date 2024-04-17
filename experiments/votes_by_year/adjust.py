# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import json
from datetime import date
from pathlib import Path

import jupyter_black
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pytility import parse_date
from tqdm import tqdm

jupyter_black.load()

SEED = 23


# %%
def process_row(
    item,
    columns=(
        "item_id",
        "bgg_id",
        "bgg_user_name",
        "bgg_user_owned",
        "bgg_user_play_count",
        "bgg_user_rating",
        "updated_at",
    ),
):
    item = json.loads(item)
    if isinstance(item, dict) and all(
        item.get(column) is not None for column in columns
    ):
        return {column: item[column] for column in columns}
    return None


def df_from_jl(path):
    with open(path) as f:
        records = filter(None, map(process_row, tqdm(f)))
        df = pd.DataFrame.from_records(records, index="item_id")
    df["year"] = df.updated_at.apply(lambda x: x[:4]).astype("int32")
    return df


# %%
path_csv = Path("bgg_RatingItem.csv").resolve()
path_jl = Path("../../../board-game-data/scraped/bgg_RatingItem.jl").resolve()
path_games = Path("../../../board-game-data/scraped/bgg_GameItem.csv").resolve()

# %%
try:
    df = pd.read_csv(path_csv, index_col="item_id", dtype={"item_id": "object"})
except Exception:
    df = df_from_jl(path_jl)
df.shape

# %%
df.sample(5, random_state=SEED).T

# %%
if not path_csv.exists():
    df.to_csv(path_csv)

# %%
by_year = df.groupby("year").bgg_id.count()
by_year

# %%
now = date.today()
eoy = date(now.year, 12, 31)

# %%
eoy_adj = by_year[now.year] * eoy.timetuple().tm_yday / now.timetuple().tm_yday
eoy_adj

# %%
by_year[by_year.index < now.year].plot(style="k-", linewidth=3)
plt.plot([now.year - 1, now.year], [by_year[now.year - 1], eoy_adj], "k:", linewidth=3)
plt.tight_layout()
plt.savefig("ratings_by_year.svg")
plt.show()

# %%
games = pd.read_csv(path_games, index_col="bgg_id")
games.compilation = games.compilation.notnull()
games.cooperative = games.cooperative.notnull()
games.shape

# %%
games.sample(5, random_state=SEED).T

# %%
votes_by_year = games.groupby("year").num_votes.agg(["sum", "mean", "median"])

# %%
votes_by_year[(votes_by_year.index >= 1980) & (votes_by_year.index <= 2020)][
    "sum"
].plot(style="k-", linewidth=3)

# %%
votes_by_year[(votes_by_year.index >= 1980) & (votes_by_year.index <= 2020)][
    "mean"
].plot(style="k-", linewidth=3)

# %%
votes_by_year[(votes_by_year.index >= 1980) & (votes_by_year.index <= 2020)][
    "median"
].plot(style="k-", linewidth=3)

# %%
votes_by_year_ranked = (
    games[~games.compilation & games["rank"].notnull() & games.bayes_rating.notnull()]
    .groupby("year")
    .num_votes.agg(["sum", "mean", "median"])
)

# %%
votes_by_year_ranked[
    (votes_by_year_ranked.index >= 1980) & (votes_by_year_ranked.index <= 2020)
]["sum"].plot(style="k-", linewidth=3)

# %%
votes_by_year_ranked[
    (votes_by_year_ranked.index >= 1980) & (votes_by_year_ranked.index <= 2020)
]["mean"].plot(style="k-", linewidth=3)

# %%
votes_by_year_ranked[
    (votes_by_year_ranked.index >= 1980) & (votes_by_year_ranked.index <= 2020)
]["median"].plot(style="k-", linewidth=3)

# %%
sns.violinplot(
    x="year",
    y="num_votes",
    data=games[(games.year >= 1990) & (games.year <= 2000)],
)
plt.ylim(0, 1_000)
