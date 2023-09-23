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
import warnings
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.optimize import fmin_slsqp
from sklearn.linear_model import LinearRegression

jupyter_black.load()
np.set_printoptions(suppress=True)
sns.set_style("dark")
warnings.filterwarnings("ignore")


# %%
@dataclass(frozen=True, kw_only=True)
class GameData:
    bgg_id: int
    name: str
    date_review: date | datetime
    days_before: int = 90
    days_after: int = 60
    max_control_games: int = 100


# %%
game = GameData(
    bgg_id=311031,
    name="Five Three Five",
    date_review=date(2023, 8, 23),
    max_control_games=1000,
)
game

# %%
plot_dir = (Path(".") / "plots").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
plot_dir

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
plt.savefig(plot_dir / f"{game.bgg_id}_num_ratings.png")
plt.show()

# %%
num_ratings_first = data[str(game.bgg_id)][0]
candidates = [
    s.name
    for s in data.select(pl.exclude("timestamp", str(game.bgg_id)))
    if s.null_count() == 0
    and 0.5 * num_ratings_first <= s[0] <= 1.5 * num_ratings_first
]
control_ids = np.random.choice(
    a=candidates,
    size=min(game.max_control_games, len(candidates)),
    replace=False,
)
len(candidates), len(control_ids)

# %%
data_train_test = data.with_columns(
    pl.when(pl.col("timestamp") < game.date_review)
    .then(pl.lit("train"))
    .otherwise(pl.lit("test"))
    .alias("train_test")
).partition_by("train_test", as_dict=True)
data_train = data_train_test["train"].sort("timestamp")
X_train = data_train.select(*control_ids).to_numpy()
y_train = data_train.select(str(game.bgg_id)).to_numpy().reshape(-1)
data_test = data_train_test["test"].sort("timestamp")
X_test = data_test.select(*control_ids).to_numpy()
y_test = data_test.select(str(game.bgg_id)).to_numpy().reshape(-1)
data_train.shape, X_train.shape, y_train.shape, data_test.shape, X_test.shape, y_test.shape

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
)
sns.lineplot(
    x=data["timestamp"],
    y=y_pred_lr,
    ax=ax,
    label="Synthetic Control",
    color="red",
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
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_lr.png")
plt.show()


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
)
sns.lineplot(
    x=data["timestamp"],
    y=y_pred_slsqp,
    ax=ax,
    label="Synthetic Control",
    color="red",
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
plt.savefig(plot_dir / f"{game.bgg_id}_synthetic_control_slsqp.png")
plt.show()
