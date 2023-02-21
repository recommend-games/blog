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
from datetime import datetime, timezone
from geek_score.rankings import print_rankings_report
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


def fetch_all_rankings(bgg_ids):
    for bgg_id in bgg_ids:
        rankings = fetch_rankings(bgg_id)
        for timestamp in rankings:
            yield bgg_id, timestamp


# %%
top_games = [3076, 12333, 31260, 161936, 174430, 224517]
rankings = pd.DataFrame.from_records(
    data=fetch_all_rankings(top_games),
    columns=("bgg_id", "timestamp"),
    index="timestamp",
)
rankings.sort_index(inplace=True)
rankings.shape

# %%
print_rankings_report(rankings, games)
