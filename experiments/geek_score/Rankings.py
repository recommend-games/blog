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
import csv
import pandas as pd
from datetime import datetime, timezone
from geek_score.rankings import print_rankings_report
from more_itertools import first
from pathlib import Path
from pytility import parse_int

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
    with file.open(encoding="utf-8") as file_obj:
        row = first(csv.DictReader(file_obj), default=None)
    if row is None:
        return None
    bgg_id = parse_int(row.get("bgg_id"))
    rank = parse_int(row.get("rank"))
    if not bgg_id or rank != 1:
        return None
    timestamp = datetime.strptime(
        file.stem,
        "%Y%m%d-%H%M%S",
    ).replace(tzinfo=timezone.utc)
    return bgg_id, timestamp


# %%
rankings = pd.DataFrame.from_records(
    data=(
        row
        for file in rankings_path.glob("*.csv")
        if (row := parse_ranking_file(file)) is not None
    ),
    columns=("bgg_id", "timestamp"),
    index="timestamp",
)
rankings.sort_index(inplace=True)
rankings.shape

# %%
sorted(rankings.bgg_id.unique())

# %%
print_rankings_report(rankings, games)
