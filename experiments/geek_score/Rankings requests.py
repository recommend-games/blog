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
import requests
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
data_path, games_path

# %%
games = pd.read_csv(games_path, index_col="bgg_id")
games.shape


# %%
def fetch_rankings(bgg_id):
    url = f"https://api.geekdo.com/api/historicalrankgraph?objectid={bgg_id}&objecttype=thing&rankobjectid=1"
    response = requests.get(url)
    data = response.json()["data"]
    for row in data:
        rank = row[1]
        if rank != 1:
            continue
        date = datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc)
        yield date


# %%
top_games = [3076, 12333, 31260, 161936, 174430, 224517]

# %%
top = {}
for bgg_id in top_games:
    rankings = fetch_rankings(bgg_id)
    for date in rankings:
        top[date] = bgg_id

# %%
total = defaultdict(int)

for bgg_id, group in groupby(sorted(top.items()), key=lambda x: x[1]):
    name = games.loc[bgg_id]["name"]
    timestamps = (x[0] for x in group)
    begin = first(timestamps)
    end = last(timestamps, default=begin)
    diff = end - begin
    days = round(diff.total_seconds() / 60 / 60 / 24) + 1
    print(
        f"{name:25}: {days:>4} day{'s' if days > 1 else ' '} ({begin.date()} to {end.date()})"
    )
    total[bgg_id] += days

# %%
for bgg_id, days in sorted(total.items(), key=lambda x: -x[1]):
    name = games.loc[bgg_id]["name"]
    print(f"{name:25}: {days:>4} day{'s' if days > 1 else ''}")
