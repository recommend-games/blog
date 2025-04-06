from __future__ import annotations
import numpy as np


def simulate_p_deterministic_games(
    rng: np.random.Generator,
    num_players: int,
    num_games: int,
    p_deterministic: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    players_a = rng.integers(low=0, high=num_players, size=num_games)
    # Sample offset for second player, ensuring it's not equal to the first
    offset = rng.integers(low=1, high=num_players, size=num_games)
    players_b = (players_a + offset) % num_players

    prob_player_a_wins = rng.random(size=num_games) < 0.5
    det_player_a_wins = players_a < players_b

    deterministic = rng.random(size=num_games) < p_deterministic
    player_a_wins = np.where(deterministic, det_player_a_wins, prob_player_a_wins)

    return players_a, players_b, player_a_wins
