from __future__ import annotations
import numpy as np

from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo


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
    *,
    rng: np.random.Generator,
    elo: EloRatingSystem | None = None,
    num_players: int,
    num_matches: int,
    players_per_match: int = 2,
    p_deterministic: float,
    progress_bar: bool = False,
) -> EloRatingSystem:
    if elo is None:
        elo = TwoPlayerElo() if players_per_match == 2 else RankOrderedLogitElo()

    matches = simulate_p_deterministic_matches(
        rng=rng,
        num_players=num_players,
        num_matches=num_matches,
        players_per_match=players_per_match,
        p_deterministic=p_deterministic,
    )

    payoffs = np.arange(players_per_match - 1, -1, -1, dtype=float)

    elo.update_elo_ratings_batch(
        matches=(dict(zip(match, payoffs)) for match in matches),
        full_results=False,
        progress_bar=progress_bar,
        tqdm_kwargs={"total": num_matches},
    )

    return elo
