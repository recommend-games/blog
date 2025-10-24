from __future__ import annotations

import itertools
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Mapping
from typing import TYPE_CHECKING, override

import numpy as np
from numpy import typing as npt

if TYPE_CHECKING:
    from collections.abc import Iterable, Generator
    from typing import Any


def elo_probability(diff: float, scale: float = 400) -> float:
    return 1 / (1 + 10 ** (-diff / scale))


class EloRatingSystem[ID_TYPE](ABC):
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

    @abstractmethod
    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, float] | Iterable[ID_TYPE],
    ) -> np.ndarray: ...

    @abstractmethod
    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> np.ndarray | None: ...

    @abstractmethod
    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> np.ndarray: ...

    @abstractmethod
    def expected_outcome(
        self,
        players: Iterable[ID_TYPE],
        *,
        rank_payoffs: np.ndarray | None = None,
    ) -> np.ndarray: ...


class TwoPlayerElo[ID_TYPE](EloRatingSystem[ID_TYPE]):
    @override
    def expected_outcome(
        self,
        players: Iterable[ID_TYPE],
        *,
        rank_payoffs: np.ndarray | None = None,
    ) -> np.ndarray:
        if rank_payoffs is not None:
            warnings.warn("rank_payoffs are ignored for two-player elo")

        player_1, player_2 = players
        elo_1 = self.elo_ratings[player_1]
        elo_2 = self.elo_ratings[player_2]
        diff = elo_1 - elo_2
        prob = elo_probability(diff, self.elo_scale)
        return np.array([prob, 1 - prob])

    @override
    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> np.ndarray:
        expected_outcome = self.expected_outcome(players)
        return np.array([expected_outcome, 1 - expected_outcome])

    @override
    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, float] | Iterable[ID_TYPE],
    ) -> np.ndarray:
        if isinstance(players, Mapping):
            player_ids = tuple(players.keys())
            outcomes = np.array(list(players.values()), dtype=float)
        else:
            player_ids = tuple(players)
            outcomes = np.array([1, 0], dtype=float)

        diffs = outcomes - self.expected_outcome(player_ids)
        for player_id, diff in zip(player_ids, diffs):
            self.elo_ratings[player_id] += self.elo_k * diff

        return diffs

    def _update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    ) -> Generator[np.ndarray]:
        for match in matches:
            yield self.update_elo_ratings(match)

    @override
    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> np.ndarray | None:
        if progress_bar:
            from tqdm import tqdm

            tqdm_kwargs = tqdm_kwargs or {}
            matches = tqdm(matches, desc="Updating elo ratings", **tqdm_kwargs)

        if full_results:
            return np.array(list(self._update_elo_ratings_batch(matches)))

        for _ in self._update_elo_ratings_batch(matches):
            pass
        return None


