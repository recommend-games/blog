from __future__ import annotations

import functools
from collections.abc import Mapping
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar

from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo

if TYPE_CHECKING:
    from collections.abc import Iterable


def calculate_loss[ID_TYPE](
    *,
    elo: EloRatingSystem[ID_TYPE],
    matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    progress_bar: bool = False,
) -> np.float64:
    errors = elo.update_elo_ratings_batch(
        matches,
        full_results=True,
        progress_bar=progress_bar,
    )
    assert errors is not None
    return np.nanmean(errors**2)


def approximate_optimal_k[ID_TYPE](
    *,
    matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    two_player_only: bool = False,
    min_elo_k: float = 0,
    max_elo_k: float = 200,
    elo_scale: float = 400,
) -> np.float64:
    match_list: list[Mapping[ID_TYPE, float]] = [
        dict(zip((m := tuple(match)), range(len(m) - 1, -1, -1)))
        if not isinstance(match, Mapping)
        else match
        for match in matches
    ]

    @functools.cache
    def loss(elo_k: float) -> np.float64:
        return calculate_loss(
            elo=TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
            if two_player_only
            else RankOrderedLogitElo(elo_k=elo_k, elo_scale=elo_scale),
            matches=match_list,
            progress_bar=False,
        )

    result = minimize_scalar(
        fun=loss,
        method="bounded",
        bounds=(min_elo_k, max_elo_k),
    )

    return result.x
