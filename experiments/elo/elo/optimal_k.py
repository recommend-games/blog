from __future__ import annotations
from collections.abc import Iterable

import numpy as np

from elo.elo_ratings import calculate_elo_ratings

from typing import TypeVar

ID_TYPE = TypeVar("ID_TYPE")


def calculate_loss(
    *,
    player_1_ids: Iterable[ID_TYPE],
    player_2_ids: Iterable[ID_TYPE],
    player_1_outcomes: Iterable[float],
    elo_initial: float = 0,
    elo_k: float = 32,
    elo_scale: float = 400,
    progress_bar: bool = False,
) -> np.float64:
    player_1_outcomes = np.array(list(player_1_outcomes))

    _, player_1_win_probs_list, _ = calculate_elo_ratings(
        player_1_ids=player_1_ids,
        player_2_ids=player_2_ids,
        player_1_outcomes=player_1_outcomes,
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
        full_results=True,
        progress_bar=progress_bar,
    )

    player_1_win_probs = np.array(player_1_win_probs_list)
    errors = player_1_outcomes - player_1_win_probs

    return np.mean(errors**2)
