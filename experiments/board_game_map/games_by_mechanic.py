# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import logging
import os.path
import sys

from datetime import timezone
from pathlib import Path

import jupyter_black
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import umap
import umap.plot

from bokeh.plotting import show, save, output_notebook, output_file
from bokeh.resources import INLINE
from pytility import parse_date
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LinearRegression

jupyter_black.load()

LOGGER = logging.getLogger(__name__)
SEED = 23
BASE_DIR = Path().resolve().parent.parent

output_notebook(resources=INLINE)

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
)

# %%
games_file = BASE_DIR.parent / "board-game-data" / "scraped" / "bgg_GameItem.csv"
df = pd.read_csv(games_file)
df.shape

# %%
df_filtered = (
    df[
        (df.num_votes >= 100)
        & (df["rank"].notnull())
        & (df.compilation != 1)
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
model.fit(mechanics.toarray())

# %%
umap_plot = umap.plot.points(
    model,
    # labels=np.log(df_filtered.num_votes.values),
    labels=-df_filtered["rank"],
    theme="fire",
    show_legend=False,
)

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
