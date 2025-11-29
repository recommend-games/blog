from __future__ import annotations

from collections.abc import Mapping
import functools
from typing import TYPE_CHECKING

import numpy as np
from numpy import typing as npt
from scipy.optimize import minimize_scalar

from elo._rust import approx_optimal_k_rust
from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo
from elo.utils import matches_to_arrays

if TYPE_CHECKING:
    from collections.abc import Iterable


def _calculate_loss[ID_TYPE](
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
    per_match_mse = np.nanmean(errors**2, axis=1, dtype=np.float64)
    return np.mean(per_match_mse, dtype=np.float64)


def approximate_optimal_k_python[ID_TYPE](
    *,
    matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    two_player_only: bool = False,
    min_elo_k: float = 0,
    max_elo_k: float = 200,
    elo_scale: float = 400,
    max_iterations: int | None = None,
    x_absolute_tol: float | None = None,
) -> np.float64:
    match_list: list[Mapping[ID_TYPE, float]] = [
        dict(zip((m := tuple(match)), range(len(m) - 1, -1, -1)))
        if not isinstance(match, Mapping)
        else match
        for match in matches
    ]

    @functools.cache
    def _loss(elo_k: float) -> np.float64:
        elo: EloRatingSystem[ID_TYPE] = (
            TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
            if two_player_only
            else RankOrderedLogitElo(elo_k=elo_k, elo_scale=elo_scale)
        )

        return _calculate_loss(
            elo=elo,
            matches=match_list,
            progress_bar=False,
        )

    options: dict[str, float | int] = {}
    if max_iterations is not None:
        options["maxiter"] = max_iterations
    if x_absolute_tol is not None:
        options["xatol"] = x_absolute_tol

    result = minimize_scalar(  # type: ignore[call-overload]
        fun=_loss,
        method="bounded",
        bounds=(min_elo_k, max_elo_k),
        options=options,
    )

    return result.x


def approximate_optimal_k[ID_TYPE](
    *,
    matches: Iterable[Mapping[ID_TYPE, float]]
    | Iterable[Iterable[ID_TYPE]]
    | npt.NDArray[np.int64],
    two_player_only: bool = False,
    min_elo_k: float = 0,
    max_elo_k: float = 200,
    elo_scale: float = 400,
    max_iterations: int | None = None,
    x_absolute_tol: float | None = None,
    python: bool = False,
) -> np.float64:
    if python:
        return approximate_optimal_k_python(
            matches=matches,
            two_player_only=two_player_only,
            min_elo_k=min_elo_k,
            max_elo_k=max_elo_k,
            elo_scale=elo_scale,
            max_iterations=max_iterations,
            x_absolute_tol=x_absolute_tol,
        )

    players_array, payoffs_array, row_splits_array, _ = matches_to_arrays(matches)
    return approx_optimal_k_rust(
        players=players_array,
        payoffs=payoffs_array,
        row_splits=row_splits_array,
        two_player_only=two_player_only,
        min_elo_k=min_elo_k,
        max_elo_k=max_elo_k,
        elo_scale=elo_scale,
        max_iterations=max_iterations,
        x_absolute_tol=x_absolute_tol,
    )
