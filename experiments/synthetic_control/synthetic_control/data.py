from datetime import date
from pathlib import Path
import polars as pl


def process_collection_counts(
    ratings_file: Path,
    *,
    max_games: int | None = None,
    min_date: date | None = None,
) -> pl.DataFrame:
    """Process the collection counts from the ratings file."""

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
