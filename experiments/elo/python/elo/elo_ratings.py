from __future__ import annotations

import itertools
import math
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
        max_dp: int = 12,
        mc_samples: int = 5_000,
        rng: np.random.Generator | int | None = None,
    ) -> None:
        super().__init__(
            init_elo_ratings=init_elo_ratings,
            elo_initial=elo_initial,
            elo_k=elo_k,
            elo_scale=elo_scale,
        )
        self.max_exact = max_exact
        self.max_dp = max_dp
        self.mc_samples = mc_samples
        self._rng = (
            rng if isinstance(rng, np.random.Generator) else np.random.default_rng(rng)
        )

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

    def _calculate_probability_matrix_from_permutations(
        self,
        players: tuple[ID_TYPE, ...],
        rtol: float = 1e-3,
        atol: float = 1e-4,
    ) -> np.ndarray:
        num_players = len(players)
        ratings = np.array([self.elo_ratings[p] for p in players], dtype=np.float64)
        # Plackett–Luce weights (paper §2.2): w_i = 10^(R_i/scale)
        weights = np.power(10.0, ratings / self.elo_scale)

        # probs[i, k] = P(player i finishes at rank k), k=0 is best rank
        probs = np.zeros((num_players, num_players), dtype=np.float64)

        for perm in itertools.permutations(range(num_players)):
            # Probability of this exact ranking under PL:
            # \prod_{l=0}^{n-2} w_{perm[l]} / \sum_{j=l}^{n-1} w_{perm[j]}
            denom = weights.sum()
            p_perm = np.float64(1.0)
            for player in range(num_players - 1):
                w = weights[perm[player]]
                p_perm *= w / denom
                denom -= w  # remove the chosen player's weight

            # Accumulate into player/position probabilities
            for position, player_idx in enumerate(perm):
                probs[player_idx, position] += p_perm

        # Numerical sanity checks (no balancing; PL is already doubly-stochastic up to FP error)
        col_sum = probs.sum(axis=0)
        row_sum = probs.sum(axis=1)
        assert np.allclose(col_sum, 1.0, rtol=rtol, atol=atol), (
            f"Probabilities must sum to 1 over players per position (got {col_sum})"
        )
        assert np.allclose(row_sum, 1.0, rtol=rtol, atol=atol), (
            f"Probabilities must sum to 1 over positions per player (got {row_sum})"
        )

        return probs

    def _calculate_probability_matrix_from_dp(
        self,
        players: tuple[ID_TYPE, ...],
        *,
        rtol: float = 1e-9,
        atol: float = 1e-12,
    ) -> np.ndarray:
        n = len(players)
        ratings = np.array([self.elo_ratings[p] for p in players], dtype=np.float64)
        w = np.power(10.0, ratings / self.elo_scale)
        W_total = float(w.sum())

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

            P = np.zeros(m + 1, dtype=np.float64)
            wi = float(w[i])
            for mask in range(num_masks):
                tsize = mask.bit_count()
                denom = W_total - subset_sum[mask]
                base = wi / denom
                sign_mask = -1.0 if (tsize & 1) else 1.0
                for k in range(tsize, m + 1):
                    sign_k = -1.0 if (k & 1) else 1.0
                    coeff = math.comb(m - tsize, k - tsize)
                    P[k] += base * sign_mask * sign_k * coeff

            P = np.clip(P, 0.0, 1.0)
            s = P.sum()
            if not np.isclose(s, 1.0, rtol=rtol, atol=atol):
                P = (P / s) if s > 0 else np.full_like(P, 1.0 / (m + 1))
            probs[i, : m + 1] = P

        col_sum = probs.sum(axis=0)
        row_sum = probs.sum(axis=1)
        assert np.allclose(col_sum, 1.0, rtol=1e-6, atol=1e-8)
        assert np.allclose(row_sum, 1.0, rtol=1e-6, atol=1e-8)
        return probs

    def _calculate_probability_matrix_from_simulations(
        self,
        players: tuple[ID_TYPE, ...],
    ) -> np.ndarray:
        n = len(players)
        ratings = np.array([self.elo_ratings[p] for p in players], dtype=np.float64)
        weights = np.power(10.0, ratings / self.elo_scale)
        counts = np.zeros((n, n), dtype=np.float64)

        rng = self._rng
        idx_all = np.arange(n, dtype=np.int64)
        for _ in range(self.mc_samples):
            remaining = idx_all.tolist()
            order: list[int] = []
            w = weights.copy()
            while remaining:
                rem_arr = np.array(remaining, dtype=np.int64)
                probs = w[rem_arr]
                tot = probs.sum()
                if not np.isfinite(tot) or tot <= 0:
                    probs = np.ones_like(probs, dtype=np.float64)
                    tot = probs.sum()
                probs = probs / tot
                chosen = int(rng.choice(rem_arr, p=probs))
                order.append(chosen)
                remaining.remove(chosen)
                w[chosen] = 0.0
            for pos, player_idx in enumerate(order):
                counts[player_idx, pos] += 1.0

        probs = np.clip(counts / float(self.mc_samples), 0.0, 1.0)
        col_sums = probs.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0.0] = 1.0
        return probs / col_sums

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

        if len(players) <= self.max_exact:
            return self._calculate_probability_matrix_from_permutations(players)

        if len(players) <= self.max_dp:
            return self._calculate_probability_matrix_from_dp(players)

        return self._calculate_probability_matrix_from_simulations(players)

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


def calculate_elo_ratings_two_players_python(
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


def calculate_elo_ratings_multi_players_python(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: float = 0,
    elo_k: float = 32,
    elo_scale: float = 400,
    progress_bar: bool = False,
) -> dict[int, float]:
    assert matches.ndim == 2 and matches.shape[1] >= 2, (
        "Matches must be a 2D array with shape (num_matches, num_players>=2)"
    )
    elo: RankOrderedLogitElo = RankOrderedLogitElo(
        elo_initial=elo_initial,
        elo_k=elo_k,
        elo_scale=elo_scale,
    )
    num_matches = len(matches)
    # Iterate over matches and drop nans from each match
    matches_iter = (match[~np.isnan(match)].astype(np.int32) for match in matches)
    elo.update_elo_ratings_batch(
        matches_iter,
        progress_bar=progress_bar,
        tqdm_kwargs={"total": num_matches},
    )
    return dict(elo.elo_ratings)
