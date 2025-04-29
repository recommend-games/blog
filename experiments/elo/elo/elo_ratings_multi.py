from __future__ import annotations

import numpy as np
import itertools
from typing import List, Any, Optional


class RankOrderedLogitElo:
    """
    A vectorised, numpy-based implementation of the rank-ordered-logit (Plackett–Luce) Elo.
    Defaults to linear pseudo-scores if no prize structure is given.
    """

    def __init__(self, k: float = 32.0):
        self.k = k
        self.ratings = {}  # player_id -> rating (float), default 0.0

    def _get_rating_array(self, players: List[Any]) -> np.ndarray:
        # Fetch current ratings (default 0.0)
        return np.array([self.ratings.get(p, 0.0) for p in players], dtype=float)

    def _set_rating_array(self, players: List[Any], arr: np.ndarray):
        # Write back updated ratings
        for p, r in zip(players, arr):
            self.ratings[p] = float(r)

    def rate(
        self,
        players: List[Any],
        ranks: List[int],
        prizes: Optional[List[float]] = None,
    ):
        """
        Update ratings for one match.

        players : list of player IDs
        ranks   : list of finishing positions (1 = first, 2 = second, ...).
                  Equal ranks are allowed (ties).
        prizes  : optional list of payoffs π_k for each position in [1..n];
                  length must equal len(players).  If None, uses linear
                  pseudo-scores (n - rank)/(n - 1).
        """
        n = len(players)
        ratings_arr = self._get_rating_array(players)
        exp_r = np.exp(ratings_arr)

        # Build the pay-off vector π
        if prizes is not None:
            pi = np.array(prizes, dtype=float)
        else:
            ranks_arr = np.array(ranks, dtype=float)
            pi = (n - ranks_arr) / (n - 1)

        pi_max = pi.max()
        S_hat = pi / pi_max

        # Enumerate all permutations of 0..n-1
        perms = np.array(
            list(itertools.permutations(range(n))),
            dtype=int,
        )  # shape (F, n)
        F = perms.shape[0]

        # Compute Plackett–Luce probabilities for each perm
        # stage_probs[k] = exp_r[perms[:,k]] / sum(exp_r[perms[:,k:]], axis=1)
        stage_probs = []
        for k in range(n):
            num = exp_r[perms[:, k]]
            denom = np.sum(exp_r[perms[:, k:]], axis=1)
            stage_probs.append(num / denom)
        perm_probs = np.prod(np.stack(stage_probs, axis=1), axis=1)  # shape (F,)

        # Build payoff matrix: payoff_mat[j,i] = π at the position where player i sits in perm j
        payoff_mat = np.zeros((F, n), dtype=float)
        rows = np.arange(F)[:, None]
        payoff_mat[rows, perms] = pi[None, :]

        # Expected raw payoff
        E_raw = (perm_probs[:, None] * payoff_mat).sum(axis=0)  # shape (n,)
        E_hat = E_raw / pi_max

        # Rating update
        ratings_arr += self.k * (S_hat - E_hat)
        self._set_rating_array(players, ratings_arr)

    def get_rating(self, player: Any) -> float:
        return self.ratings.get(player, 0.0)

    def batch_ratings(self, players: List[Any]) -> np.ndarray:
        return self._get_rating_array(players)


# Example usage:
if __name__ == "__main__":
    elo = RankOrderedLogitElo(k=24.0)
    players = ["Alice", "Bob", "Carol", "Dave"]
    ranks = [1, 2, 2, 4]  # Carol tied second with Bob
    # No prizes → linear pseudo-scores used
    elo.rate(players, ranks)
    print({p: elo.get_rating(p) for p in players})

    # With explicit prize structure:
    prizes = [10, 6, 4, 2]
    elo.rate(players, ranks, prizes=prizes)
    print({p: elo.get_rating(p) for p in players})
