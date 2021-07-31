# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
from datetime import date
import pandas as pd

pd.options.display.max_columns = 100
pd.options.display.max_rows = 1000
pd.options.display.float_format = "{:.6g}".format

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
    low_memory=False,
)
games.drop(index=games[games["compilation_of"].notna()].index, inplace=True)
games["cooperative"] = games["cooperative"].fillna(False).astype(bool)
games.shape

# %%
games["cooperative"].mean()

# %%
games[games["cooperative"]].sort_values("year").head(10)

# %%
years = games.groupby("year")["cooperative"].agg(["size", "sum", "mean"])
years[(years.index >= 1900) & (years.index <= date.today().year)]
