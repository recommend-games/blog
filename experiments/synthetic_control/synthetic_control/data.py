from datetime import date
import os
from pathlib import Path
import polars as pl
from tqdm import tqdm


def process_rankings_counts(
    rankings_dir: os.PathLike,
    progress_bar: bool = False,
) -> pl.DataFrame:
    """Process the rankings counts from the rankings files."""

    rankings_dir = Path(rankings_dir).resolve()

    files = list(rankings_dir.glob("*.csv"))
    rankings_dfs = (
        pl.scan_csv(file).select(
            pl.col("ID").alias("bgg_id"),
            pl.col("Users rated").alias("num_ratings"),
            pl.lit(file.stem[:10]).alias("day"),
        )
        for file in files
    )

    if progress_bar:
        rankings_dfs = tqdm(rankings_dfs, total=len(files))

    pivoted = (
        pl.concat(rankings_dfs)
        .collect()
        .pivot(
            values="num_ratings",
            index="day",
            columns="bgg_id",
            aggregate_function="max",
        )
    )

    game_columns = sorted(pivoted.select(pl.exclude("day")).columns, key=int)

    rankings_counts = (
        pivoted.lazy()
        .sort("day")
        .select(
            "day",
            pl.col(*game_columns)
            .interpolate()
            .fill_null(strategy="forward")
            .cast(pl.Int64),
        )
        .collect()
    )

    return rankings_counts


def process_collection_counts(
    ratings_file: os.PathLike,
    *,
    max_games: int | None = None,
    min_date: date | None = None,
) -> pl.DataFrame:
    """Process the collection counts from the ratings file."""

    ratings_file = Path(ratings_file).resolve()

    schema = {
        "bgg_id": pl.Int64,
        "updated_at": pl.Datetime,
    }

    collection_counts = (
        pl.scan_ndjson(ratings_file, schema=schema)
        .drop_nulls()
        .sort("bgg_id", "updated_at")
        .group_by_dynamic("updated_at", every="1d", by="bgg_id", check_sorted=False)
        .agg(pl.len().alias("num_collections"))
        .with_columns(
            pl.col("updated_at").dt.date().alias("day"),
            pl.col("num_collections").cum_sum().over("bgg_id"),
        )
        .collect()
    )

    pivoted = collection_counts.pivot(
        values="num_collections",
        index="day",
        columns="bgg_id",
    ).sort("day")

    top_games = (
        pivoted.select(pl.exclude("day").max())
        .transpose(
            include_header=True,
            header_name="bgg_id",
            column_names=("max_count",),
        )
        .cast(pl.Int32)
        .sort("max_count", descending=True)["bgg_id"]
    )
    if max_games:
        top_games = top_games[:max_games]
    top_games = top_games.sort().cast(pl.String)

    collection_counts = pivoted.lazy().select(
        "day",
        pl.col(*top_games).interpolate().fill_null(strategy="forward").cast(pl.Int64),
    )
    if min_date:
        collection_counts = collection_counts.filter(pl.col("day") >= min_date)
    collection_counts = collection_counts.collect()

    return collection_counts
