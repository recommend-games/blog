"""
This module implements the Schulze method for ranking games based on user preferences.
"""

from __future__ import annotations
from collections.abc import Iterable

import polars as pl
import numpy as np
from tqdm import trange


def schulze_method(
    rating_matrix: np.ndarray,
    bgg_user_names: Iterable[str],
    bgg_ids: Iterable[int],
    progress_bar: bool = False,
) -> pl.DataFrame:
    """
    Compute the Schulze ranking from a sparse pairwise wins matrix.

    Args:
        rating_matrix (np.ndarray): A (num_users, num_games) matrix with ratings.

    Returns:
        pl.DataFrame: A DataFrame with game indices and scores.
    """

    bgg_user_names = sorted(bgg_user_names)
    bgg_ids = sorted(bgg_ids)
    assert rating_matrix.shape == (len(bgg_user_names), len(bgg_ids))

    ratings = (
        pl.LazyFrame(data=rating_matrix.T, schema=tuple(bgg_user_names))
        .with_columns(pl.Series("bgg_id", bgg_ids))
        .unpivot(
            index="bgg_id",
            variable_name="bgg_user_name",
            value_name="bgg_user_rating",
        )
    )

    strength_matrix = (
        ratings.join(ratings, on="bgg_user_name", how="inner", suffix="_other")
        .filter(pl.col("bgg_id") != pl.col("bgg_id_other"))
        .filter(pl.col("bgg_user_rating") > pl.col("bgg_user_rating_other"))
        .group_by(["bgg_id", "bgg_id_other"])
        .agg(pl.len().alias("wins"))
        .group_by("bgg_id")
        .agg(
            pl.col("wins")
            .filter(pl.col("bgg_id_other") == bgg_id)
            .first()
            .alias(str(bgg_id))
            for bgg_id in bgg_ids
        )
        .sort("bgg_id")
        .drop("bgg_id")
        .collect(streaming=True)
        .to_numpy(order="c", writable=True)
    )

    num_games = len(bgg_ids)
    range_ = trange(num_games) if progress_bar else range(num_games)
    for i in range_:
        for j in range(num_games):
            if i != j:
                for k in range(num_games):
                    if i != k and j != k:
                        strength_matrix[j, k] = max(
                            strength_matrix[j, k],
                            min(strength_matrix[j, i], strength_matrix[i, k]),
                        )
    scores = (strength_matrix > strength_matrix.T).sum(axis=1)

    return (
        pl.DataFrame(
            data={
                "bgg_id": bgg_ids,
                "score": scores,
            }
        )
        .with_columns(rank=pl.col("score").rank(descending=True, method="min"))
        .sort("rank")
    )
