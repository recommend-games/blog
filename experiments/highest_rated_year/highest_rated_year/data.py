from datetime import date
import logging
from pathlib import Path
import polars as pl

LOGGER = logging.getLogger(__name__)


def load_years_from_rankings(rankings_dir: str | Path) -> pl.DataFrame:
    rankings_dir = Path(rankings_dir).resolve()
    file_path = max(rankings_dir.glob("*.csv"))
    LOGGER.info("Loading data from <%s>", file_path)

    this_year = date.today().year

    return (
        pl.scan_csv(file_path)
        .select(
            bgg_id="ID",
            name="Name",
            year="Year",
            avg_rating="Average",
            bayes_rating="Bayes average",
            num_ratings="Users rated",
        )
        .filter(pl.col("year") >= 1900)
        .filter(pl.col("year") < this_year)
        .group_by("year")
        .agg(
            num_games=pl.len(),
            avg_rating=pl.mean("avg_rating"),
            bayes_rating=pl.mean("bayes_rating"),
        )
        .with_columns(rel_num_games=pl.col("num_games") / pl.max("num_games"))
        .sort("year")
        .collect()
    )


def load_years_from_ratings(data_dir: str | Path) -> pl.DataFrame:
    data_dir = Path(data_dir).resolve()
    LOGGER.info("Loading data from <%s>", data_dir)
    this_year = date.today().year

    games = (
        pl.scan_ndjson(data_dir / "scraped" / "bgg_GameItem.jl")
        .select("bgg_id", "name", "year")
        .filter(pl.col("year") >= 1900)
        .filter(pl.col("year") < this_year)
    )

    ratings = (
        pl.scan_ndjson(data_dir / "scraped" / "bgg_RatingItem.jl")
        .select("bgg_id", "bgg_user_rating")
        .drop_nulls()
    )

    return (
        games.join(ratings, on="bgg_id", how="inner")
        .select("year", "bgg_user_rating")
        .group_by("year")
        .agg(
            num_ratings=pl.len(),
            avg_rating=pl.mean("bgg_user_rating"),
        )
        .with_columns(rel_num_ratings=pl.col("num_ratings") / pl.max("num_ratings"))
        .sort("year")
        .collect()
    )
