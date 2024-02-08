import logging
import math
import os
from datetime import timedelta
from typing import Optional

import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from synthetic_control.data import GameData, GameResult
from synthetic_control.models import (
    sample_control_group,
    train_test_split,
    weights_and_predictions,
)

sns.set_style("dark")

LOGGER = logging.getLogger(__name__)


def plot_ratings(
    data: pl.DataFrame,
    game: GameData,
    y_pred: Optional[np.ndarray] = None,
    *,
    y_label: str = "Num Ratings",
    ax: Optional[Axes] = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots()

    sns.lineplot(
        x=data["timestamp"],
        y=data[str(game.bgg_id)],
        label=game.name,
        color="purple",
        lw=3,
        ax=ax,
    )

    if y_pred is not None:
        sns.lineplot(
            x=data["timestamp"],
            y=y_pred,
            label="Synthetic Control",
            color="crimson",
            lw=3,
            ax=ax,
        )
        y_pred_min = y_pred.min()
        y_pred_max = y_pred.max()

    else:
        y_pred_min = math.inf
        y_pred_max = -math.inf

    ax.vlines(
        x=game.date_review,
        ymin=min(data[str(game.bgg_id)].min(), y_pred_min),
        ymax=max(data[str(game.bgg_id)].max(), y_pred_max),
        label="SU&SD video",
        linestyle=":",
        color="purple",
        lw=2,
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_xlabel(None)
    ax.set_ylabel(y_label)
    ax.set_title(None)
    ax.legend()

    return ax


def plot_effect(
    data: pl.DataFrame,
    game: GameData,
    y_pred: np.ndarray,
    *,
    y_label: str = "Additional Ratings",
    ax: Optional[Axes] = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots()

    effect = data[str(game.bgg_id)] - y_pred

    ax.hlines(
        y=0,
        xmin=data["timestamp"].min(),
        xmax=data["timestamp"].max(),
        label=None,
        color="purple",
        lw=2,
    )

    sns.lineplot(
        x=data["timestamp"],
        y=effect,
        label="SU&SD effect",
        color="crimson",
        lw=3,
        ax=ax,
    )

    plt.vlines(
        x=game.date_review,
        ymin=effect.min(),
        ymax=effect.max(),
        label="SU&SD video",
        linestyle=":",
        color="purple",
        lw=2,
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    ax.set_xlabel(None)
    ax.set_ylabel(y_label)
    ax.set_title(None)
    ax.legend()

    return ax


def process_game(
    rating_data: pl.DataFrame | pl.LazyFrame,
    game: GameData,
    plot_dir: Optional[os.PathLike] = None,
    threshold_rmse_slsqp: float = 0.05,
    y_label: str = "Num Ratings",
) -> GameResult:
    data = (
        rating_data.lazy()
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

    data_train, data_test = train_test_split(data, game)

    control_ids = sample_control_group(data_train, game)

    X_train = data_train.select(*control_ids).to_numpy()
    y_train = data_train.select(str(game.bgg_id)).to_numpy().reshape(-1)
    X_test = data_test.select(*control_ids).to_numpy()
    y_test = data_test.select(str(game.bgg_id)).to_numpy().reshape(-1)

    weights, y_pred_train, y_pred_test = weights_and_predictions(
        model="slsqp",
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
    )

    effect_train = y_train - y_pred_train
    train_error = np.sqrt((effect_train**2).mean()) / y_train.mean()

    if train_error > threshold_rmse_slsqp:
        LOGGER.info(
            "RMSE for train data is %.3f, using ridge regression instead",
            train_error,
        )
        weights, y_pred_train, y_pred_test = weights_and_predictions(
            model="ridge",
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
        )
        method = "ridge"
    else:
        method = "slsqp"

    y_pred = np.concatenate((y_pred_train, y_pred_test))

    model_str = "\n+ ".join(
        f"{weight:.3} * <{bgg_id}>"
        for weight, bgg_id in sorted(
            sorted(zip(weights, control_ids), key=lambda x: -abs(x[0]))[:10],
            reverse=True,
        )
        if abs(weight) >= 0.001
    )

    ratings_train = y_train[-1]
    ratings_test = y_test[-1]
    susd_effect = ratings_test - y_pred[-1]
    new_ratings = ratings_test - ratings_train
    pct_new_ratings = susd_effect / new_ratings

    if plot_dir is None:
        plot_path = None
    else:
        plot_path = plot_dir / f"{game.bgg_id}_synthetic_control.svg"
        plot_ratings(data, game, y_pred, y_label=y_label)
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

    return GameResult(
        game_data=game,
        num_ratings_before_review=ratings_train,
        new_ratings=int(new_ratings),
        new_ratings_predicted=int(y_pred[-1] - ratings_train),
        susd_effect=int(susd_effect),
        susd_effect_rel=pct_new_ratings,
        nrmse_slsqp=train_error,
        method=method,
        model=model_str,
        plot_path=plot_path,
    )
