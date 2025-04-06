from __future__ import annotations
from collections.abc import Iterable
import numpy as np


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


def elo_probability(diff: float, scale: float = 400) -> float:
    return 1 / (1 + 10 ** (-diff / scale))


def update_elo_scores_p_deterministic(
    rng: np.random.Generator,
    elo_scores: np.ndarray,
    num_games: int,
    p_deterministic: float,
    elo_k: float = 32,
    elo_scale: float = 400,
    inplace: bool = True,
    progress_bar: bool = False,
) -> np.ndarray:
    assert elo_scores.ndim == 1
    num_players = len(elo_scores)

    if not inplace:
        elo_scores = np.copy(elo_scores)

    players_a, players_b, player_a_wins = simulate_p_deterministic_games(
        rng=rng,
        num_players=num_players,
        num_games=num_games,
        p_deterministic=p_deterministic,
    )

    if progress_bar:
        from tqdm import trange

        iterator: Iterable[int] = trange(num_games)

    else:
        iterator = range(num_games)

    for i in iterator:
        player_a = players_a[i]
        elo_a = elo_scores[player_a]
        player_b = players_b[i]
        elo_b = elo_scores[player_b]
        prob_a_wins = elo_probability(diff=elo_a - elo_b, scale=elo_scale)
        outcome_a_wins = player_a_wins[i]
        elo_update = elo_k * (outcome_a_wins - prob_a_wins)
        elo_scores[player_a] += elo_update
        elo_scores[player_b] -= elo_update

    return elo_scores
