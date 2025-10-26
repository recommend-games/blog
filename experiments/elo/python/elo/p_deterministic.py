from __future__ import annotations

import dataclasses
import itertools
import time
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import TYPE_CHECKING

import numpy as np

from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo
from elo.optimal_k import approximate_optimal_k

if TYPE_CHECKING:
    from collections.abc import Generator
    from concurrent.futures import Future


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


@dataclasses.dataclass(frozen=True, kw_only=True)
class ExperimentResult:
    num_players: int
    num_matches: int
    players_per_match: int

    p_deterministic: float
    elo_k: float
    elo_scale: float

    mean: float
    std_dev: float
    p00: float
    p01: float
    p25: float
    p50: float
    p75: float
    p99: float
    p100: float


def p_deterministic_experiment(
    *,
    rng: np.random.Generator,
    num_players: int,
    num_matches: int,
    players_per_match: int = 2,
    p_deterministic: float,
    elo_scale: float = 400,
    max_iterations: int | None = None,
    x_absolute_tol: float | None = None,
    progress_bar: bool = False,
) -> ExperimentResult:
    if p_deterministic < 0 or p_deterministic > 1:
        raise ValueError("p_deterministic must be between 0 and 1")

    if np.isclose(p_deterministic, 0.0):
        return ExperimentResult(
            num_players=num_players,
            num_matches=num_matches,
            players_per_match=players_per_match,
            p_deterministic=0.0,
            elo_k=0.0,
            elo_scale=elo_scale,
            mean=0.0,
            std_dev=0.0,
            p00=0.0,
            p01=0.0,
            p25=0.0,
            p50=0.0,
            p75=0.0,
            p99=0.0,
            p100=0.0,
        )

    if np.isclose(p_deterministic, 1.0):
        return ExperimentResult(
            num_players=num_players,
            num_matches=num_matches,
            players_per_match=players_per_match,
            p_deterministic=1.0,
            elo_k=float("inf"),
            elo_scale=elo_scale,
            mean=0.0,
            std_dev=float("inf"),
            p00=-float("inf"),
            p01=-float("inf"),
            p25=-float("inf"),
            p50=0.0,
            p75=float("inf"),
            p99=float("inf"),
            p100=float("inf"),
        )

    matches = simulate_p_deterministic_matches(
        rng=rng,
        num_players=num_players,
        num_matches=num_matches,
        players_per_match=players_per_match,
        p_deterministic=p_deterministic,
    )

    try:
        elo_k = approximate_optimal_k(
            matches=matches,
            two_player_only=players_per_match == 2,
            min_elo_k=0,
            max_elo_k=elo_scale / 2,
            elo_scale=elo_scale,
            max_iterations=max_iterations,
            x_absolute_tol=x_absolute_tol,
        )
    except Exception:
        return ExperimentResult(
            num_players=num_players,
            num_matches=num_matches,
            players_per_match=players_per_match,
            p_deterministic=p_deterministic,
            elo_k=float("nan"),
            elo_scale=elo_scale,
            mean=float("nan"),
            std_dev=float("nan"),
            p00=float("nan"),
            p01=float("nan"),
            p25=float("nan"),
            p50=float("nan"),
            p75=float("nan"),
            p99=float("nan"),
            p100=float("nan"),
        )

    elo = update_elo_ratings_p_deterministic(
        rng=rng,
        elo=TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
        if players_per_match == 2
        else RankOrderedLogitElo(elo_k=elo_k, elo_scale=elo_scale),
        num_players=num_players,
        num_matches=num_matches,
        players_per_match=players_per_match,
        p_deterministic=p_deterministic,
        progress_bar=progress_bar,
    )
    elo_ratings = np.array(list(elo.elo_ratings.values()))

    return ExperimentResult(
        num_players=num_players,
        num_matches=num_matches,
        players_per_match=players_per_match,
        p_deterministic=p_deterministic,
        elo_k=elo_k,
        elo_scale=elo_scale,
        mean=elo_ratings.mean(),
        std_dev=elo_ratings.std(),
        p00=elo_ratings.min(),
        p01=np.percentile(elo_ratings, 1),
        p25=np.percentile(elo_ratings, 25),
        p50=np.percentile(elo_ratings, 50),
        p75=np.percentile(elo_ratings, 75),
        p99=np.percentile(elo_ratings, 99),
        p100=elo_ratings.max(),
    )


def _make_iterable[T](value: T | Iterable[T]) -> Iterable[T]:
    return value if isinstance(value, Iterable) else (value,)


def _p_deterministic_experiment_futures(
    *,
    executor: ProcessPoolExecutor,
    seed: int,
    num_playerss: Iterable[int] | int,
    num_matchess: Iterable[int] | int,
    players_per_matchs: Iterable[int] | int,
    p_deterministics: Iterable[float] | float,
    elo_scales: Iterable[float] | float,
    max_iterations: int | None = None,
    x_absolute_tol: float | None = None,
) -> Generator[Future[ExperimentResult]]:
    for i, (
        num_players,
        num_matches,
        players_per_match,
        p_deterministic,
        elo_scale,
    ) in enumerate(
        itertools.product(
            _make_iterable(num_playerss),
            _make_iterable(num_matchess),
            _make_iterable(players_per_matchs),
            _make_iterable(p_deterministics),
            _make_iterable(elo_scales),
        )
    ):
        rng = np.random.default_rng(seed + i)
        yield executor.submit(
            p_deterministic_experiment,
            rng=rng,
            num_players=num_players,
            num_matches=num_matches,
            players_per_match=players_per_match,
            p_deterministic=p_deterministic,
            elo_scale=elo_scale,
            max_iterations=max_iterations,
            x_absolute_tol=x_absolute_tol,
            progress_bar=False,
        )


def p_deterministic_experiments(
    *,
    seed: int | None = None,
    num_players: Iterable[int] | int,
    num_matches: Iterable[int] | int,
    players_per_match: Iterable[int] | int = 2,
    p_deterministic: Iterable[float] | float,
    elo_scale: Iterable[float] | float = 400,
    max_iterations: int | None = None,
    x_absolute_tol: float | None = None,
) -> Generator[ExperimentResult]:
    with ProcessPoolExecutor() as executor:
        futures = _p_deterministic_experiment_futures(
            executor=executor,
            seed=seed or time.time_ns(),
            num_playerss=num_players,
            num_matchess=num_matches,
            players_per_matchs=players_per_match,
            p_deterministics=p_deterministic,
            elo_scales=elo_scale,
            max_iterations=max_iterations,
            x_absolute_tol=x_absolute_tol,
        )
        for future in as_completed(futures):
            yield future.result()
