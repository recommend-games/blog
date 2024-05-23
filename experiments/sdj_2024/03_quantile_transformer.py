# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import joblib
import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from sklearn.preprocessing import QuantileTransformer

jupyter_black.load()

# %%
ratings = (
    pl.scan_ndjson("../../../board-game-data/scraped/bgg_RatingItem.jl")
    .select("bgg_user_rating")
    .drop_nulls()
    .filter(pl.col("bgg_user_rating") >= 1)
    .collect()
)
ratings.shape

# %%
ratings.sample(10)

# %%
ratings.describe()

# %%
qt = QuantileTransformer(output_distribution="uniform", subsample=1_000_000)
qt.fit(ratings)

# %%
sample = ratings.sample(10_000)
sns.histplot(sample["bgg_user_rating"], bins=10)

# %%
sns.histplot(qt.transform(sample)[:, 0], bins=10)

# %%
x = np.arange(1, 11).reshape(-1, 1)
y = qt.transform(x)
dict(zip(x[:, 0], y[:, 0]))

# %%
joblib.dump(qt, "qt.joblib")
