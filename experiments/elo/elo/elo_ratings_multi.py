from __future__ import annotations

import numpy as np
import itertools
from typing import Generic, TypeVar, TYPE_CHECKING
from collections import defaultdict

ID_TYPE = TypeVar("ID_TYPE")

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


class RankOrderedLogitElo(Generic[ID_TYPE]):
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
        self.elo_ratings: defaultdict[ID_TYPE, float] = defaultdict(
            lambda: self.elo_initial,
            init_elo_ratings if init_elo_ratings is not None else {},
        )
        self.elo_k = elo_k
        self.elo_scale = elo_scale

        self.max_exact = max_exact
        self.mc_samples = mc_samples

    def calculate_probability_matrix(self, players: Iterable[ID_TYPE]) -> np.ndarray:
        players = tuple(players)
        num_players = len(players)

        if num_players < 2:
            raise ValueError("At least 2 players are required")

        if num_players > self.max_exact:
            # TODO: implement Monte Carlo fallback
            raise NotImplementedError(
                f"Monte Carlo fallback not implemented for n>{self.max_exact}"
            )

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

        assert np.allclose(probs.sum(axis=0), 1), "Probabilities must sum to 1"
        assert np.allclose(probs.sum(axis=1), 1), "Probabilities must sum to 1"

        return probs

    def calculate_expected_payoff(
        self,
        players: Iterable[ID_TYPE],
        rank_payoffs: np.ndarray,
    ) -> np.ndarray:
        assert rank_payoffs.ndim == 1, "Rank payoffs must be a 1D array"
        probs = self.calculate_probability_matrix(players)
        assert len(rank_payoffs) == len(probs), (
            "Rank payoffs must be the same length as the number of players"
        )
        return probs @ rank_payoffs

    def update_elo_ratings(
        self,
        players: Mapping[ID_TYPE, float],
    ) -> None:
        player_ids = tuple(players.keys())
        payoffs = np.array(list(players.values()), dtype=float)
        assert np.all(payoffs >= 0), "Payoffs must be non-negative"
        assert np.any(payoffs > 0), "At least one payoff must be positive"
        max_payoff = payoffs.max()
        expected_payoffs = self.calculate_expected_payoff(player_ids, payoffs)
        diffs = (payoffs - expected_payoffs) / max_payoff
        for player_id, diff in zip(player_ids, diffs):
            self.elo_ratings[player_id] += self.elo_k * diff
