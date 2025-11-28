from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Mapping
from typing import TYPE_CHECKING, override

import numpy as np
from numpy import typing as npt
from scipy.special import comb

if TYPE_CHECKING:
    from collections.abc import Iterable, Generator
    from typing import Any

NP_ZERO = np.float64(0.0)
NP_ONE = np.float64(1.0)
NP_TEN = np.float64(10.0)
NP_THIRTYTWO = np.float64(32.0)
NP_FOURHUNDRED = np.float64(400.0)


def elo_probability(
    diff: np.float64 | float,
    scale: np.float64 | float = NP_FOURHUNDRED,
) -> np.float64:
    return NP_ONE / (NP_ONE + np.power(NP_TEN, -np.float64(diff) / np.float64(scale)))


class EloRatingSystem[ID_TYPE](ABC):
    elo_initial: np.float64 = NP_ZERO
    elo_k: np.float64 = NP_THIRTYTWO
    elo_scale: np.float64 = NP_FOURHUNDRED

    elo_ratings: defaultdict[ID_TYPE, np.float64]

    def __init__(
        self,
        *,
        init_elo_ratings: Mapping[ID_TYPE, np.float64 | float] | None = None,
        elo_initial: np.float64 | float = NP_ZERO,
        elo_k: np.float64 | float = NP_THIRTYTWO,
        elo_scale: np.float64 | float = NP_FOURHUNDRED,
    ) -> None:
        self.elo_initial = np.float64(elo_initial)
        self.elo_k = np.float64(elo_k)
        self.elo_scale = np.float64(elo_scale)

        init_elo_ratings_converted: dict[ID_TYPE, np.float64] = (
            {k: np.float64(v) for k, v in init_elo_ratings.items()}
            if init_elo_ratings
            else {}
        )
        self.elo_ratings = defaultdict(
            lambda: self.elo_initial,
            init_elo_ratings_converted,
        )

    @abstractmethod
    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]: ...

    @abstractmethod
    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> npt.NDArray[np.float64] | None: ...

    @abstractmethod
    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]: ...

    @abstractmethod
    def expected_outcome(
        self,
        players: Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]: ...


class TwoPlayerElo[ID_TYPE](EloRatingSystem[ID_TYPE]):
    @override
    def expected_outcome(self, players: Iterable[ID_TYPE]) -> npt.NDArray[np.float64]:
        player_1, player_2 = players
        elo_1 = self.elo_ratings[player_1]
        elo_2 = self.elo_ratings[player_2]
        diff = elo_1 - elo_2
        prob = elo_probability(diff, self.elo_scale)
        return np.asarray([prob, 1 - prob], dtype=np.float64)

    @override
    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]:
        expected_outcome = self.expected_outcome(players)
        return np.asarray([expected_outcome, 1 - expected_outcome], dtype=np.float64)

    @override
    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]:
        if isinstance(players, Mapping):
            player_ids = tuple(players.keys())
            actual_outcome = np.asarray(list(players.values()), dtype=np.float64)
            assert np.all(actual_outcome >= 0), "Outcomes must be non-negative"
            assert np.any(actual_outcome > 0), "At least one outcome must be positive"
            assert np.allclose(actual_outcome.sum(), 1.0), (
                "Outcomes for two players must sum to 1.0"
            )
        else:
            player_ids = tuple(players)
            actual_outcome = np.asarray([1.0, 0.0], dtype=np.float64)

        diffs = actual_outcome - self.expected_outcome(player_ids)
        for player_id, diff in zip(player_ids, diffs):
            self.elo_ratings[player_id] += self.elo_k * diff

        return diffs

    def _update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE]],
    ) -> Generator[npt.NDArray[np.float64]]:
        for match in matches:
            yield self.update_elo_ratings(match)

    @override
    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> npt.NDArray[np.float64] | None:
        if progress_bar:
            from tqdm import tqdm

            tqdm_kwargs = tqdm_kwargs or {}
            matches = tqdm(matches, desc="Updating elo ratings", **tqdm_kwargs)

        if full_results:
            return np.asarray(
                list(self._update_elo_ratings_batch(matches)),
                dtype=np.float64,
            )

        for _ in self._update_elo_ratings_batch(matches):
            pass
        return None


