from datetime import date
import logging
import os
from pathlib import Path
from typing import Iterable
import polars as pl
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)


def process_rankings_counts(
    rankings_dir: os.PathLike,
    *,
    max_games: int | None = None,
    min_date: date | None = None,
    progress_bar: bool = False,
) -> pl.DataFrame:
    """Process the rankings counts from the rankings files."""

    rankings_dir = Path(rankings_dir).resolve()
    LOGGER.info("Processing rankings files from <%s>", rankings_dir)

    all_files = rankings_dir.glob("*.csv")
    if min_date:
        LOGGER.info("Filtering rankings files by min date <%s>", min_date)
        files = [
            file for file in all_files if date.fromisoformat(file.stem[:10]) >= min_date
        ]
    else:
        files = list(all_files)
    LOGGER.info("Found %d rankings files", len(files))

    rankings_dfs: Iterable[pl.LazyFrame] = (
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
    LOGGER.info("Pivoted rankings data has shape %dx%d", *pivoted.shape)

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
    LOGGER.info("Using the %d top games", len(top_games))

    rankings_counts = (
        pivoted.lazy()
        .sort("day")
        .select(
            "day",
            pl.col(*top_games)
            .interpolate()
            .fill_null(strategy="forward")
            .cast(pl.Int64),
        )
        .collect()
    )
    LOGGER.info("Processed rankings data has shape %dx%d", *rankings_counts.shape)

    return rankings_counts


def process_collection_counts(
    ratings_file: os.PathLike,
    *,
    max_games: int | None = None,
    min_date: date | None = None,
) -> pl.DataFrame:
    """Process the collection counts from the ratings file."""

    ratings_file = Path(ratings_file).resolve()
    LOGGER.info("Processing collection data from <%s>", ratings_file)

    schema = {
        "bgg_id": pl.Int64,
        "updated_at": pl.Datetime,
    }

    collection_counts_by_day = (
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
    LOGGER.info("Collection data has shape %dx%d", *collection_counts_by_day.shape)

    pivoted = collection_counts_by_day.pivot(
        values="num_collections",
        index="day",
        columns="bgg_id",
    ).sort("day")
    LOGGER.info("Pivoted collection data has shape %dx%d", *pivoted.shape)

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
    LOGGER.info("Using the %d top games", len(top_games))

    collection_counts = pivoted.lazy().select(
        "day",
        pl.col(*top_games).interpolate().fill_null(strategy="forward").cast(pl.Int64),
    )
    if min_date:
        collection_counts = collection_counts.filter(pl.col("day") >= min_date)
    result = collection_counts.collect()
    LOGGER.info("Processed collection data has shape %dx%d", *result.shape)

    return result


def _main():
    max_games = 50_000
    min_date = date(2021, 1, 1)

    rankings_dir = Path().resolve().parent.parent.parent / "bgg-ranking-historicals"
    rankings_counts = process_rankings_counts(
        rankings_dir=rankings_dir,
        max_games=max_games,
        min_date=min_date,
        progress_bar=True,
    )
    rankings_counts.write_csv("./data/num_ratings.csv")

    ratings_file = (
        Path().resolve().parent.parent.parent
        / "board-game-data"
        / "scraped"
        / "bgg_RatingItem.jl"
    )
    collection_counts = process_collection_counts(
        ratings_file=ratings_file,
        max_games=max_games,
        min_date=min_date,
    )
    collection_counts.write_csv("./data/num_collections.csv")


if __name__ == "__main__":
    _main()
