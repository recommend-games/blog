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

# %% [markdown]
# # Synthetic Control

# %% [markdown]
# ## Init and Config

# %%
import warnings
from datetime import timedelta
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
from matplotlib import pyplot as plt

from synthetic_control.data import REVIEWS
from synthetic_control.models import sample_control_group, train_test_split, weights_and_predictions
from synthetic_control.plots import plot_effect, plot_ratings

jupyter_black.load()
np.set_printoptions(suppress=True)
warnings.filterwarnings("ignore")

# %%
game = REVIEWS[2]
game

# %%
plot_dir = (Path(".") / "plots").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
plot_dir

# %% [markdown]
# ## The Data

# %%
data = (
    pl.scan_csv("num_ratings.csv")
    .select(pl.col("timestamp").str.to_datetime(), pl.exclude("timestamp").cast(int))
    .filter(pl.col(str(game.bgg_id)).is_not_null())
    .filter(
        pl.col("timestamp").is_between(
            game.date_review - timedelta(days=game.days_before),
            game.date_review + timedelta(days=game.days_after),
        )
    )
    .collect()
)
data.shape

# %%
data.head(10)

# %%
ax = plot_ratings(data, game)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_num_ratings.png")
plt.show()

# %%
data_train, data_test = train_test_split(data, game)
data_train.shape, data_test.shape

# %%
control_ids = sample_control_group(data_train, game)
len(control_ids)

# %%
X_train = data_train.select(*control_ids).to_numpy()
y_train = data_train.select(str(game.bgg_id)).to_numpy().reshape(-1)
X_test = data_test.select(*control_ids).to_numpy()
y_test = data_test.select(str(game.bgg_id)).to_numpy().reshape(-1)
X_train.shape, y_train.shape, X_test.shape, y_test.shape

# %% [markdown]
# ## Linear Regression

# %%
_, y_pred_lr = weights_and_predictions("linear", X_train, y_train, X_test)
y_pred_lr.shape

# %%
ax = plot_ratings(data, game, y_pred_lr)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_lr.png")
plt.show()

# %% [markdown]
# ## Ridge Regression

# %%
_, y_pred_ridge = weights_and_predictions("ridge", X_train, y_train, X_test)
y_pred_ridge.shape

# %%
plot_ratings(data, game, y_pred_ridge)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_ridge.png")
plt.show()

# %%
plot_effect(data, game, y_pred_ridge)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_ridge.png")
plt.show()

# %% [markdown]
# ## Convex combination

# %%
weights_slsqp, y_pred_slsqp = weights_and_predictions("slsqp", X_train, y_train, X_test)
weights_slsqp.shape, y_pred_slsqp.shape

# %%
{
    bgg_id: weight
    for bgg_id, weight in zip(control_ids, weights_slsqp)
    if weight >= 0.001
}

# %%
plot_ratings(data, game, y_pred_slsqp)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_slsqp.png")
plt.show()

# %%
plot_effect(data, game, y_pred_slsqp)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp.png")
plt.show()
