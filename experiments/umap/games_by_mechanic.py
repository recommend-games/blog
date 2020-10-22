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
)
df.shape

# %%
df_filtered = (
    df[
        (df.num_votes >= 100)
        & (df["rank"].notnull())
        & (df.compilation == 0)
        & (df.mechanic.notnull())
    ]
    .reset_index(drop=True)
    .copy()
)
df_filtered.shape

# %%
df_filtered.mechanic

# %%
cv = CountVectorizer(binary=True)  # TfidfVectorizer(binary=True)
mechanics = cv.fit_transform(df_filtered.mechanic)
mechanics.shape

# %%
model = umap.UMAP(metric="jaccard", random_state=SEED)  # metric="hellinger"
model.fit(mechanics.todense())

# %%
umap_plot = umap.plot.points(
    model,
    # labels=np.log(df_filtered.num_votes.values),
    labels=-df_filtered["rank"],
    theme="fire",
    show_legend=False,
)

# %%
from bokeh.plotting import show, save, output_notebook, output_file
from bokeh.resources import INLINE

output_notebook(resources=INLINE)

# %%
hover_df = df_filtered[
    ["name", "year", "avg_rating", "num_votes", "bayes_rating", "rank"]
]
plot = umap.plot.interactive(
    model,
    # labels=np.log(df_filtered.num_votes.values),
    labels=-df_filtered["rank"],
    hover_data=hover_df,
    theme="fire",
    point_size=5,
)
show(plot)
