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

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
df = pd.read_csv("results.csv", parse_dates=["datetime"], index_col="datetime")
df.sort_index(inplace=True)
df.shape

# %%
df.sample(10, random_state=SEED)

# %%
cutoff = df[df.min_mse > 10].index.max()
cutoff

# %%
data = df[df.index > cutoff]
data.shape

# %%
data.num_games.plot()

# %%
data.num_games_ranked.plot()

# %%
data.num_votes_total.plot()

# %%
data.avg_rating.plot()

# %%
data.num_votes_dummy.plot()

# %%
data.min_mse.plot()

# %%
data.plot(x="num_votes_total", y="num_votes_dummy")

# %%
model = LinearRegression(fit_intercept=False)
X = data.num_votes_total.values.reshape(-1, 1)  # need a matrix
y = data.num_votes_dummy
model.fit(X, y)

# %%
model.coef_

# %%
(data.num_votes_total / 10_000 - data.num_votes_dummy).abs().sum() / len(data)
