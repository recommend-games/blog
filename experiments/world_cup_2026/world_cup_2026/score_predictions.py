"""Per-match scoreline analytics built directly from the Poisson goal model.

Given (lambda_a, lambda_b), we can read everything off the joint
probability grid P(goals_A = i, goals_B = j) = Poisson(i; lambda_a) *
Poisson(j; lambda_b) for i, j in 0..max_goals:

  - win/draw/loss split: split the grid below diagonal / on diagonal / above
  - modal score: argmax(grid)
  - top-N scorelines: flatten + sort

No Monte Carlo needed.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import poisson

from . import config


def score_grid(
    lambda_a: float,
    lambda_b: float,
    max_goals: int = config.MAX_GOALS,
) -> np.ndarray:
    g = np.arange(max_goals + 1)
    p_a = poisson.pmf(g, lambda_a)
    p_b = poisson.pmf(g, lambda_b)
    p_a /= p_a.sum()
    p_b /= p_b.sum()
    return np.outer(p_a, p_b)


def outcome_probs(grid: np.ndarray) -> tuple[float, float, float]:
    p_a_wins = float(np.tril(grid, k=-1).sum())
    p_draw = float(np.trace(grid))
    p_b_wins = float(np.triu(grid, k=1).sum())
    return p_a_wins, p_draw, p_b_wins


def modal_score(grid: np.ndarray) -> tuple[int, int, float]:
    i, j = np.unravel_index(grid.argmax(), grid.shape)
    return int(i), int(j), float(grid[i, j])


def top_n_scores(grid: np.ndarray, n: int = 5) -> list[tuple[int, int, float]]:
    flat = grid.flatten()
    top_idx = np.argpartition(flat, -n)[-n:]
    top_idx = top_idx[np.argsort(-flat[top_idx])]
    rows, cols = np.unravel_index(top_idx, grid.shape)
    return [(int(rows[k]), int(cols[k]), float(flat[top_idx[k]])) for k in range(n)]
