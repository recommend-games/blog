from __future__ import annotations

from collections.abc import Mapping
import itertools
from typing import TYPE_CHECKING

import numpy as np
from numpy import typing as npt


if TYPE_CHECKING:
    from collections.abc import Iterable


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


def matches_to_arrays[ID_TYPE](
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
