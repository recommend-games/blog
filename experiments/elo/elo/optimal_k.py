from __future__ import annotations

import logging

from collections.abc import Mapping
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar

from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import TypeVar

    ID_TYPE = TypeVar("ID_TYPE")

LOGGER = logging.getLogger(__name__)


def calculate_loss[ID_TYPE](
    *,
    elo: EloRatingSystem[ID_TYPE],
    matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    progress_bar: bool = False,
) -> np.float64:
    errors = elo.update_elo_ratings_batch(
        matches,
        full_results=True,
        progress_bar=progress_bar,
    )
    assert errors is not None
    return np.nanmean(errors**2)


def approximate_optimal_k[ID_TYPE](
    *,
    matches: Iterable[Mapping[ID_TYPE, float] | Iterable[ID_TYPE]],
    two_player_only: bool = False,
    min_elo_k: float | np.float64 = 1e-6,
    max_elo_k: float | np.float64 = 200.0,
    elo_scale: float | np.float64 = 400.0,
    coarse_points: int | np.int64 = 12,  # number of thetas in coarse scan
    xatol: float | np.float64 = 1e-3,  # tolerance in log-k for Brent refine
    maxiter: int | np.int64 = 80,
) -> np.float64:
    """
    Compute k* for the *given* population of players and matches ONLY.

    This routine explicitly treats k* as *data-dependent*. It performs:
      1) A coarse scan of L(k) on the full set of matches to find a good bracket
         in theta = log(k)-space; and
      2) A Brent refinement on the full match list within that bracket.

    Parameters
    ----------
    matches : iterable of Mapping or iterable of player IDs
        Chronological stream of matches (Elo is order-sensitive).
    two_player_only : bool
        Use TwoPlayerElo if True, else RankOrderedLogitElo.
    min_elo_k, max_elo_k : float
        Search bounds for k. min_elo_k must be > 0 to define log(k).
    elo_scale : float
        Logistic scale parameter (e.g., 400).
    coarse_points : int
        Grid size for coarse scan in log-space.
    final_bracket_halfwidth : float
        Half-width of the final bracket in log-space around the coarse best.
    xatol : float
        Absolute tolerance in log(k) for Brent; corresponds to relative tol in k.

    Returns
    -------
    float
        The k* that minimises mean squared prediction error on the PROVIDED matches.
    """

    # 0) Normalise matches ONCE; k* is specific to this realised sample.
    match_list: list[Mapping[ID_TYPE, float]] = [
        dict(zip((m := tuple(match)), range(len(m) - 1, -1, -1)))
        if not isinstance(match, Mapping)
        else match
        for match in matches
    ]

    n = len(match_list)
    if not n:
        raise ValueError("approximate_optimal_k: empty match stream")

    # Validate and sanitise bounds
    min_k = min_elo_k
    max_k = max_elo_k
    if not (np.isfinite(min_k) and np.isfinite(max_k)):
        raise ValueError("min_elo_k and max_elo_k must be finite")
    if min_k <= 0.0:
        # Avoid log(0); use the smallest positive *normal* float, not subnormal
        min_k = np.finfo(float).tiny
    if max_k <= min_k:
        raise ValueError(
            f"max_elo_k ({max_k}) must be greater than min_elo_k ({min_k})."
        )

    def _loss_theta(theta: np.float64) -> np.float64:
        elo_k = np.exp(theta)
        elo: EloRatingSystem[ID_TYPE] = (
            TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
            if two_player_only
            else RankOrderedLogitElo(elo_k=elo_k, elo_scale=elo_scale)
        )
        return calculate_loss(elo=elo, matches=match_list, progress_bar=False)

    # 1) Coarse bracket on the FULL sample in theta = log(k)
    th_min: np.float64 = np.log(min_k)
    th_max: np.float64 = np.log(max_k)
    thetas = np.linspace(th_min, th_max, max(5, coarse_points))
    # Evaluate coarse grid on FULL data
    coarse_vals = np.array([_loss_theta(th) for th in thetas])

    # Pick a bracket that satisfies Brent's requirement: f(b) < f(a) and f(b) < f(c)
    if not np.all(np.isfinite(coarse_vals)):
        raise ValueError("Non-finite loss encountered during coarse scan.")

    # Find local minima on the coarse grid
    candidates = [
        i
        for i in range(1, len(coarse_vals) - 1)
        if (coarse_vals[i] < coarse_vals[i - 1])
        and (coarse_vals[i] < coarse_vals[i + 1])
    ]

    if not candidates:
        LOGGER.debug(
            "approximate_optimal_k: No strict local minimum found on coarse grid; "
            "falling back to bounded search.",
        )
        LOGGER.debug("thetas: %s; values: %s", thetas, coarse_vals)
        # No strict local minimum on the coarse grid (flat/noisy surface): fall back to bounded search
        result = minimize_scalar(  # type: ignore[call-overload]
            fun=_loss_theta,
            method="bounded",
            bounds=(th_min, th_max),
            options={"xatol": xatol, "maxiter": maxiter * 2},
        )
        return np.exp(result.x)

    # Choose the lowest local minimum and its immediate neighbours as a strict bracket
    i = min(candidates, key=lambda j: coarse_vals[j])
    a, b, c = thetas[i - 1], thetas[i], thetas[i + 1]

    result = minimize_scalar(  # type: ignore[call-overload]
        fun=_loss_theta,
        method="brent",
        bracket=(a, b, c),
        options={"xtol": xatol, "maxiter": maxiter},
    )
    return np.exp(result.x)
