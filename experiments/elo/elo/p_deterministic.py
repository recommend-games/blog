from __future__ import annotations
from collections import defaultdict
import numpy as np

from elo.elo_ratings import calculate_elo_ratings


def simulate_p_deterministic_matches(
    *,
    rng: np.random.Generator,
    num_players: int,
    num_matches: int,
    players_per_match: int = 2,
    p_deterministic: float,
) -> np.ndarray:
    assert 0 <= p_deterministic <= 1, "p_deterministic must be between 0 and 1"
    assert num_players > 1, "num_players must be greater than 1"
    assert num_matches > 0, "num_games must be greater than 0"
    assert 2 <= players_per_match <= num_players, (
        "players_per_match must be between 2 and num_players"
    )

    players = np.arange(num_players)
    random_outcomes = np.array(
        [
            rng.choice(
                players,
                size=players_per_match,
                replace=False,
            )
            for _ in range(num_matches)
        ]
    )

    if p_deterministic == 0:
        return random_outcomes

    deterministic_outcomes = np.sort(random_outcomes, axis=1)

    if p_deterministic == 1:
        return deterministic_outcomes

    mask = rng.random(size=num_matches) < p_deterministic
    return np.where(mask[:, np.newaxis], deterministic_outcomes, random_outcomes)


def update_elo_ratings_p_deterministic(
    rng: np.random.Generator,
    elo_ratings: np.ndarray,
    num_games: int,
    p_deterministic: float,
    elo_initial: float = 0,
    elo_k: float = 32,
    elo_scale: float = 400,
    inplace: bool = True,
    progress_bar: bool = False,
) -> np.ndarray:
    assert elo_ratings.ndim == 1
    num_players = len(elo_ratings)

    if not inplace:
        elo_ratings = np.copy(elo_ratings)

    players_a, players_b, player_a_wins = simulate_p_deterministic_matches(
        rng=rng,
        num_players=num_players,
        num_matches=num_games,
        p_deterministic=p_deterministic,
    )

    results = calculate_elo_ratings(
        player_1_ids=players_a,
        player_2_ids=players_b,
        player_1_outcomes=player_a_wins,
        init_elo_ratings=dict(enumerate(elo_ratings)),
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
        full_results=False,
        progress_bar=progress_bar,
    )

    assert isinstance(results, defaultdict)

    for player_id, elo_rating in results.items():
        elo_ratings[player_id] = elo_rating

    return elo_ratings
