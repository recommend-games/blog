"""Metrics for h- and g-index calculation."""

import polars as pl


def h_and_g_index(
    counts: pl.DataFrame | pl.LazyFrame,
    count_col: str,
    target_col: str,
) -> pl.LazyFrame:
    """Calculate h-index and g-index."""

    return (
        counts.lazy()
        .sort(
            [target_col, count_col],
            descending=[False, True],
        )
        .select(
            pl.col(target_col),
            pl.col(count_col),
            pl.col(count_col).cum_sum().over(target_col).alias("cum_count"),
            pl.col(count_col)
            .rank("ordinal", descending=True)
            .over(target_col)
            .alias("rank"),
        )
        .with_columns(
            pl.when(pl.col("rank") <= pl.col(count_col))
            .then(pl.col("rank"))
            .alias("h_index_rank"),
            pl.when(pl.col("rank") ** 2 <= pl.col("cum_count"))
            .then(pl.col("rank"))
            .alias("g_index_rank"),
        )
        .group_by(target_col)
        .agg(
            pl.col("h_index_rank").max().alias("h_index"),
            pl.col("g_index_rank").max().alias("g_index"),
        )
        .sort(["h_index", "g_index", target_col], descending=[True, True, False])
        .select(
            pl.col("h_index").rank("min", descending=True).alias("rank_h_index"),
            pl.col("h_index"),
            pl.col("g_index").rank("min", descending=True).alias("rank_g_index"),
            pl.col("g_index"),
            pl.col(target_col),
        )
    )
