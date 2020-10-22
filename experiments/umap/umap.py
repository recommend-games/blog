# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import logging
import os.path
import sys

from datetime import timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import umap
import umap.plot

from pytility import parse_date
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LinearRegression

LOGGER = logging.getLogger(__name__)
SEED = 23

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
)

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
df = pd.read_csv(
    "/Users/markus/Workspace/board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
)
df.shape

# %%
df_filtered = df[
    (df.num_votes >= 100)
    & (df["rank"].notnull())
    & (df.compilation == 0)
    & (df.mechanic.notnull())
]
df_filtered.shape

# %%
df_filtered.mechanic

# %%
cv = CountVectorizer(binary=True)
mechanics = cv.fit_transform(df_filtered.mechanic)
mechanics.shape

# %%
model = umap.UMAP(metric="jaccard", random_state=SEED)
model.fit(mechanics.todense())

# %%
umap_plot = umap.plot.points(
    model,
    labels=np.log(df_filtered.num_votes.values),
    theme="fire",
    show_legend=False,
)