class RankOrderedLogitElo[ID_TYPE](EloRatingSystem[ID_TYPE]):
    """
    Rank-ordered-logit Elo with Monte-Carlo fallback for large fields.
    """

    def __init__(
        self,
        *,
        init_elo_ratings: Mapping[ID_TYPE, float] | None = None,
        elo_initial: float = 0,
        elo_k: float = 32,
        elo_scale: float = 400,
        max_exact: int = 6,
        mc_samples: int = 5_000,
    ) -> None:
        super().__init__(
            init_elo_ratings=init_elo_ratings,
            elo_initial=elo_initial,
            elo_k=elo_k,
            elo_scale=elo_scale,
        )

        self.max_exact = max_exact
        self.mc_samples = mc_samples

    def _calculate_probability_matrix_two_players(
        self,
        players: tuple[ID_TYPE, ID_TYPE],
    ) -> np.ndarray:
        rating_a = self.elo_ratings[players[0]]
        rating_b = self.elo_ratings[players[1]]
        diff = rating_a - rating_b
        prob_a = elo_probability(diff, self.elo_scale)
        prob_b = 1 - prob_a
        return np.array([[prob_a, prob_b], [prob_b, prob_a]])

    def _calculate_probability_matrix_from_simulations(
        self,
        players: tuple[ID_TYPE, ...],
    ) -> np.ndarray:
        # TODO: implement Monte Carlo fallback
        raise NotImplementedError

    def _calculate_probability_matrix_from_permutations(
        self,
        players: tuple[ID_TYPE, ...],
        rtol: float = 1e-3,
        atol: float = 1e-4,
    ) -> np.ndarray:
        num_players = len(players)
        ratings = np.array([self.elo_ratings[p] for p in players], dtype=float)
        exp_ratings = 10 ** (ratings / self.elo_scale)
        probs = np.zeros((num_players, num_players))

        for perm in itertools.permutations(range(num_players)):
            prob = 1
            denom = np.sum(exp_ratings)
            for i in range(num_players - 1):
                prob *= exp_ratings[perm[i]] / denom
                denom -= exp_ratings[perm[i]]
            for position, player in enumerate(perm):
                probs[player, position] += prob

        col_sum = probs.sum(axis=0, keepdims=True)
        row_sum = probs.sum(axis=1, keepdims=True)
        while not (
            np.allclose(col_sum, 1.0, rtol=rtol, atol=atol)
            and np.allclose(row_sum, 1.0, rtol=rtol, atol=atol)
        ):
            col_sum[col_sum == 0.0] = 1.0
            probs /= col_sum
            row_sum = probs.sum(axis=1, keepdims=True)
            row_sum[row_sum == 0.0] = 1.0
            probs /= row_sum
            col_sum = probs.sum(axis=0, keepdims=True)
            row_sum = probs.sum(axis=1, keepdims=True)

        # Robust checks for probability matrix
        assert np.all(np.isfinite(probs)), "Probability matrix has non-finite values"
        assert np.allclose(col_sum, 1.0, rtol=rtol, atol=atol), (
            f"Probabilities must sum to 1 over players per position (got {col_sum})"
        )
        assert np.allclose(row_sum, 1.0, rtol=rtol, atol=atol), (
            f"Probabilities must sum to 1 over positions per player (got {row_sum})"
        )

        return probs

    @override
    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> np.ndarray:
        players = tuple(players)

        if len(players) < 2:
            raise ValueError("At least 2 players are required")

        if len(players) == 2:
            return self._calculate_probability_matrix_two_players(players)

        if len(players) > self.max_exact:
            return self._calculate_probability_matrix_from_simulations(players)

        return self._calculate_probability_matrix_from_permutations(players)

    @override
    def expected_outcome(
        self,
        players: Iterable[ID_TYPE],
        *,
        rank_payoffs: np.ndarray | None = None,
    ) -> np.ndarray:
        players = tuple(players)
        if rank_payoffs is None:
            rank_payoffs = np.arange(len(players) - 1, -1, -1, dtype=float)

        assert rank_payoffs.ndim == 1, "Rank payoffs must be a 1D array"
        assert len(rank_payoffs) == len(players), (
            "Rank payoffs must be the same length as the number of players"
        )
        probs = self.probability_matrix(players)
        return probs @ rank_payoffs

    @override
    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, float] | Iterable[ID_TYPE],
    ) -> np.ndarray:
        if isinstance(players, Mapping):
            player_ids = tuple(players.keys())
            payoffs = np.array(list(players.values()), dtype=float)
        else:
            player_ids = tuple(players)
            payoffs = np.arange(len(player_ids) - 1, -1, -1, dtype=float)

        assert np.all(payoffs >= 0), "Payoffs must be non-negative"
        assert np.any(payoffs > 0), "At least one payoff must be positive"

        max_payoff = payoffs.max()
        expected_payoffs = self.expected_outcome(player_ids, rank_payoffs=payoffs)
        diffs = (payoffs - expected_payoffs) / max_payoff
        for player_id, diff in zip(player_ids, diffs):
            self.elo_ratings[player_id] += self.elo_k * diff

        return diffs

    def _update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    ) -> Generator[np.ndarray]:
        for match in matches:
            yield self.update_elo_ratings(match)

    @override
    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> np.ndarray | None:
        if progress_bar:
            from tqdm import tqdm

            tqdm_kwargs = tqdm_kwargs or {}
            matches = tqdm(matches, **tqdm_kwargs)

        if full_results:
            return _padded_numpy_array(self._update_elo_ratings_batch(matches))

        for _ in self._update_elo_ratings_batch(matches):
            pass
        return None


def _padded_numpy_array(
    arrays: Iterable[np.ndarray],
    *,
    pad_value: float = np.nan,
    dtype: np.dtype | None = None,
) -> np.ndarray:
    arrays = tuple(arrays)
    max_len = max((a.shape[0] for a in arrays), default=0)
    result = np.full((len(arrays), max_len), pad_value, dtype=dtype or np.float64)
    for i, a in enumerate(arrays):
        result[i, : a.shape[0]] = a
    return result


def calculate_elo_ratings_python(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: float = 0,
    elo_k: float = 32,
    elo_scale: float = 400,
    progress_bar: bool = False,
) -> dict[int, float]:
    assert matches.ndim == 2 and matches.shape[1] == 2, (
        "Matches must be a 2D array with shape (num_matches, 2)"
    )
    elo: TwoPlayerElo = TwoPlayerElo(
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
    )
    elo.update_elo_ratings_batch(matches, progress_bar=progress_bar)
    return dict(elo.elo_ratings)


def _main():
    from elo._rust import calculate_elo_ratings_rust

    matches = np.array([[0, 1], [0, 1]], dtype=np.int32)
    elo_initial = 0.0
    elo_k = 32.0
    elo_scale = 400.0

    print("Elo ratings (Python implementation):")
    elo_ratings = calculate_elo_ratings_python(
        matches=matches,
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
        progress_bar=True,
    )
    for player, rating in sorted(
        elo_ratings.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"Player {player:4d}:\tElo {rating:10.3f}")

    print("Elo ratings (Rust implementation):")
    elo_ratings_rust = calculate_elo_ratings_rust(
        matches=matches,
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
    )
    for player, rating in sorted(
        elo_ratings_rust.items(),
        key=lambda x: x[1],
        reverse=True,
    ):
        print(f"Player {player:4d}:\tElo {rating:10.3f}")


if __name__ == "__main__":
    _main()
