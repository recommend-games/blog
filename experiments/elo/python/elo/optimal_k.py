from __future__ import annotations

from collections.abc import Mapping
import functools
import itertools
from typing import TYPE_CHECKING

import numpy as np
from numpy import typing as npt
from scipy.optimize import minimize_scalar

from elo._rust import approx_optimal_k_rust
from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo

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
    return np.nanmean(errors**2, dtype=np.float64)


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


def _match_mapping_to_lists[ID_TYPE](
    matches: Iterable[Mapping[ID_TYPE, float]],
) -> tuple[list[ID_TYPE], list[float], list[int]]:
    players: list[ID_TYPE] = []
    payoffs: list[float] = []
    row_splits: list[int] = [0]

    for match in matches:
        for player, payoff in match.items():
            players.append(player)
            payoffs.append(payoff)
        row_splits.append(len(players))

    return players, payoffs, row_splits


def _match_iterable_to_lists[ID_TYPE](
    matches: Iterable[Iterable[ID_TYPE]],
) -> tuple[list[ID_TYPE], list[int]]:
    players: list[ID_TYPE] = []
    row_splits: list[int] = [0]

    for match in matches:
        for player in match:
            players.append(player)
        row_splits.append(len(players))

    return players, row_splits


def _player_ids_to_ints[ID_TYPE](
    players: list[ID_TYPE],
) -> npt.NDArray[np.int64]:
    unique_players = tuple(frozenset(players))
    mapping = dict(zip(unique_players, range(len(unique_players))))
    return np.asarray([mapping[p] for p in players], dtype=np.int64)


def _matches_to_arrays[ID_TYPE](
    matches: Iterable[Mapping[ID_TYPE, float]]
    | Iterable[Iterable[ID_TYPE]]
    | npt.NDArray[np.int64],
) -> tuple[
    npt.NDArray[np.int64],
    npt.NDArray[np.float64] | None,
    npt.NDArray[np.int64],
]:
    if (
        isinstance(matches, np.ndarray)
        and matches.dtype in (np.int8, np.int16, np.int32, np.int64)
        and matches.ndim == 2
    ):
        return (
            matches.flatten().astype(np.int64),
            None,
            np.arange(0, matches.size + 1, matches.shape[1], dtype=np.int64),
        )

    matches_iter = iter(matches)
    first_match = next(matches_iter)
    if isinstance(first_match, Mapping):
        match_mappings: Iterable[Mapping[ID_TYPE, float]] = itertools.chain(
            (first_match,),
            matches_iter,  # type: ignore[arg-type]
        )
        players, payoffs, row_splits = _match_mapping_to_lists(match_mappings)
        payoffs_array = np.asarray(payoffs, dtype=np.float64)
    else:
        match_iterables: Iterable[Iterable[ID_TYPE]] = itertools.chain(
            (first_match,),
            matches_iter,
        )
        players, row_splits = _match_iterable_to_lists(match_iterables)
        payoffs_array = None

    players_array = _player_ids_to_ints(players)
    row_splits_array = np.asarray(row_splits, dtype=np.int64)

    return players_array, payoffs_array, row_splits_array


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

    players_array, payoffs_array, row_splits_array = _matches_to_arrays(matches)
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
