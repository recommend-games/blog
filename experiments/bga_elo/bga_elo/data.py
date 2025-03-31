from __future__ import annotations
from pathlib import Path

import polars as pl
from board_game_merger.config import MergeConfig
from board_game_merger.merge import merge_files


def load_and_merge_rankings(
    rankings_path: str | Path | list[str] | list[Path],
    output_path: str | Path,
    progress_bar: bool = False,
) -> None:
    schema = {
        "id": pl.Int64,
        "name": pl.String,
        "ranking": pl.Float64,
        "nbr_game": pl.Int64,
        "rank_no": pl.Int64,
        "game_id": pl.Int64,
        "scraped_at": pl.Datetime,
    }

    config = MergeConfig(
        schema=pl.Schema(schema),
        in_paths=rankings_path,
        out_path=output_path,
        key_col=["game_id", "name"],
        latest_col="scraped_at",
    )

    merge_files(
        merge_config=config,
        overwrite=False,
        drop_empty=True,
        sort_keys=True,
        progress_bar=progress_bar,
    )
