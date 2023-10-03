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
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from joblib import Parallel, delayed
from matplotlib import pyplot as plt

from synthetic_control.data import REVIEWS
from synthetic_control.models import (
    sample_control_and_predict,
    sample_control_group,
    train_test_split,
    weights_and_predictions,
)
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

# %%
game_data = pl.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    columns=["bgg_id", "name"],
)
game_data.shape


# %%
def game_name(bgg_id, base_data=game_data):
    return base_data.filter(pl.col("bgg_id") == int(bgg_id))["name"][0]


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
_, y_pred_train_lr, y_pred_test_lr = weights_and_predictions(
    "linear",
    X_train,
    y_train,
    X_test,
)
y_pred_lr = np.concatenate((y_pred_train_lr, y_pred_test_lr))
y_pred_lr.shape

# %%
ax = plot_ratings(data, game, y_pred_lr)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_lr.png")
plt.show()

# %% [markdown]
# ## Ridge Regression

# %%
_, y_pred_train_ridge, y_pred_test_ridge = weights_and_predictions(
    "ridge",
    X_train,
    y_train,
    X_test,
)
y_pred_ridge = np.concatenate((y_pred_train_ridge, y_pred_test_ridge))
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
weights_slsqp, y_pred_train_slsqp, y_pred_test_slsqp = weights_and_predictions(
    "slsqp",
    X_train,
    y_train,
    X_test,
)
y_pred_slsqp = np.concatenate((y_pred_train_slsqp, y_pred_test_slsqp))
weights_slsqp.shape, y_pred_slsqp.shape

# %%
print(
    "\n+ ".join(
        f"{weight:.3} * <{game_name(bgg_id)} ({bgg_id})>"
        for weight, bgg_id in sorted(zip(weights_slsqp, control_ids), reverse=True)
        if weight >= 0.001
    )
)

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


# %% [markdown]
# ## Fisher's Exact Test

# %%
def process_control(
    bgg_id,
    original_game=game,
    data_train=data_train,
    data_test=data_test,
):
    control_game = replace(
        original_game,
        bgg_id=bgg_id,
        name=game_name(bgg_id),
    )

    y_pred_train_control, y_pred_test_control = sample_control_and_predict(
        "slsqp",
        control_game,
        data_train,
        data_test,
    )

    effect_train = data_train[str(control_game.bgg_id)] - y_pred_train_control
    effect_test = data_test[str(control_game.bgg_id)] - y_pred_test_control
    train_error = np.sqrt((effect_train**2).mean())

    return (
        control_game,
        y_pred_train_control,
        y_pred_test_control,
        effect_train,
        effect_test,
        train_error,
    )


# %%
parallel_fn = delayed(process_control)
jobs = (
    parallel_fn(bgg_id)
    for bgg_id in np.random.choice(
        control_ids,
        min(128, len(control_ids)),
        replace=False,
    )
)
control_game_results = Parallel(n_jobs=-1, return_as="generator")(jobs)

# %%
_, ax = plt.subplots()
for control_game, _, _, effect_train, effect_test, train_error in control_game_results:
    if train_error > 3:
        print(f"Ignore <{control_game.name}> with RMSE of {train_error:.3f}")
        continue
    effect = np.concatenate((effect_train, effect_test))
    # TODO count smaller and larger effects
    sns.lineplot(
        x=data["timestamp"],
        y=effect,
        label=None,
        color="pink",
        lw=2,
        alpha=0.4,
        ax=ax,
    )
plot_effect(data, game, y_pred_slsqp, ax=ax)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp_fisher.png")
plt.show()
