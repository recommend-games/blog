import numpy as np
import itertools
import numpy.random as npr
from typing import List, Any, Optional


class RankOrderedLogitElo:
    """
    Numpy-based rank-ordered-logit Elo with Monte-Carlo fallback for large fields.
    """

    def __init__(self, k: float = 32.0, max_exact: int = 6, mc_samples: int = 5000):
        self.k = k
        self.max_exact = max_exact
        self.mc_samples = mc_samples
        self.ratings = {}  # player_id -> rating

    def _get_ratings(self, players: List[Any]) -> np.ndarray:
        return np.array([self.ratings.get(p, 0.0) for p in players], dtype=float)

    def _set_ratings(self, players: List[Any], arr: np.ndarray):
        for p, r in zip(players, arr):
            self.ratings[p] = float(r)

    def rate(
        self,
        players: List[Any],
        ranks: List[int],
        prizes: Optional[List[float]] = None,
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
        R += self.k * (S_hat - E_hat)
        self._set_ratings(players, R)

    def get_rating(self, player: Any) -> float:
        return self.ratings.get(player, 0.0)

    def batch_ratings(self, players: List[Any]) -> np.ndarray:
        return self._get_ratings(players)


# Example usage
if __name__ == "__main__":
    elo = RankOrderedLogitElo(k=24.0, max_exact=6, mc_samples=10000)
    players = ["A", "B", "C", "D", "E", "F", "G"]
    ranks = [1, 2, 3, 4, 5, 6, 7]
    elo.rate(players, ranks)  # uses Monte Carlo for n>6
    print({p: elo.get_rating(p) for p in players})
