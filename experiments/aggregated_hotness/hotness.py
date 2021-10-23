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

# %load_ext nb_black
# %load_ext lab_black

# %%
hot_dir = Path("../../../board-game-data/rankings/bgg/hotness/").resolve()
hot_dir

# %%
pd.read_csv(
    max(hot_dir.glob("*.csv")),
    index_col="bgg_id",
)["rank"]
