import logging
from pathlib import Path
import numpy as np
import polars as pl
from sklearn.preprocessing import MultiLabelBinarizer

LOGGER = logging.getLogger(__name__)


def load_data(
    path: str | Path,
    *,
    min_year: int | None = None,
    max_year: int | None = None,
    max_min_time: int | None = None,
) -> pl.DataFrame:
    path = Path(path).resolve()
    LOGGER.info("Loading data from <%s>", path)

    games = (
        pl.scan_ndjson(path)
        .filter(pl.col("complexity").is_not_null())
        .filter(pl.col("rank").is_not_null())
        .filter(pl.col("bgg_id") != 91313)  # Video game
    )

    if min_year:
        games = games.filter(pl.col("year") >= min_year)
    if max_year:
        games = games.filter(pl.col("year") <= max_year)
    if max_min_time:
        games = games.filter(pl.col("min_time") <= max_min_time)

    games = games.select(
        "bgg_id",
        "name",
        "year",
        "rank",
        "num_votes",
        "avg_rating",
        "bayes_rating",
        "complexity",
        "min_time",
        pl.col("cooperative").fill_null(False).cast(pl.Int8),
        pl.col("game_type").fill_null([]),
    )

    if max_year:
        games = games.with_columns(age=max_year - pl.col("year"))

    games = games.collect()

    mlb = MultiLabelBinarizer()
    game_types_transformed = mlb.fit_transform(games["game_type"])
    game_types = pl.DataFrame(
        data=game_types_transformed.astype(np.int8),
        schema=list(mlb.classes_),
    )

    return pl.concat([games, game_types], how="horizontal")
