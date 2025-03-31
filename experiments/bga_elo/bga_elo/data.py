from __future__ import annotations
from pathlib import Path

import polars as pl
from board_game_merger.config import MergeConfig
from board_game_merger.merge import merge_files


def merge_rankings(
    rankings_path: str | Path | list[str] | list[Path],
    output_path: str | Path,
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
        overwrite=False,
        drop_empty=True,
        sort_keys=True,
        progress_bar=progress_bar,
    )


if __name__ == "__main__":
    merge_rankings(
        rankings_path="results/rankings-*.jl",
        output_path="rankings.jl",
        progress_bar=True,
    )
