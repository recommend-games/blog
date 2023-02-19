# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
from collections import defaultdict
from datetime import datetime, timezone
from itertools import groupby
from more_itertools import first, last
from pathlib import Path

pd.options.display.max_columns = 150
pd.options.display.max_rows = 150

# %load_ext nb_black
# %load_ext lab_black

# %%
data_path = (Path(".") / ".." / ".." / ".." / "board-game-data").resolve()
games_path = (data_path / "scraped" / "bgg_GameItem.csv").resolve()
rankings_path = (data_path / "rankings" / "bgg" / "bgg").resolve()
data_path, games_path, rankings_path

# %%
games = pd.read_csv(games_path, index_col="bgg_id")
games.shape


# %%
def parse_ranking_file(file):
    df = pd.read_csv(file, nrows=1)
    df["timestamp"] = datetime.strptime(
        file.stem,
        "%Y%m%d-%H%M%S",
    ).replace(tzinfo=timezone.utc)
    return df.iloc[0]


# %%
rankings = pd.DataFrame.from_records(
    data=map(parse_ranking_file, rankings_path.glob("*.csv")), index="timestamp",
)
rankings.sort_index(inplace=True)
rankings.shape

# %%
rankings.drop(df[df["rank"] != 1].index, inplace=True)
rankings.drop(columns="rank", inplace=True)
rankings.shape

# %%
sorted(rankings.bgg_id.unique())

# %%
total = defaultdict(int)

for bgg_id, group in groupby(df.itertuples(), key=lambda x: x.bgg_id):
    name = games.loc[bgg_id]["name"]
    timestamps = (row.Index for row in group)
    begin = first(timestamps)
    end = last(timestamps, default=begin)
    diff = end - begin
    days = diff.days + 1
    print(
        f"{name:25}: {days:>4} day{'s' if days > 1 else ' '} ({begin.date()} to {end.date()})"
    )
    total[bgg_id] += days

# %%
for bgg_id, days in sorted(total.items(), key=lambda x: -x[1]):
    name = games.loc[bgg_id]["name"]
    print(f"{name:25}: {days:>4} day{'s' if days > 1 else ''}")
