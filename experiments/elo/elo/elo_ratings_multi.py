from __future__ import annotations

from collections import defaultdict
from itertools import permutations
import math
import random


class RankOrderedLogitElo:
    """
    Multiplayer Elo using the Plackett–Luce (rank‑ordered logit) model.

    Parameters
    ----------
    k : float, default 32
        Learning rate (just as in standard Elo).  Tune this on historical
        data by minimising a Brier‑type loss, exactly like in the paper.
    """

    def __init__(self, k: float = 32.0):
        self.k = k
        self.R = defaultdict(float)  # default rating = 0.0

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _pl_prob(order, expR):
        """
        Probability of a specific ranking *order* under Plackett‑Luce.

        order : tuple[int]
            One permutation of player indices, winner first.
        expR : list[float]
            pre‑computed exponentials of the players' ratings.
        """
        p = 1.0
        denom = sum(expR)
        for idx in order:
            p *= expR[idx] / denom
            denom -= expR[idx]
        return p

    def _expected_normalised_scores(self, players, prizes, max_enum=6, mc_samples=5000):
        """
        Expected normalised prize for each player.

        players : list[hashable]
        prizes  : list[float]      (len == len(players))
        """
        n = len(players)
        assert n == len(prizes), "players and prizes length mismatch"
        max_prize = max(prizes)
        norm_prize = [p / max_prize for p in prizes]
        ratings = [self.R[p] for p in players]
        expR = [math.exp(r) for r in ratings]

        expected = [0.0] * n

        # ---- exact enumeration (factorial) for small fields ---- #
        if n <= max_enum:
            for order in permutations(range(n)):
                prob = self._pl_prob(order, expR)
                for pos, idx in enumerate(order):
                    expected[idx] += norm_prize[pos] * prob
        else:
            # ---- Monte‑Carlo approximation for larger n ---- #
            for _ in range(mc_samples):
                remaining = list(range(n))
                ranking = []
                while remaining:
                    # draw winner according to current weights
                    weights = [expR[i] for i in remaining]
                    chosen_idx = random.choices(remaining, weights)[0]
                    ranking.append(chosen_idx)
                    remaining.remove(chosen_idx)

                # compute prob of this ranking (needed for importance‑weighting)
                prob = self._pl_prob(tuple(ranking), expR)
                for pos, idx in enumerate(ranking):
                    expected[idx] += norm_prize[pos] * prob  # prob already weights

            # normalise because probabilities sum to 1 in expectation
            total_prob = (
                sum(self._pl_prob(order, expR) for order in permutations(range(n)))
                if n <= max_enum
                else 1.0
            )
            expected = [e / total_prob for e in expected]

        return expected

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def rate_match(self, players, prizes, actual_prizes):
        """
        Update ratings after one multiplayer match.

        players       : list[hashable]         ordered arbitrarily
        prizes        : list[float]            prize money (or points) by finishing position
        actual_prizes : list[float]            prize actually earned by each *player*
                                                (same order as `players`)
        """
        max_prize = max(prizes)
        norm_actual = [s / max_prize for s in actual_prizes]

        expected = self._expected_normalised_scores(players, prizes)

        for idx, p in enumerate(players):
            self.R[p] += self.k * (norm_actual[idx] - expected[idx])

    # ------------------------------------------------------------------ #
    #  Convenience
    # ------------------------------------------------------------------ #

    def rating(self, player):
        return self.R[player]


# -------------------------------------------------------------------------- #
#  Demo: 4‑player free‑for‑all (prizes 10‑6‑4‑2)
# -------------------------------------------------------------------------- #
elo = RankOrderedLogitElo(k=24)

players = ["A", "B", "C", "D"]
prizes = [10, 6, 4, 2]  # winner‑takes‑most

# Suppose the first match ends A‑B‑C‑D
actual_prizes = [10, 6, 4, 2]
print(elo.rate_match(players, prizes, actual_prizes))

# Second match D‑B‑A‑C
actual_prizes = [10, 6, 4, 2]  # but reorder to players' list order
print(elo.rate_match(players, prizes, [4, 6, 2, 10]))

# Show current ratings
print({p: round(elo.rating(p), 2) for p in players})
