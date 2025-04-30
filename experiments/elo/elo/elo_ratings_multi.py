from __future__ import annotations

import numpy as np
import itertools
import numpy.random as npr
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
        self.elo_initial = elo_initial
        self.elo_k = elo_k
        self.elo_scale = elo_scale
        self.max_exact = max_exact
        self.mc_samples = mc_samples
        self.elo_ratings: defaultdict[ID_TYPE, float] = defaultdict(
            lambda: self.elo_initial,
            init_elo_ratings if init_elo_ratings is not None else {},
        )

    def calculate_probability_matrix(self, players: Iterable[ID_TYPE]) -> np.ndarray:
        players = tuple(players)
        num_players = len(players)
        if num_players > self.max_exact:
            raise NotImplementedError(
                f"Monte Carlo fallback not implemented for n>{self.max_exact}"
            )

        probs = np.zeros((num_players, num_players))

        ratings = self._get_ratings(players)
        exp_ratings = 10 ** (ratings / self.elo_scale)

        for perm in itertools.permutations(range(num_players)):
            prob = 1
            denom = np.sum(exp_ratings)
            for i in range(num_players - 1):
                prob *= exp_ratings[perm[i]] / denom
                denom -= exp_ratings[perm[i]]
            for player, position in enumerate(perm):
                probs[player, position] += prob

    def _calculate_player_scores(self, players: Mapping[ID_TYPE, float]) -> np.ndarray:
        scores = np.array(list(players.values()), dtype=float)
        assert np.all(scores >= 0)
        assert np.any(scores > 0)
        scores /= scores.max()
        return scores

    def calculate_elo_ratings(
        self,
        players: Mapping[ID_TYPE, float],
    ) -> defaultdict[ID_TYPE, float]:
        # player_ids = list(players.keys())
        # player_scores = self._calculate_player_scores(players)
        # probs = self.calculate_probability_matrix(player_ids)
        # TODO: finish calculations
        return self.elo_ratings

    def _get_ratings(self, players: Iterable[ID_TYPE]) -> np.ndarray:
        return np.array([self.elo_ratings[p] for p in players], dtype=float)

    def _set_ratings(self, players: Iterable[ID_TYPE], arr: np.ndarray):
        for p, r in zip(players, arr):
            self.elo_ratings[p] = float(r)

    def rate(
        self,
        players: list[ID_TYPE],
        ranks: list[int],
        prizes: list[float] | None = None,
    ):
        n = len(players)
        R = self._get_ratings(players)
        expR = np.exp(R)

        # define payoff vector π
        if prizes is not None:
            pi = np.array(prizes, dtype=float)
        else:
            ranks_arr = np.array(ranks, dtype=float)
            pi = (n - ranks_arr) / (n - 1)

        pi_max = pi.max()
        S_hat = pi / pi_max

        # compute expected payoffs
        if n <= self.max_exact:
            perms = np.array(list(itertools.permutations(range(n))), dtype=int)
            # Plackett-Luce probability for each perm
            stage_probs = []
            for k in range(n):
                num = expR[perms[:, k]]
                denom = np.sum(expR[perms[:, k:]], axis=1)
                stage_probs.append(num / denom)
            perm_probs = np.prod(np.stack(stage_probs, axis=1), axis=1)
            # payoff per perm
            rows = np.arange(perms.shape[0])[:, None]
            payoff_mat = np.zeros_like(
                perm_probs[:, None] * np.zeros((perms.shape[0], n))
            )
            payoff_mat[rows, perms] = pi[None, :]
            E_raw = (perm_probs[:, None] * payoff_mat).sum(axis=0)
        else:
            # Monte Carlo fallback
            E_raw = np.zeros(n, dtype=float)
            for _ in range(self.mc_samples):
                remaining = list(range(n))
                denom = expR.copy()
                ranking_pos = [None] * n
                for k in range(n):
                    weights = denom[remaining]
                    weights_sum = weights.sum()
                    probs = weights / weights_sum
                    chosen = npr.choice(remaining, p=probs)
                    ranking_pos[chosen] = k
                    remaining.remove(chosen)
                # accumulate payoff
                for i in range(n):
                    E_raw[i] += pi[ranking_pos[i]]
            E_raw /= self.mc_samples

        E_hat = E_raw / pi_max

        # update ratings
        R += self.elo_k * (S_hat - E_hat)
        self._set_ratings(players, R)

    def get_rating(self, player: ID_TYPE) -> float:
        return self.elo_ratings.get(player, 0.0)

    def batch_ratings(self, players: list[ID_TYPE]) -> np.ndarray:
        return self._get_ratings(players)


# Example usage
if __name__ == "__main__":
    elo = RankOrderedLogitElo(elo_k=24.0, max_exact=6, mc_samples=10000)
    players = ["A", "B", "C", "D", "E", "F", "G"]
    ranks = [1, 2, 3, 4, 5, 6, 7]
    elo.rate(players, ranks)  # uses Monte Carlo for n>6
    print({p: elo.get_rating(p) for p in players})
