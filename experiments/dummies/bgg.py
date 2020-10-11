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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.optimize import minimize

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
def bayes(avg_rating, num_rating, dummy_value, num_dummy):
    return (avg_rating * num_rating + dummy_value * num_dummy) / (
        num_rating + num_dummy
    )


def target_rmse(num_dummy, dummy_value, data):
    return np.linalg.norm(
        data.bayes_rating
        - bayes(data.avg_rating, data.num_votes, dummy_value, num_dummy)
    )


def process_games(games, x0=np.array([1000]), dummy_value=5.5):
    result = minimize(
        fun=lambda x: target_rmse(
            num_dummy=x[0],
            dummy_value=dummy_value,
            data=games[
                games.bayes_rating.notna()
                & games.avg_rating.notna()
                & games.num_votes.notna()
            ],
        ),
        x0=x0,
        method="Nelder-Mead",
        options={
            "xatol": 1e-12,
            "maxiter": 10_000,
            "maxfev": 10_000,
            "disp": True,
        },
    )

    num_votes_total = games.num_votes.sum()
    avg_rating = (games.avg_rating * games.num_votes).sum() / num_votes_total

    return {
        "num_votes_total": num_votes_total,
        "avg_rating": avg_rating,
        "num_votes_dummy": result.x[0],
        "result": result,
    }


# %%
df = pd.read_csv(
    "~/Workspace/board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
df.drop(
    index=df.index[df.compilation == 1],
    inplace=True,
)
df.shape

# %%
process_games(df)
