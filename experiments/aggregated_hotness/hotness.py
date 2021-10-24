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
from pathlib import Path
import pandas as pd
from pytility import parse_date
from aggregated_hotness.hotness import aggregate_hotness

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
    low_memory=False,
)
games.shape

# %%
hot_dir = Path("../../../board-game-data/rankings/bgg/hotness/").resolve()
hot_dir

# %%
aggregated_hotness = aggregate_hotness(
    path_dir=hot_dir,
    start_date=parse_date("2021-08-01T00:00Z"),
    end_date=parse_date("2021-10-01T00:00Z"),
    top=30,
).rename("hotness")
aggregated_hotness.shape

# %%
results = (
    games[["name"]]
    .join(aggregated_hotness, how="right")
    .sort_values("hotness", ascending=False)
)
results.head(50)
