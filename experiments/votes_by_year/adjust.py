# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from pytility import parse_date

SEED = 23

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

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
        records = filter(None, map(process_row, f))
        df = pd.DataFrame.from_records(records, index="item_id")
    df["year"] = df.updated_at.apply(lambda x: x[:4]).astype("int32")
    return df


# %%
path_csv = Path("bgg_RatingItem.csv").resolve()
path_jl = Path("../../../board-game-data/scraped/bgg_RatingItem.jl").resolve()

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

# %%
plt.savefig("ratings_by_year.svg")
