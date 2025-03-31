from __future__ import annotations
from datetime import datetime
from pathlib import Path

import polars as pl
from board_game_merger.config import MergeConfig
from board_game_merger.merge import merge_files


def merge_games(
    games_path: str | Path | list[str] | list[Path],
    output_path: str | Path,
    overwrite: bool = False,
    progress_bar: bool = False,
) -> None:
    schema = {
        "id": pl.Int64,
        "name": pl.String,
        "display_name_en": pl.String,
        "status": pl.String,
        "premium": pl.Boolean,
        "locked": pl.Boolean,
        "weight": pl.Int64,
        "priority": pl.Int64,
        "games_played": pl.Int64,
        "published_on": pl.String,
        "average_duration": pl.Int64,
        "bgg_id": pl.Int64,
        "is_ranking_disabled": pl.Boolean,
        "scraped_at": pl.String,
    }

    config = MergeConfig(
        schema=pl.Schema(schema),
        in_paths=games_path,
        out_path=output_path,
        key_col="id",
        latest_col=pl.col("scraped_at").str.to_datetime(time_zone="UTC"),
        sort_fields="id",
    )

    merge_files(
        merge_config=config,
        overwrite=overwrite,
        drop_empty=True,
        sort_keys=True,
        progress_bar=progress_bar,
    )


def merge_rankings(
    rankings_path: str | Path | list[str] | list[Path],
    output_path: str | Path,
    overwrite: bool = False,
    progress_bar: bool = False,
) -> None:
    schema = {
        "name": pl.String,
        "ranking": pl.String,
        "nbr_game": pl.String,
        "rank_no": pl.String,
        "game_id": pl.Int64,
        "scraped_at": pl.String,
    }

    config = MergeConfig(
        schema=pl.Schema(schema),
        in_paths=rankings_path,
        out_path=output_path,
        key_col=["game_id", "name"],
        latest_col=pl.col("scraped_at").str.to_datetime(time_zone="UTC"),
        sort_fields=[
            "game_id",
            -pl.col("ranking").cast(pl.Float64),
            pl.col("rank_no").cast(pl.Float64),
            "name",
        ],
    )

    merge_files(
        merge_config=config,
        overwrite=overwrite,
        drop_empty=True,
        sort_keys=True,
        progress_bar=progress_bar,
    )


def load_data(
    *,
    bgg_games_path: str | Path,
    bga_games_path: str | Path,
) -> pl.DataFrame:
    bgg_games_data = pl.scan_ndjson(bgg_games_path).select(
        "bgg_id",
        "name",
        "year",
        "complexity",
        "avg_rating",
        "bayes_rating",
    )

    bga_games_schema = {
        "id": pl.Int64,
        "name": pl.String,
        "display_name_en": pl.String,
        "status": pl.String,
        "premium": pl.Boolean,
        "locked": pl.Boolean,
        "weight": pl.Int64,
        "priority": pl.Int64,
        "games_played": pl.Int64,
        "published_on": pl.Datetime,
        "average_duration": pl.Int64,
        "bgg_id": pl.Int64,
        "is_ranking_disabled": pl.Boolean,
    }

    bga_games_data = (
        pl.scan_ndjson(bga_games_path, schema=bga_games_schema)
        .drop_nulls("bgg_id")
        .with_columns(days_online=pl.lit(datetime.now()) - pl.col("published_on"))
        .with_columns(
            games_per_day=pl.col("games_played")
            / pl.col("days_online").dt.total_days(),
        )
    )

    return bgg_games_data.join(bga_games_data, on="bgg_id", how="inner").collect()


if __name__ == "__main__":
    merge_games(
        games_path="results/games-*.jl",
        output_path="games.jl",
        overwrite=True,
        progress_bar=True,
    )
    merge_rankings(
        rankings_path="results/rankings-*.jl",
        output_path="rankings.jl",
        overwrite=True,
        progress_bar=True,
    )
