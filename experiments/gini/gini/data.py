from datetime import datetime
from pathlib import Path
from typing import Generator
import polars as pl


def scan_rankings(
    path: Path,
    *,
    additional_columns: dict[str, str] | None = None,
    date_fmt: str = "%Y-%m-%dT%H-%M-%S",
) -> pl.LazyFrame:
    column_aliases = (
        [pl.col(name).alias(alias) for name, alias in additional_columns.items()]
        if additional_columns
        else []
    )
    pub_date = datetime.strptime(path.stem, date_fmt)
    return (
        pl.scan_csv(path)
        .select(
            pl.col("ID").alias("bgg_id"),
            pl.col("Users rated").alias("num_ratings"),
            *column_aliases,
        )
        .with_columns(pl.lit(pub_date).alias("date"))
    )


def scan_all_rankings(
    rankings_dir: Path,
    glob: str = "*.csv",
    *,
    date_fmt: str = "%Y-%m-%dT%H-%M-%S",
) -> Generator[pl.LazyFrame, None, None]:
    curr_length = 0
    for path in sorted(rankings_dir.glob(glob)):
        df = scan_rankings(path, date_fmt=date_fmt)
        length = df.select(pl.len()).collect().item()
        if length < curr_length * 0.99:
            continue
        curr_length = length
        yield df
