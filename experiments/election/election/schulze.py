"""
This module implements the Schulze method for ranking games based on user preferences.
"""

from __future__ import annotations

import numpy as np
from scipy.sparse import dok_matrix, csr_matrix, lil_matrix


def compute_pairwise_preferences(rating_matrix: csr_matrix) -> csr_matrix:
    """
    Compute sparse pairwise wins matrix from a user-game rating matrix.
    Assumes ratings are numeric and higher means better.

    Args:
        rating_matrix (csr_matrix): A sparse (num_users, num_games) matrix with ratings.

    Returns:
        csr_matrix: A sparse (num_games, num_games) matrix with pairwise wins.
    """
    num_games = rating_matrix.shape[1]
    pairwise_wins = dok_matrix((num_games, num_games), dtype=int)

    for user_ratings in rating_matrix:
        rated_indices = user_ratings.indices
        user_data = user_ratings.data
        for i, idx_i in enumerate(rated_indices):
            for j, idx_j in enumerate(rated_indices):
                if idx_i != idx_j and user_data[i] > user_data[j]:
                    pairwise_wins[idx_i, idx_j] += 1

    return pairwise_wins.tocsr()


def schulze_method(pairwise_wins: csr_matrix) -> list[int]:
    """
    Compute the Schulze ranking from a sparse pairwise wins matrix.

    Args:
        pairwise_wins (csr_matrix): A sparse (num_games, num_games) matrix of pairwise wins.

    Returns:
        list[int]: List of game indices in descending order of preference.
    """
    num_games = pairwise_wins.shape[0]
    strength = pairwise_wins.toarray()

    # Compute strongest paths using optimized Floyd-Warshall updates
    for i in range(num_games):
        for j in range(num_games):
            if strength[j, i] > 0:
                for k in range(num_games):
                    if strength[i, k] > 0:
                        strength[j, k] = max(
                            strength[j, k], min(strength[j, i], strength[i, k])
                        )

    # Determine ranking based on strongest paths
    ranking = sorted(
        range(num_games),
        key=lambda x: np.count_nonzero(strength[x] > strength[:, x]),
        reverse=True,
    )

    return ranking


# Example usage
if __name__ == "__main__":
    # Example sparse rating matrix (users x games)
    rating_matrix = lil_matrix((3, 4), dtype=np.float32)
    rating_matrix[0, 0] = 8
    rating_matrix[0, 1] = 9
    rating_matrix[0, 3] = 7
    rating_matrix[1, 0] = 7
    rating_matrix[1, 2] = 6
    rating_matrix[1, 3] = 8
    rating_matrix[2, 0] = 9
    rating_matrix[2, 1] = 8
    rating_matrix[2, 2] = 7

    rating_matrix = rating_matrix.tocsr()
    pairwise_wins = compute_pairwise_preferences(rating_matrix)
    ranking = schulze_method(pairwise_wins)
    print("Final Schulze Ranking (game indices):", ranking)
