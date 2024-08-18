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
from pathlib import Path

import jupyter_black
import polars as pl
import statsmodels.api as sm
from scipy.stats import t

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
base_dir = Path(".").resolve()
data_dir = base_dir / "data"
base_dir, data_dir

# %% [markdown]
# # Rankings

# %%
years_from_rankings = pl.read_csv(data_dir / "years_from_rankings.csv")
data_from_rankings = years_from_rankings.filter(pl.col("year") >= 1970)
years_from_rankings.shape, data_from_rankings.shape

# %%
years = sm.add_constant(data_from_rankings["year"].to_numpy())
model_from_avg_rankings = sm.OLS(
    endog=data_from_rankings["avg_rating"].to_numpy(),
    exog=years,
).fit()
model_from_avg_rankings.summary().tables[1]

# %%
alpha = 0.05  # / len(data_from_rankings)
avg_rating_pred = model_from_avg_rankings.predict(years)
influence = model_from_avg_rankings.get_influence()
data_from_rankings = data_from_rankings.with_columns(
    avg_rating_pred=avg_rating_pred
).with_columns(
    avg_rating_error=pl.col("avg_rating") - pl.col("avg_rating_pred"),
    avg_rating_error_studentized=influence.resid_studentized_internal,
)
data_from_rankings = data_from_rankings.with_columns(
    avg_rating_p_value=t.sf(
        data_from_rankings["avg_rating_error_studentized"].abs(),
        df=model_from_avg_rankings.df_resid,
    )
).with_columns(avg_rating_sig=pl.col("avg_rating_p_value") < alpha)
data_from_rankings.shape

# %%
data_from_rankings.sort(pl.col("avg_rating_p_value").abs()).head(10)

# %%
model_from_bayes_rankings = sm.OLS(
    data_from_rankings["bayes_rating"].to_numpy(),
    sm.add_constant(data_from_rankings["year"].to_numpy()),
)
results_from_bayes_rankings = model_from_bayes_rankings.fit()
results_from_bayes_rankings.summary().tables[1]

# %% [markdown]
# # Ratings

# %%
years_from_ratings = pl.read_csv(data_dir / "years_from_ratings.csv")
data_from_ratings = years_from_ratings.filter(pl.col("year") >= 1970)
years_from_ratings.shape, data_from_ratings.shape

# %%
model_from_ratings = sm.OLS(
    data_from_ratings["avg_rating"].to_numpy(),
    sm.add_constant(data_from_ratings["year"].to_numpy()),
)
results_from_ratings = model_from_ratings.fit()
results_from_ratings.summary().tables[1]
