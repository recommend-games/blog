# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
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
from matplotlib import pyplot as plt
from tqdm import tqdm

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
# TODO: Use numpy random number generator with seed everywhere.

# %%
game = REVIEWS[0]
game = replace(game, days_before=90, days_after=60)
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
    pl.scan_csv("num_collections.csv")
    .select(
        pl.col("day").str.to_datetime().alias("timestamp"),
        pl.exclude("day").cast(int),
    )
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
plt.savefig(plot_dir / f"{game.bgg_id}_num_ratings.svg")
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
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_lr.svg")
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
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_ridge.svg")
plt.show()

# %%
plot_effect(data, game, y_pred_ridge)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_ridge.png")
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_ridge.svg")
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
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_slsqp.svg")
plt.show()

# %%
plot_effect(data, game, y_pred_slsqp)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp.png")
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp.svg")
plt.show()

# %%
ratings_train = data_train[str(game.bgg_id)][-1]
ratings_test = data_test[str(game.bgg_id)][-1]
susd_effect = ratings_test - y_pred_slsqp[-1]
new_ratings = ratings_test - ratings_train
pct_new_ratings = susd_effect / new_ratings
print(
    f"SU&SD effect: additional {int(susd_effect)} ratings, {pct_new_ratings:.1%} of all new ratings"
)


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
control_bgg_ids = np.random.choice(
    control_ids,
    min(128, len(control_ids)),
    replace=False,
)
control_game_results = (process_control(bgg_id) for bgg_id in control_bgg_ids)

# %%
larger_effect = 0
smaller_effect = 0

_, ax = plt.subplots()
for control_game, _, _, effect_train, effect_test, train_error in tqdm(
    control_game_results,
    total=len(control_bgg_ids),
):
    if train_error > 3:
        print(f"Ignore <{control_game.name}> with RMSE of {train_error:.3f}")
        continue

    effect = np.concatenate((effect_train, effect_test))
    if effect_test[-1] >= susd_effect:
        larger_effect += 1
    else:
        smaller_effect += 1

    sns.lineplot(
        x=data["timestamp"],
        y=effect,
        label=None,
        color="pink",
        lw=2,
        alpha=0.4,
        ax=ax,
    )

total_control = smaller_effect + larger_effect
print(
    f"{larger_effect} out of {total_control} ({larger_effect / total_control:.1%}) have a larger effect"
)
plot_effect(data, game, y_pred_slsqp, ax=ax)
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp_fisher.png")
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp_fisher.svg")
plt.show()
