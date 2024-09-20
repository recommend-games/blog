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
        pl.col("game_type").fill_null([]).list.eval(pl.element().str.head(-5)),
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


def markdown_table(data):
    header = ["Rank", "Game", "Rating"]
    align = [":--:", ":---", ":----:"]
    rows = [header, align]

    for game in data.select(
        "bgg_id",
        "name",
        "year",
        "rank_debiased",
        "rank_change",
        "avg_rating_debiased",
        "avg_rating_change",
    ).iter_rows(named=True):
        rank_change = game["rank_change"]
        rank_change_emoji = (
            "🔺" if rank_change > 0 else "🔻" if rank_change < 0 else "🔸"
        )

        rating_change = game["avg_rating_change"]
        rating_change_emoji = (
            "🔸" if abs(rating_change) < 0.05 else "🔺" if rating_change > 0 else "🔻"
        )

        rows += [
            [
                f"**#{game["rank_debiased"]}** <small>({rank_change_emoji} {abs(rank_change)})</small>",
                f"{{{{% game {game["bgg_id"]} %}}}}{game["name"]}{{{{% /game %}}}} <small>({game["year"]})</small>",
                f"{game["avg_rating_debiased"]:.1f} <small>({rating_change_emoji} {abs(rating_change):.1f})</small>",
            ]
        ]

    return "\n".join("|".join([""] + row + [""]) for row in rows)
