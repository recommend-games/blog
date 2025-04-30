from __future__ import annotations

from collections import defaultdict
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

ID_TYPE = TypeVar("ID_TYPE")


def elo_probability(diff: float, scale: float = 400) -> float:
    return 1 / (1 + 10 ** (-diff / scale))


def calculate_elo_ratings(
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
