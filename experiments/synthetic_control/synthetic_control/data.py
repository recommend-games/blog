from datetime import date
import logging
import os
from pathlib import Path
import sys
from typing import Iterable
import polars as pl
from tqdm import tqdm
import argparse

LOGGER = logging.getLogger(__name__)
PROJECT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_DIR.parent.parent


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


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Process rankings and collection counts",
    )
    parser.add_argument(
        "--rankings-dir",
        type=Path,
        default=BASE_DIR.parent / "bgg-ranking-historicals",
        help="Directory containing the rankings files",
    )
    parser.add_argument(
        "--ratings-file",
        type=Path,
        default=BASE_DIR.parent / "board-game-data" / "scraped" / "bgg_RatingItem.jl",
        help="File containing the ratings data",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_DIR / "data",
        help="Directory to save the results to",
    )
    parser.add_argument(
        "--max-games",
        type=int,
        help="Maximum number of games to process",
    )
    parser.add_argument(
        "--min-date",
        type=date.fromisoformat,
        help="Minimum date to process",
    )
    parser.add_argument(
        "--progress-bar",
        action="store_true",
        help="Show a progress bar",
    )
    parser.add_argument(
        "--verbose",
        action="count",
        default=0,
        help="Verbosity level (repeat for more verbosity)",
    )
    return parser.parse_args()


def _main():
    args = _parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 0 else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    LOGGER.info(args)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Saving results to <%s>", output_dir)

    rankings_dir = Path(args.rankings_dir).resolve()
    if rankings_dir.is_dir():
        rankings_counts = process_rankings_counts(
            rankings_dir=rankings_dir,
            max_games=args.max_games,
            min_date=args.min_date,
            progress_bar=args.progress_bar,
        )
        rankings_file = output_dir / "num_ratings.csv"
        LOGGER.info("Saving rankings counts to <%s>", rankings_file)
        rankings_counts.write_csv(rankings_file)

    ratings_file = Path(args.ratings_file).resolve()
    if ratings_file.is_file():
        collection_counts = process_collection_counts(
            ratings_file=ratings_file,
            max_games=args.max_games,
            min_date=args.min_date,
        )
        collection_file = output_dir / "num_collections.csv"
        LOGGER.info("Saving collection counts to <%s>", collection_file)
        collection_counts.write_csv(collection_file)

    LOGGER.info("Done.")


if __name__ == "__main__":
    _main()
