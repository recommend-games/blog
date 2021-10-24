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
from pytility import parse_date
from aggregated_hotness.hotness import aggregate_hotness

# %load_ext nb_black
# %load_ext lab_black

# %%
hot_dir = Path("../../../board-game-data/rankings/bgg/hotness/").resolve()
hot_dir

# %%
aggregated_hotness = aggregate_hotness(
    path_dir=hot_dir,
    start_date=parse_date("2021-08-01T00:00Z"),
    end_date=parse_date("2021-10-01T00:00Z"),
    top=30,
)
aggregated_hotness.head(50)
