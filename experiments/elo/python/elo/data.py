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
        fieldnames_exclude=["scraped_at"],
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
        fieldnames_exclude=["scraped_at"],
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
    bga_rankings_path: str | Path,
    exclude_bga_slugs: list[str] | None = None,
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
        # "priority": pl.Int64,
        "games_played": pl.Int64,
        "published_on": pl.Datetime,
        "average_duration": pl.Int64,
        "bgg_id": pl.Int64,
        "is_ranking_disabled": pl.Boolean,
    }

    bga_games_data = (
        pl.scan_ndjson(bga_games_path, schema=bga_games_schema)
        .with_columns(pl.col(pl.Boolean).fill_null(False))
        .remove(pl.col("is_ranking_disabled"))
        .remove(pl.col("locked"))
        .filter(pl.col("status") == "public")
        .drop("is_ranking_disabled", "locked", "status")
        .drop_nulls("bgg_id")
        .rename({"id": "bga_id", "name": "bga_slug", "display_name_en": "bga_name"})
        .with_columns(days_online=pl.lit(datetime.now()) - pl.col("published_on"))
        .with_columns(
            games_per_day=pl.col("games_played")
            / pl.col("days_online").dt.total_days(),
        )
    )

    if exclude_bga_slugs:
        bga_games_data = bga_games_data.remove(
            pl.col("bga_slug").is_in(exclude_bga_slugs),
        )

    bga_rankings_schema = {
        "ranking": pl.Float64,
        # "nbr_game": pl.Int64,
        # "rank_no": pl.Int64,
        "game_id": pl.Int64,
    }

    bga_rankings_data = (
        pl.scan_ndjson(bga_rankings_path)
        .select([pl.col(k).cast(v) for k, v in bga_rankings_schema.items()])
        .with_columns(elo=pl.col("ranking") - 1300)
        .drop("ranking")
        .rename({"game_id": "bga_id"})
        .group_by("bga_id")
        .agg(
            num_players=pl.len(),
            elo_mean=pl.col("elo").mean(),
            elo_std=pl.col("elo").std(),
            elo_min=pl.col("elo").min(),
            elo_p01=pl.col("elo").quantile(0.01),
            elo_p05=pl.col("elo").quantile(0.05),
            elo_p25=pl.col("elo").quantile(0.25),
            elo_p50=pl.col("elo").quantile(0.50),
            elo_p75=pl.col("elo").quantile(0.75),
            elo_p95=pl.col("elo").quantile(0.95),
            elo_p99=pl.col("elo").quantile(0.99),
            elo_max=pl.col("elo").max(),
        )
        .with_columns(
            elo_iqr=pl.col("elo_p75") - pl.col("elo_p25"),
        )
    )

    return (
        bgg_games_data.join(bga_games_data, on="bgg_id", how="inner")
        .join(bga_rankings_data, on="bga_id", how="left")
        .with_columns(games_per_player=pl.col("games_played") / pl.col("num_players"))
        .sort("num_players", "games_played", "bayes_rating", descending=True)
        .collect()
    )


def main() -> None:
    input_dir = Path("results").resolve()
    output_dir = Path("csv").resolve()
    merge_games(
        games_path=input_dir / "games-*.jl",
        output_path=output_dir / "games.jl",
        overwrite=True,
        progress_bar=True,
    )
    merge_rankings(
        rankings_path=input_dir / "rankings-*.jl",
        output_path=output_dir / "rankings.jl",
        overwrite=True,
        progress_bar=True,
    )


if __name__ == "__main__":
    main()
