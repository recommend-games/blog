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
experiments = (
    ("age",),
    ("complexity",),
    ("min_time",),
    ("cooperative",),
    (
        "Abstract Game:4666",
        "Children's Game:4665",
        "Customizable:4667",
        "Family Game:5499",
        "Party Game:5498",
        "Strategy Game:5497",
        "Thematic:5496",
        "War Game:4664",
    ),
    (
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
    ),
)

# %%
for regressor_cols in experiments:
    print("***", "Columns:", ", ".join(regressor_cols), "***")
    model, exp_results = debias(
        data=data,
        target_col="avg_rating",
        regressor_cols=regressor_cols,
    )
    print()
    print(model.summary().tables[1])
    print()
    with pl.Config(
        tbl_formatting="ASCII_MARKDOWN",
        tbl_hide_column_data_types=True,
        tbl_hide_dataframe_shape=True,
        tbl_width_chars=10000,
        tbl_cols=-1,
        fmt_str_lengths=20,
    ):
        print(
            exp_results.sort("rank_debiased")
            .select(
                "bgg_id",
                "name",
                "year",
                "rank",
                "avg_rating",
                "avg_rating_debiased",
            )
            .head(10)
        )
    print()
    print()
    print()
