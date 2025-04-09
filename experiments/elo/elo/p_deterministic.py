from __future__ import annotations
from collections import defaultdict
import numpy as np

from elo.elo_ratings import calculate_elo_ratings


def simulate_p_deterministic_games(
    rng: np.random.Generator,
    num_players: int,
    num_games: int,
    p_deterministic: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    assert 0 <= p_deterministic <= 1, "p_deterministic must be between 0 and 1"
    assert num_players > 1, "num_players must be greater than 1"
    assert num_games > 0, "num_games must be greater than 0"

    players_a = rng.integers(low=0, high=num_players, size=num_games)
    # Sample offset for second player, ensuring it's not equal to the first
    offset = rng.integers(low=1, high=num_players, size=num_games)
    players_b = (players_a + offset) % num_players
    assert np.all(players_a != players_b), "Players A and B must be different"

    if p_deterministic == 0:
        # If p_deterministic is 0, all games are probabilistic
        return players_a, players_b, rng.random(size=num_games) < 0.5

    if p_deterministic == 1:
        # If p_deterministic is 1, all games are deterministic
        return players_a, players_b, players_a < players_b

    # Otherwise, mix deterministic and probabilistic outcomes
    prob_player_a_wins = rng.random(size=num_games) < 0.5
    det_player_a_wins = players_a < players_b

    deterministic = rng.random(size=num_games) < p_deterministic
    player_a_wins = np.where(deterministic, det_player_a_wins, prob_player_a_wins)

    return players_a, players_b, player_a_wins


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

    players_a, players_b, player_a_wins = simulate_p_deterministic_games(
        rng=rng,
        num_players=num_players,
        num_games=num_games,
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
