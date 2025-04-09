from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

import numpy as np
from scipy.optimize import minimize_scalar

from elo.elo_ratings import calculate_elo_ratings


ID_TYPE = TypeVar("ID_TYPE")


def calculate_loss(
    *,
    player_1_ids: Iterable[ID_TYPE],
    player_2_ids: Iterable[ID_TYPE],
    player_1_outcomes: Iterable[float],
    elo_k: float,
    elo_scale: float,
    progress_bar: bool = False,
) -> np.float64:
    if not isinstance(player_1_outcomes, np.ndarray):
        player_1_outcomes = np.array(list(player_1_outcomes))

    _, player_1_win_probs_list, _ = calculate_elo_ratings(
        player_1_ids=player_1_ids,
        player_2_ids=player_2_ids,
        player_1_outcomes=player_1_outcomes,
        elo_k=elo_k,
        elo_scale=elo_scale,
        full_results=True,
        progress_bar=progress_bar,
    )

    player_1_win_probs = np.array(player_1_win_probs_list)
    errors = player_1_outcomes - player_1_win_probs

    return np.mean(errors**2)


def approximate_optimal_k(
    *,
    player_1_ids: Iterable[ID_TYPE],
    player_2_ids: Iterable[ID_TYPE],
    player_1_outcomes: Iterable[float],
    min_elo_k: float = 0,
    max_elo_k: float = 160,
    elo_scale: float = 400,
) -> np.float64:
    player_1_ids = list(player_1_ids)
    player_2_ids = list(player_2_ids)
    player_1_outcomes = np.array(list(player_1_outcomes))

    def loss(elo_k: float) -> np.float64:
        return calculate_loss(
            player_1_ids=player_1_ids,
            player_2_ids=player_2_ids,
            player_1_outcomes=player_1_outcomes,
            elo_k=elo_k,
            elo_scale=elo_scale,
        )

    result = minimize_scalar(
        fun=loss,
        method="bounded",
        bounds=(min_elo_k, max_elo_k),
    )

    return result.x
