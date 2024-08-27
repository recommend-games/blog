# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import date
from pathlib import Path

import jupyter_black
import polars as pl

from debiased_rankings.data import load_data
from debiased_rankings.model import debias

jupyter_black.load()
pl.Config.set_tbl_rows(100)

this_year = date.today().year

# %%
base_dir = Path(".").resolve()
project_dir = base_dir.parent.parent
data_dir = project_dir.parent / "board-game-data"
base_dir, project_dir, data_dir

# %%
data = load_data(
    path=data_dir / "scraped" / "bgg_GameItem.jl",
    min_year=1970,
    max_year=this_year,
    max_min_time=360,
)
data.shape

# %%
data.describe()

# %%
data.sample(10, seed=this_year)

# %%
regressor_cols = (
    "age",
    "complexity",
    "min_time",
    "cooperative",
    "Abstract Game:4666",
    "Children's Game:4665",
    "Customizable:4667",
    "Family Game:5499",
    "Party Game:5498",
    "Strategy Game:5497",
    "Thematic:5496",
    "War Game:4664",
)
model, data = debias(
    data=data,
    target_col="avg_rating",
    regressor_cols=regressor_cols,
)
data.shape

# %%
model.summary().tables[1]

# %%
data.sort("rank_debiased").head(10)
