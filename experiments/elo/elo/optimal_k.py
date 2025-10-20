from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar

from elo.elo_ratings import EloRatingSystem, TwoPlayerElo, RankOrderedLogitElo

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import TypeVar

    ID_TYPE = TypeVar("ID_TYPE")


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
    final_bracket_halfwidth: float | np.float64 = np.log(2.0),  # half-width in log-k
    xatol: float | np.float64 = 1e-3,  # tolerance in log-k for Brent refine
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

    def _loss(elo_k: np.float64) -> np.float64:
        elo: EloRatingSystem[ID_TYPE] = (
            TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
            if two_player_only
            else RankOrderedLogitElo(elo_k=elo_k, elo_scale=elo_scale)
        )
        return calculate_loss(elo=elo, matches=match_list, progress_bar=False)

    # 1) Coarse bracket on the FULL sample in theta = log(k)
    th_min = np.log(min_elo_k)
    th_max = np.log(max_elo_k)
    thetas = np.linspace(th_min, th_max, max(5, coarse_points))
    # Evaluate coarse grid on FULL data
    coarse_vals = [_loss(np.exp(th)) for th in thetas]
    # Pick best theta and form a local bracket [a, b, c] in log-space
    best_i = int(np.argmin(coarse_vals))
    # Keep b away from edges for a proper (a < b < c) triple
    b = thetas[np.clip(best_i, 1, len(thetas) - 2)]
    # Symmetric bracket around b in log-space, clipped to bounds.
    # Ensure non-degenerate width by using at least half a grid step.
    grid_step = thetas[1] - thetas[0]
    half = max(final_bracket_halfwidth, 0.5 * grid_step)
    # Form bracket
    a = max(th_min, b - half)
    c = min(th_max, b + half)

    if not (a < b < c):
        # Degenerate cases: zero half-width, collapsed bounds, or numerical ties.
        eps = 1e-9
        mid = 0.5 * (th_min + th_max)
        a, b, c = th_min, mid, th_max
        if not (a < b < c):  # th_min == th_max edge case
            c = a + eps

    # 2) Final Brent refine on the FULL sample
    def _loss_theta(theta: np.float64) -> np.float64:
        return _loss(np.exp(theta))

    result = minimize_scalar(
        fun=_loss_theta,
        method="brent",
        bracket=(a, b, c),
        options={"xtol": xatol, "maxiter": 80},
    )

    return np.exp(result.x)
