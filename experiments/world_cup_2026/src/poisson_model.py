"""Elo expected score and Poisson lambda fitting for the match model.

Given an Elo difference (with host adjustment already applied), elo_expected_score
returns the team-A "expected score" s_A = P(A wins) + 0.5 * P(draw). The Poisson
model then chooses (lambda_A, lambda_B) so that lambda_A + lambda_B = total_goals
and the implied expected score from a truncated Poisson grid matches s_A.

Lambda lookups happen many millions of times during a simulation, so the
results are cached by rounded Elo difference (~1200 unique keys in practice).
"""

from __future__ import annotations

from functools import cache, lru_cache

import numpy as np
from scipy.optimize import brentq
from scipy.stats import poisson

from . import config

_EPS = 1e-9


def elo_expected_score(elo_diff: float) -> float:
    return 1.0 / (1.0 + 10.0 ** (-elo_diff / 400.0))


def poisson_expected_score(
    lambda_a: float,
    lambda_b: float,
    max_goals: int = config.MAX_GOALS,
) -> float:
    g = np.arange(max_goals + 1)
    p_a = poisson.pmf(g, lambda_a)
    p_b = poisson.pmf(g, lambda_b)
    # Renormalise the truncated PMFs so the joint grid sums to 1. For
    # reasonable lambdas (< 5) this is a no-op; for extreme lambdas it
    # corrects the otherwise leaking right-tail mass.
    p_a /= p_a.sum()
    p_b /= p_b.sum()
    m = np.outer(p_a, p_b)
    p_a_wins = float(np.tril(m, k=-1).sum())
    p_draw = float(np.trace(m))
    return p_a_wins + 0.5 * p_draw


@cache
def _saturation_bound(total_goals: float, max_goals: int, min_lambda: float) -> float:
    # Highest s_A reachable in the normal (lambda_a + lambda_b = total_goals)
    # regime, with the underdog pinned at min_lambda.
    return poisson_expected_score(total_goals - min_lambda, min_lambda, max_goals)


def fit_lambdas(
    s_a: float,
    total_goals: float = config.TOTAL_GOALS,
    max_goals: int = config.MAX_GOALS,
    min_lambda: float = config.MIN_LAMBDA,
) -> tuple[float, float]:
    sat_hi = _saturation_bound(total_goals, max_goals, min_lambda)

    if 1.0 - sat_hi <= s_a <= sat_hi:
        def objective(lam_a: float) -> float:
            return poisson_expected_score(lam_a, total_goals - lam_a, max_goals) - s_a
        lam_a = brentq(objective, min_lambda, total_goals - min_lambda, xtol=1e-7)
        return float(lam_a), float(total_goals - lam_a)

    if s_a > sat_hi:
        # Team A is so dominant the budget can't represent it; pin the
        # underdog at min_lambda and let lambda_a rise above total_goals.
        def objective(lam_a: float) -> float:
            return poisson_expected_score(lam_a, min_lambda, max_goals) - s_a
        lam_a = brentq(
            objective, total_goals - min_lambda, max_goals - _EPS, xtol=1e-7
        )
        return float(lam_a), float(min_lambda)

    # Symmetric: team B dominant, pin lambda_a and solve for lambda_b.
    def objective(lam_b: float) -> float:
        return poisson_expected_score(min_lambda, lam_b, max_goals) - s_a
    lam_b = brentq(
        objective, total_goals - min_lambda, max_goals - _EPS, xtol=1e-7
    )
    return float(min_lambda), float(lam_b)


@lru_cache(maxsize=None)
def lambdas_for_rounded_diff(
    rounded_diff: int,
    total_goals: float = config.TOTAL_GOALS,
    max_goals: int = config.MAX_GOALS,
) -> tuple[float, float]:
    s_a = elo_expected_score(float(rounded_diff))
    return fit_lambdas(s_a, total_goals=total_goals, max_goals=max_goals)


def build_lambda_cache(elo_diffs):
    """Precompute and return a dict {rounded_diff: (lambda_a, lambda_b)}."""
    cache: dict[int, tuple[float, float]] = {}
    rounding = config.ELO_DIFFERENCE_CACHE_ROUNDING
    for d in elo_diffs:
        key = round(d / rounding) * rounding
        if key not in cache:
            cache[key] = lambdas_for_rounded_diff(key)
    return cache
