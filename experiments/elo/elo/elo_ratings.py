from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from typing import Any


def elo_probability(diff: float, scale: float = 400) -> float:
    return 1 / (1 + 10 ** (-diff / scale))


def calculate_elo_ratings[ID_TYPE](
    *,
    player_1_ids: Iterable[ID_TYPE],
    player_2_ids: Iterable[ID_TYPE],
    player_1_outcomes: Iterable[float],
    init_elo_ratings: Mapping[ID_TYPE, float] | None = None,
    elo_initial: float = 0,
    elo_k: float = 32,
    elo_scale: float = 400,
    full_results: bool = False,
    progress_bar: bool = False,
) -> (
    defaultdict[ID_TYPE, float]
    | tuple[defaultdict[ID_TYPE, float], list[float], list[float]]
):
    elo_ratings = defaultdict(
        lambda: elo_initial,
        init_elo_ratings if init_elo_ratings is not None else {},
    )

    player_1_win_probs: list[float] = []
    elo_updates: list[float] = []

    if progress_bar:
        from tqdm import tqdm

        player_1_ids = tqdm(player_1_ids, desc="Processing games")

    for player_1_id, player_2_id, player_1_outcome in zip(
        player_1_ids,
        player_2_ids,
        player_1_outcomes,
        strict=True,
    ):
        elo_1 = elo_ratings[player_1_id]
        elo_2 = elo_ratings[player_2_id]

        diff = elo_1 - elo_2
        player_1_win_prob = elo_probability(diff, elo_scale)
        player_1_update = elo_k * (player_1_outcome - player_1_win_prob)

        # Update ratings
        elo_ratings[player_1_id] += player_1_update
        elo_ratings[player_2_id] -= player_1_update

        if full_results:
            player_1_win_probs.append(player_1_win_prob)
            elo_updates.append(player_1_update)

    if full_results:
        return elo_ratings, player_1_win_probs, elo_updates
    return elo_ratings


class EloRatingSystem[ID_TYPE]:
    elo_initial: float = 0
    elo_k: float = 32
    elo_scale: float = 400

    elo_ratings: defaultdict[ID_TYPE, float]

    def __init__(
        self,
        *,
        init_elo_ratings: Mapping[ID_TYPE, float] | None = None,
        elo_initial: float = 0,
        elo_k: float = 32,
        elo_scale: float = 400,
    ) -> None:
        self.elo_initial = elo_initial
        self.elo_k = elo_k
        self.elo_scale = elo_scale

        self.elo_ratings = defaultdict(
            lambda: elo_initial,
            init_elo_ratings if init_elo_ratings is not None else {},
        )

    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, float] | Iterable[ID_TYPE],
    ) -> np.ndarray:
        raise NotImplementedError

    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> np.ndarray | None:
        raise NotImplementedError

    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> np.ndarray:
        raise NotImplementedError

    def expected_outcome(
        self,
        players: Iterable[ID_TYPE],
        *,
        rank_payoffs: np.ndarray | None = None,
    ) -> np.ndarray:
        raise NotImplementedError