class RankOrderedLogitElo[ID_TYPE](EloRatingSystem[ID_TYPE]):
    """
    Rank-ordered-logit Elo with MC/DP for larger fields.
    """

    def __init__(
        self,
        *,
        init_elo_ratings: Mapping[ID_TYPE, np.float64 | float] | None = None,
        elo_initial: np.float64 | float = NP_ZERO,
        elo_k: np.float64 | float = NP_THIRTYTWO,
        elo_scale: np.float64 | float = NP_FOURHUNDRED,
        max_permutations: int = 6,
        max_dynamic_programming: int = 12,
        monte_carlo_samples: int = 5_000,
        rng: np.random.Generator | int | None = None,
    ) -> None:
        super().__init__(
            init_elo_ratings=init_elo_ratings,
            elo_initial=elo_initial,
            elo_k=elo_k,
            elo_scale=elo_scale,
        )
        self.max_permutations = max_permutations
        self.max_dynamic_programming = max_dynamic_programming
        self.monte_carlo_samples = monte_carlo_samples
        self._rng = (
            rng if isinstance(rng, np.random.Generator) else np.random.default_rng(rng)
        )

    def _calculate_probability_matrix_two_players(
        self,
        players: tuple[ID_TYPE, ID_TYPE],
    ) -> npt.NDArray[np.float64]:
        rating_a = self.elo_ratings[players[0]]
        rating_b = self.elo_ratings[players[1]]
        diff = rating_a - rating_b
        prob_a = elo_probability(diff, self.elo_scale)
        prob_b = 1 - prob_a
        return np.asarray([[prob_a, prob_b], [prob_b, prob_a]], dtype=np.float64)

    def _calculate_probability_matrix_permutations(
        self,
        players: tuple[ID_TYPE, ...],
        *,
        rtol: np.float64 | float = np.float64(1e-3),
        atol: np.float64 | float = np.float64(1e-4),
    ) -> npt.NDArray[np.float64]:
        ratings = np.asarray([self.elo_ratings[p] for p in players], dtype=np.float64)
        weights = np.power(NP_TEN, ratings / self.elo_scale)
        n = len(players)
        probs = np.zeros((n, n), dtype=np.float64)

        for perm in itertools.permutations(range(n)):
            denom = weights.sum(dtype=np.float64)
            p_perm = NP_ONE
            for player in range(n - 1):
                w = weights[perm[player]]
                p_perm *= w / denom
                denom -= w

            for position, player_idx in enumerate(perm):
                probs[player_idx, position] += p_perm

        col_sum = probs.sum(axis=0, dtype=np.float64)
        row_sum = probs.sum(axis=1, dtype=np.float64)
        assert np.allclose(col_sum, NP_ONE, rtol=rtol, atol=atol), (
            f"Probabilities must sum to 1 over players per position (got {col_sum})"
        )
        assert np.allclose(row_sum, NP_ONE, rtol=rtol, atol=atol), (
            f"Probabilities must sum to 1 over positions per player (got {row_sum})"
        )
        return probs

    def _calculate_probability_matrix_dynamic_programming(
        self,
        players: tuple[ID_TYPE, ...],
        *,
        rtol: np.float64 | float = np.float64(1e-3),
        atol: np.float64 | float = np.float64(1e-4),
    ) -> npt.NDArray[np.float64]:
        n = len(players)
        ratings = np.asarray([self.elo_ratings[p] for p in players], dtype=np.float64)
        w = np.power(NP_TEN, ratings / self.elo_scale)
        w_total = w.sum(dtype=np.float64)

        probs = np.zeros((n, n), dtype=np.float64)
        for i in range(n):
            other_idx = [j for j in range(n) if j != i]
            m = n - 1
            other_w = w[other_idx]

            num_masks = 1 << m
            subset_sum = np.zeros(num_masks, dtype=np.float64)
            for mask in range(1, num_masks):
                lsb = mask & -mask
                bit = lsb.bit_length() - 1
                subset_sum[mask] = subset_sum[mask ^ lsb] + other_w[bit]

            p = np.zeros(m + 1, dtype=np.float64)
            wi = w[i]  # NumPy scalar float64

            for mask in range(num_masks):
                tsize = int(mask.bit_count())
                denom = w_total - subset_sum[mask]
                base = wi / denom  # NumPy scalar
                if tsize <= m:
                    ks = np.arange(tsize, m + 1, dtype=np.int64)
                    coeffs = comb(m - tsize, ks - tsize, exact=False)
                    signs = np.where(((ks + tsize) & 1) == 1, -1.0, 1.0).astype(
                        np.float64
                    )
                    p[tsize : m + 1] += (base * signs * coeffs).astype(np.float64)

            p = np.clip(p, 0.0, 1.0)
            s = p.sum(dtype=np.float64)
            if not np.isclose(s, 1.0, rtol=rtol, atol=atol):
                if s > 0:
                    p /= s
                else:
                    p.fill(1.0 / (m + 1))

            probs[i, : m + 1] = p

        col_sum = probs.sum(axis=0, dtype=np.float64)
        row_sum = probs.sum(axis=1, dtype=np.float64)
        assert np.allclose(col_sum, NP_ONE, rtol=rtol, atol=atol)
        assert np.allclose(row_sum, NP_ONE, rtol=rtol, atol=atol)
        return probs

    def _calculate_probability_matrix_monte_carlo(
        self,
        players: tuple[ID_TYPE, ...],
    ) -> npt.NDArray[np.float64]:
        n = len(players)
        ratings = np.asarray([self.elo_ratings[p] for p in players], dtype=np.float64)
        weights = np.power(NP_TEN, ratings / self.elo_scale)
        counts = np.zeros((n, n), dtype=np.float64)

        idx_all = np.arange(n, dtype=np.int64)
        for _ in range(self.monte_carlo_samples):
            remaining = idx_all.tolist()
            order: list[int] = []
            w = weights.copy()
            while remaining:
                rem_arr = np.array(remaining, dtype=np.int64)
                probs = w[rem_arr]
                tot = probs.sum(dtype=np.float64)
                probs = np.divide(
                    probs,
                    tot,
                    out=np.full_like(probs, NP_ONE / probs.size),
                    where=tot > NP_ZERO,
                )
                chosen = int(self._rng.choice(rem_arr, p=probs))
                order.append(chosen)
                remaining.remove(chosen)
                w[chosen] = NP_ZERO
            for pos, player_idx in enumerate(order):
                counts[player_idx, pos] += NP_ONE

        probs = np.clip(counts / np.float64(self.monte_carlo_samples), NP_ZERO, NP_ONE)
        col_sums = probs.sum(axis=0, keepdims=True)
        col_sums[col_sums == NP_ZERO] = NP_ONE
        return probs / col_sums

    @override
    def probability_matrix(
        self,
        players: Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]:
        players = tuple(players)
        n = len(players)

        if n < 2:
            raise ValueError("At least 2 players are required")

        if n == 2:
            assert len(players) == 2
            return self._calculate_probability_matrix_two_players(players)

        if n <= self.max_permutations:
            return self._calculate_probability_matrix_permutations(players)

        if n <= self.max_dynamic_programming:
            return self._calculate_probability_matrix_dynamic_programming(players)

        return self._calculate_probability_matrix_monte_carlo(players)

    @override
    def expected_outcome(self, players: Iterable[ID_TYPE]) -> npt.NDArray[np.float64]:
        players = tuple(players)
        rank_payoff = np.arange(len(players) - 1, -1, -1, dtype=np.float64)
        probs = self.probability_matrix(players)
        return probs @ rank_payoff

    @override
    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE],
    ) -> npt.NDArray[np.float64]:
        if isinstance(players, Mapping):
            player_ids = tuple(players.keys())
            num_players = len(player_ids)
            actual_outcome = np.asarray(list(players.values()), dtype=np.float64)
            assert np.all(actual_outcome >= 0), "Payoffs must be non-negative"
            assert np.any(actual_outcome > 0), "At least one payoff must be positive"
            expected_sum = num_players * (num_players - 1) / 2
            assert np.allclose(actual_outcome.sum(), expected_sum), (
                f"Payoffs must sum to {expected_sum}, the sum of [n-1,...,0]"
            )
        else:
            player_ids = tuple(players)
            actual_outcome = np.arange(len(player_ids) - 1, -1, -1, dtype=np.float64)

        max_outcome = np.float64((len(player_ids) - 1))
        expected_outcome = self.expected_outcome(player_ids)
        diffs = (actual_outcome - expected_outcome) / max_outcome
        for player_id, diff in zip(player_ids, diffs):
            self.elo_ratings[player_id] += self.elo_k * diff

        return diffs

    def _update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE]],
    ) -> Generator[npt.NDArray[np.float64]]:
        for match in matches:
            yield self.update_elo_ratings(match)

    @override
    def update_elo_ratings_batch(
        self,
        matches: Iterable[Mapping[ID_TYPE, np.float64 | float] | Iterable[ID_TYPE]],
        *,
        full_results: bool = False,
        progress_bar: bool = False,
        tqdm_kwargs: dict[str, Any] | None = None,
    ) -> npt.NDArray[np.float64] | None:
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
    arrays: Iterable[npt.NDArray[np.float64]],
    *,
    pad_value: np.float64 | float = np.nan,
    dtype: np.dtype | None = None,
) -> npt.NDArray[np.float64]:
    arrays = tuple(arrays)
    max_len = max((a.shape[0] for a in arrays), default=0)
    result = np.full(
        shape=(len(arrays), max_len),
        fill_value=pad_value,
        dtype=dtype or np.float64,
    )

    for i, a in enumerate(arrays):
        result[i, : a.shape[0]] = a

    return result


def calculate_elo_ratings_two_players_python(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: np.float64 | float = NP_ZERO,
    elo_k: np.float64 | float = NP_THIRTYTWO,
    elo_scale: np.float64 | float = NP_FOURHUNDRED,
    progress_bar: bool = False,
) -> dict[int, np.float64]:
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


def calculate_elo_ratings_multi_players_python(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: np.float64 | float = NP_ZERO,
    elo_k: np.float64 | float = NP_THIRTYTWO,
    elo_scale: np.float64 | float = NP_FOURHUNDRED,
    progress_bar: bool = False,
) -> dict[int, np.float64]:
    assert matches.ndim == 2 and matches.shape[1] >= 2, (
        "Matches must be a 2D array with shape (num_matches, num_players>=2)"
    )
    elo: RankOrderedLogitElo = RankOrderedLogitElo(
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
    )
    num_matches = len(matches)
    matches_iter = (match[~np.isnan(match)].astype(np.int32) for match in matches)
    elo.update_elo_ratings_batch(
        matches_iter,
        progress_bar=progress_bar,
        tqdm_kwargs={"total": num_matches},
    )
    return dict(elo.elo_ratings)
