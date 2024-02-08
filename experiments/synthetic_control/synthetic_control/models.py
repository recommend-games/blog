from typing import Optional

import numpy as np
import polars as pl
from scipy.optimize import fmin_slsqp
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression, Ridge

from synthetic_control.data import GameData


def train_test_split(
    data: pl.DataFrame,
    game: GameData,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    data_train_test = data.with_columns(
        pl.when(pl.col("timestamp") < game.date_review)
        .then(pl.lit("train"))
        .otherwise(pl.lit("test"))
        .alias("train_test")
    ).partition_by("train_test", as_dict=True)

    return (
        data_train_test["train"].sort("timestamp"),
        data_train_test["test"].sort("timestamp"),
    )


def sample_control_group(
    data: pl.DataFrame,
    game: GameData,
    *,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    rng = np.random.default_rng() if rng is None else rng

    num_ratings_last = data[str(game.bgg_id)][-1]
    candidates = [
        s
        for s in data.select(pl.exclude("train_test", "timestamp", str(game.bgg_id)))
        if s.null_count() == 0 and 0 < s[-1] < 2 * num_ratings_last
    ]
    weights = np.array([1 - abs(1 - s[-1] / num_ratings_last) for s in candidates])
    return rng.choice(
        a=[s.name for s in candidates],
        size=min(game.max_control_games, len(candidates)),
        replace=False,
        p=weights / weights.sum(),
    )  # type: ignore


def train_weights_lr(
    X_train: np.ndarray,
    y_train: np.ndarray,
    model: Optional[BaseEstimator] = None,
) -> np.ndarray:
    if model is None:
        model = LinearRegression(fit_intercept=False)

    return model.fit(X_train, y_train).coef_


def train_weights_slsqp(X_train: np.ndarray, y_train: np.ndarray) -> np.ndarray:
    def loss(weights):
        return np.sqrt(np.mean((y_train - X_train.dot(weights)) ** 2))

    weights_init = np.ones(X_train.shape[1]) / X_train.shape[1]

    return fmin_slsqp(
        func=loss,
        x0=weights_init,
        f_eqcons=lambda weights: np.sum(weights) - 1,
        bounds=[(0.0, 1.0)] * len(weights_init),
        disp=False,
    )


def weights_and_predictions(
    model: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    *,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # TODO: Use rng for training
    rng = np.random.default_rng() if rng is None else rng

    if model == "linear":
        weights = train_weights_lr(
            X_train,
            y_train,
            model=LinearRegression(fit_intercept=False),
        )
    elif model == "ridge":
        weights = train_weights_lr(
            X_train,
            y_train,
            model=Ridge(fit_intercept=False, alpha=100.0),
        )
    elif model == "slsqp":
        weights = train_weights_slsqp(X_train, y_train)
    else:
        raise ValueError(f"Unknown model: {model}")

    return weights, X_train.dot(weights), X_test.dot(weights)


def sample_control_and_predict(
    model: str,
    game: GameData,
    data_train: pl.DataFrame,
    data_test: pl.DataFrame,
    *,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng() if rng is None else rng

    control_ids = sample_control_group(
        data=data_train,
        game=game,
        rng=rng,
    )

    X_train = data_train.select(*control_ids).to_numpy()
    y_train = data_train[str(game.bgg_id)].to_numpy()
    X_test = data_test.select(*control_ids).to_numpy()

    _, y_pred_train, y_pred_test = weights_and_predictions(
        model,
        X_train,
        y_train,
        X_test,
    )

    return y_pred_train, y_pred_test
