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

from pytility import parse_date
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
cutoff = df[
    (df.min_mse > 10) | (df.index < parse_date("2019-07-01", timezone.utc))
].index.max()
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
model = LinearRegression(fit_intercept=False)
X = data.num_votes_total.values.reshape(-1, 1)  # need a matrix
y = data.num_votes_dummy
model.fit(X, y)

# %%
coef = model.coef_[0]
coef * 10_000

# %%
x0 = data.num_votes_total.min()
x1 = data.num_votes_total.max()
y0 = coef * x0
y1 = coef * x1

# %%
data.sort_values("num_votes_total").plot(
    x="num_votes_total",
    y="num_votes_dummy",
    style="k-",
    linewidth=3,
    legend=False,
    xlabel="total ratings",
    ylabel="dummy ratings",
)
plt.plot([x0, x1], [y0, y1], "r--", linewidth=2)

# %%
(data.num_votes_total / 10_000 - data.num_votes_dummy).abs().sum() / len(data)
