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
from datetime import date, datetime, timedelta
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.optimize import fmin_slsqp
from sklearn.linear_model import LinearRegression, Ridge

from synthetic_control.data import REVIEWS

jupyter_black.load()
np.set_printoptions(suppress=True)
sns.set_style("dark")
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
ax = plt.subplot(1, 1, 1)
sns.lineplot(
    data=data,
    x="timestamp",
    y=str(game.bgg_id),
    ax=ax,
    label=game.name,
    lw=3,
)
plt.vlines(
    x=game.date_review,
    ymin=data[str(game.bgg_id)].min(),
    ymax=data[str(game.bgg_id)].max(),
    linestyle=":",
    lw=2,
    label="SU&SD video",
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
plt.xlabel(None)
plt.ylabel("Num ratings")
plt.title(None)
plt.legend()
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_num_ratings.png")
plt.show()

# %%
data_train_test = data.with_columns(
    pl.when(pl.col("timestamp") < game.date_review)
    .then(pl.lit("train"))
    .otherwise(pl.lit("test"))
    .alias("train_test")
).partition_by("train_test", as_dict=True)
data_train = data_train_test["train"].sort("timestamp")
data_test = data_train_test["test"].sort("timestamp")
data_train.shape, data_test.shape

# %%
num_ratings_last = data_train[str(game.bgg_id)][-1]
candidates = [
    s
    for s in data_train.select(pl.exclude("train_test", "timestamp", str(game.bgg_id)))
    if s.null_count() == 0 and 0 < s[-1] < 2 * num_ratings_last
]
weights = np.array([1 - abs(1 - s[-1] / num_ratings_last) for s in candidates])
control_ids = np.random.choice(
    a=[s.name for s in candidates],
    size=min(game.max_control_games, len(candidates)),
    replace=False,
    p=weights / weights.sum(),
)
len(candidates), len(control_ids)

# %%
X_train = data_train.select(*control_ids).to_numpy()
y_train = data_train.select(str(game.bgg_id)).to_numpy().reshape(-1)
X_test = data_test.select(*control_ids).to_numpy()
y_test = data_test.select(str(game.bgg_id)).to_numpy().reshape(-1)
X_train.shape, y_train.shape, X_test.shape, y_test.shape

# %% [markdown]
# ## Linear Regression

# %%
weights_lr = LinearRegression(fit_intercept=False).fit(X_train, y_train).coef_
weights_lr.round(3)

# %%
y_pred_lr = np.concatenate((X_train.dot(weights_lr), X_test.dot(weights_lr)))
y_pred_lr.shape

# %%
ax = plt.subplot(1, 1, 1)
sns.lineplot(
    data=data,
    x="timestamp",
    y=str(game.bgg_id),
    ax=ax,
    label=game.name,
    lw=3,
)
sns.lineplot(
    x=data["timestamp"],
    y=y_pred_lr,
    ax=ax,
    label="Synthetic Control",
    color="red",
    lw=3,
)
plt.vlines(
    x=game.date_review,
    ymin=data[str(game.bgg_id)].min(),
    ymax=data[str(game.bgg_id)].max(),
    linestyle=":",
    lw=2,
    label="SU&SD video",
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
plt.xlabel(None)
plt.ylabel("Num ratings")
plt.title(None)
plt.legend()
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_lr.png")
plt.show()

# %% [markdown]
# ## Ridge Regression

# %%
weights_ridge = Ridge(fit_intercept=False, alpha=100.0).fit(X_train, y_train).coef_
weights_ridge.round(3)

# %%
y_pred_ridge = np.concatenate((X_train.dot(weights_ridge), X_test.dot(weights_ridge)))
y_pred_ridge.shape

# %%
ax = plt.subplot(1, 1, 1)
sns.lineplot(
    data=data,
    x="timestamp",
    y=str(game.bgg_id),
    ax=ax,
    label=game.name,
    lw=3,
)
sns.lineplot(
    x=data["timestamp"],
    y=y_pred_ridge,
    ax=ax,
    label="Synthetic Control",
    color="red",
    lw=3,
)
plt.vlines(
    x=game.date_review,
    ymin=data[str(game.bgg_id)].min(),
    ymax=data[str(game.bgg_id)].max(),
    linestyle=":",
    lw=2,
    label="SU&SD video",
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
plt.xlabel(None)
plt.ylabel("Num ratings")
plt.title(None)
plt.legend()
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_ridge.png")
plt.show()

# %%
ax = plt.subplot(1, 1, 1)
effect_ridge = data[str(game.bgg_id)] - y_pred_ridge
plt.hlines(
    y=0,
    xmin=data["timestamp"].min(),
    xmax=data["timestamp"].max(),
    lw=2,
    label=None,
)
sns.lineplot(
    x=data["timestamp"],
    y=effect_ridge,
    ax=ax,
    label="SU&SD effect",
    color="red",
    lw=3,
)
plt.vlines(
    x=game.date_review,
    ymin=effect_ridge.min(),
    ymax=effect_ridge.max(),
    linestyle=":",
    lw=2,
    label="SU&SD video",
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
plt.xlabel(None)
plt.ylabel("Additional ratings")
plt.title(None)
plt.legend()
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_ridge.png")
plt.show()


# %% [markdown]
# ## Convex combination

# %%
def get_weights(X, y):
    def loss_weights(W):
        return np.sqrt(np.mean((y - X.dot(W)) ** 2))

    w_start = np.ones(X.shape[1]) / X.shape[1]

    return fmin_slsqp(
        loss_weights,
        w_start,
        f_eqcons=lambda x: np.sum(x) - 1,
        bounds=[(0.0, 1.0)] * len(w_start),
        disp=False,
    )


# %%
weights_slsqp = get_weights(X_train, y_train)
print("Sum:", weights_slsqp.sum())
np.round(weights_slsqp, 3)

# %%
{
    bgg_id: weight
    for bgg_id, weight in zip(control_ids, weights_slsqp)
    if weight >= 0.001
}

# %%
y_pred_slsqp = np.concatenate((X_train.dot(weights_slsqp), X_test.dot(weights_slsqp)))
y_pred_slsqp.shape

# %%
ax = plt.subplot(1, 1, 1)
sns.lineplot(
    data=data,
    x="timestamp",
    y=str(game.bgg_id),
    ax=ax,
    label=game.name,
    lw=3,
)
sns.lineplot(
    x=data["timestamp"],
    y=y_pred_slsqp,
    ax=ax,
    label="Synthetic Control",
    color="red",
    lw=3,
)
plt.vlines(
    x=game.date_review,
    ymin=data[str(game.bgg_id)].min(),
    ymax=data[str(game.bgg_id)].max(),
    linestyle=":",
    lw=2,
    label="SU&SD video",
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
plt.xlabel(None)
plt.ylabel("Num ratings")
plt.title(None)
plt.legend()
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_slsqp.png")
plt.show()

# %%
ax = plt.subplot(1, 1, 1)
effect_slsqp = data[str(game.bgg_id)] - y_pred_slsqp
plt.hlines(
    y=0,
    xmin=data["timestamp"].min(),
    xmax=data["timestamp"].max(),
    lw=2,
    label=None,
)
sns.lineplot(
    x=data["timestamp"],
    y=effect_slsqp,
    ax=ax,
    label="SU&SD effect",
    color="red",
    lw=3,
)
plt.vlines(
    x=game.date_review,
    ymin=effect_slsqp.min(),
    ymax=effect_slsqp.max(),
    linestyle=":",
    lw=2,
    label="SU&SD video",
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
plt.xlabel(None)
plt.ylabel("Additional ratings")
plt.title(None)
plt.legend()
plt.tight_layout()
plt.savefig(plot_dir / f"{game.bgg_id}_susd_effect_slsqp.png")
plt.show()
